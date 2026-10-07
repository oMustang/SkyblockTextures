# SkyblockTextures

Official Hypixel SkyBlock resource-pack assets supplied in `SkyblockPack.zip`, preserved with their original `LICENSE` and directory layout.

## Contents

- `assets/`: item textures, item/model definitions, GUI and SkyBlock symbol sheets, shaders, and sounds.
- `pack.mcmeta` and `pack.png`: resource-pack metadata and icon.
- `web/item-icons.json`: item-model-to-texture index, including layered and animated texture metadata.
- `web/glyphs.json`: SkyBlock symbol codepoints and their sprite-sheet coordinates.
- `web/pack-info.json`: import checksum and asset counts.

## Using the assets in Hex Online

Copy the required assets into the website's static build directory and pin the source commit for consistent builds. This public repository also supports GitHub raw asset URLs; pin a commit rather than loading a moving branch.

Resolve an item's `item_model` from Hypixel's item resource through `web/item-icons.json` → `byItemModel`. `byItemIdCandidate` provides filename-based convenience keys; match against game metadata before treating a candidate as an exact item ID. Models requiring additional rendering stay marked instead of receiving a fabricated icon.

Textures with multiple `layers` need compositing. Animated textures include their `.mcmeta` metadata and must display the selected frame rather than a whole vertical strip. Use `image-rendering: pixelated` for icon display.

The pack's font definition adds Hypixel-specific symbols to Minecraft's font. It includes the original symbol sheets, but does **not** include Minecraft's base letter font or enchanting alphabet. Use `web/glyphs.json` to render the supplied symbols accurately.

Regenerate indexes with `python3 scripts/build_web_indexes.py`.

## Attribution

The resource pack and its assets are owned by Hypixel Inc. See `LICENSE` for the included terms, including the exception for free Hypixel-related websites/apps. This repository and Hex Online do not claim ownership of the artwork or endorsement by Hypixel.
