#!/usr/bin/env python3
"""Check local Markdown links, heading anchors, and reachability from README.

Uses the repository's inline-link and ATX-heading conventions; does not fetch
external URLs or interpret code examples as links.
"""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'(?<!!)\[[^\]\n]+\]\(([^\s)]+)\)')


def prose(text):
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r'^\s*(`{3,}|~{3,})', line)
        if match:
            token = match[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            lines.append('')
        else:
            lines.append(line if fence is None else '')
    return '\n'.join(lines)


def anchors(text):
    result, counts = set(), {}
    for line in prose(text).splitlines():
        match = re.match(r'^#{1,6}\s+(.+?)(?:\s+#+)?$', line)
        if not match:
            continue
        heading = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', match[1])
        slug = re.sub(r'[^\w\-\s]', '', heading.lower()).replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(f'{slug}-{count}' if count else slug)
    return result


def main():
    docs = {p.resolve(): p.read_text() for p in ROOT.rglob('*.md') if '.git' not in p.parts}
    graph = {p: set() for p in docs}
    heading_ids = {p: anchors(text) for p, text in docs.items()}
    errors, links = [], 0
    for path, text in docs.items():
        for match in LINK.finditer(prose(text)):
            target = urlsplit(match[1].strip('<>'))
            if target.scheme or target.netloc:
                continue
            links += 1
            dest = (path.parent / unquote(target.path)).resolve() if target.path else path
            line = text[:match.start()].count('\n') + 1
            label = f'{path.relative_to(ROOT)}:{line}'
            if not dest.exists():
                errors.append(f'{label}: missing {match[1]}')
            elif target.fragment and dest in heading_ids and unquote(target.fragment) not in heading_ids[dest]:
                errors.append(f'{label}: unknown anchor {match[1]}')
            if dest in docs:
                graph[path].add(dest)
    seen, pending = set(), [ROOT / 'README.md']
    while pending:
        path = pending.pop()
        if path in seen:
            continue
        seen.add(path)
        pending.extend(graph.get(path, set()) - seen)
    for path in sorted(set(docs) - seen):
        errors.append(f'{path.relative_to(ROOT)}: unreachable from README.md')
    if errors:
        print('\n'.join(errors))
        return 1
    print(f'OK: {len(docs)} Markdown files, {links} local links, all reachable from README.md')
    return 0


if __name__ == '__main__':
    sys.exit(main())
