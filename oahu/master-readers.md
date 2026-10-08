# RPG3 (oahu) のマスターの表の読み手

対象: 日本版 RPG3 (oahu)、Update TitleVersion 4096 の code.bin。アドレスは実行時仮想アドレス。以下の「確定」は既存のコード解析・実データ照合による記録、「推定」「未確認」はそのまま区別する。Base / Update の資源の選択は [更新データ](../roms/oahu-update.md) を参照。

RPG3 のコードは master の表を名前ではなく、マスター (`*0x59F200`) の中の**読み手** (0x1C バイト: +0x04 表の先頭、+0x0C 行、+0x10 行のポインタ、+0x14 状態) で引く。エントリのハッシュ → 読み手のオフセットは `FUN_001D9BBC` (ハッシュの二分探索の分岐) で決まる。これを実行して得た対応 (92 個中 82 個。残りの flagData 系・vendor・innSetting・W01_ground・denpaHash はここでは割り当てない):

| オフセット | 表 | オフセット | 表 | オフセット | 表 |
|---|---|---|---|---|---|
| +0x000 | floorData | +0x310 | treasureGroup | +0x690 | denpaByeEvent |
| +0x01C | animData | +0x32C | mapChara | +0x6AC | denpaRecoverEvent |
| +0x0E0 | actionData | +0x348 | mapCamera | +0x700 | common_SaveDenpaHome |
| +0x0FC | antennaGroup | +0x364 | **mapData** | +0x738 | mapNavi |
| +0x118 | itemData | +0x380 | mapResource | +0x754 | cecLampIgnore |
| +0x134 | levelData | +0x39C | mapExtraRoom | +0x770 | houseRoofColor |
| +0x150 | bodyData | +0x3B8 | mapEffect | +0x78C | npcCollisionSize |
| +0x16C | bodyColorData | +0x3D4 | mapObject | +0x7A8 | mapExit |
| +0x188 | headData | +0x3F0 | mapSaveRestart | +0x7C4 | battleParameter |
| +0x1A4 | headDataRare | +0x40C | scriptCharacterPopupPos | +0x834〜+0x9F4 | createRarityLot・createSelect* (16 個) |
| +0x1C0 | conditionData | +0x498 | mapParts | +0xA2C | monsterEffect |
| +0x1DC | denpaPersonality | +0x4D0 | designedMap | +0xA48 | monsterParameter |
| +0x1F8 | initLevelData | +0x4EC〜+0x524 | plantInfo / plantMap / plantPoint | +0xA64 | **monsterGroup** |
| +0x214 | **soundData** | +0x540〜+0x5B0 | fishData / fishingHook / fishingPoint / fishingRod / fishingLevel | +0xA80 | reBossInfo |
| +0x230 | stereoCamera | +0x5CC | previewParameter | +0xA9C〜+0xAD4 | nagomiHouseList / nagomiCatchList / nagomiTownList |
| +0x24C | font | +0x5E8 | insideInterior | | |
| +0x268 | areaInfoData | +0x604 / +0x620 | worldmapParts / worldmapPort | | |
| +0x284 | denpaCustom | +0x63C / +0x658 / +0x674 | mapAppearPos / mapAppearWorldmap / mapJumpPoint | | |
| +0x2A0 / +0x2BC | actionCamera / statusCommunity | | | | |
| +0x2D8 | **mapGroup** | | | | |
| +0x2F4 | dungeonEnv | | | | |

- 表の読み手の使い方は RPG2 と同じ (`FUN_0022C084(読み手, 行)` で行のポインタ)。ある表を読む関数を探すときは、`*0x59F200 + オフセット` を探すとよい。
