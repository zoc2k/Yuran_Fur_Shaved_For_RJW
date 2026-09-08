# Yuran Fur Shaved For RJW

A texture replacement patch for the **Yuran** race (HAR) in RJW addon mods. It
swaps the fur on Yuran body and genital textures for a shaved variant.

This mod adds **no gameplay content**: no Defs, no patches, no C# assembly.
It contains textures and two XML metadata files, nothing else.

##
If you're using the **Yuran race's facial animations**, we recommend subscribing to “Yuran Furshaved Continue” on the Steam Workshop.
https://steamcommunity.com/sharedfiles/filedetails/?id=3569887039

This mod does not include textures for facial animations.

## Supported addon mods

Every target below is **optional**. Folders are gated with `LoadFolders.xml`,
so a mod you do not have installed simply contributes nothing, and no error or
warning is produced. Installing none of them is also safe.

| Target mod | packageId | RimWorld | Replaced textures |
| --- | --- | --- | --- |
| Rimworld Hawkeye32's RJW Animations | `Hawkeye32.Hawks.Anims` | 1.5, 1.6 | 12 |
| Multiple Races SA0 Patch | `adk.sar.alien` | 1.5, 1.6 | 144 |
| RJW Animations adjusts HAR race offset | `Talos.RJW.Animations.adjusts.HAR.race.offset` | 1.6 only | 14 |

The `Multiple Races SA0 Patch` folder additionally requires the Yuran race mod
(`RooAndGloomy.YuranRaceMod`) to be active, and the `RJW Animations adjusts HAR
race offset` folder additionally requires Sized Apparel
(`OTYOTY.SizedApparel`) — matching the conditions those mods use for their own
Yuran folders.

`RJW Animations adjusts HAR race offset` ships its Yuran leg textures under a
1.6-only folder, so that part of this patch applies on RimWorld 1.6 only.

## Load order

Place this mod **below** all of the following that you have installed:

1. Harmony
2. Humanoid Alien Races
3. RimJobWorld
4. Yuran race mod
5. Sized Apparel (and Sized Apparel Extended)
6. RimWorld Animations / Hawkeye32's RJW Animations
7. Multiple Races SA0 Patch
8. RJW Animations adjusts HAR race offset

Because this mod only overrides textures, a wrong load order does not break
anything — the replacements are simply not applied.

## Installation

### GitHub release zip

1. Download the zip from the
   [Releases](https://github.com/zoc2k/Yuran_Fur_Shaved_For_RJW/releases) page.
2. Extract it into your RimWorld `Mods` folder. The result must be
   `Mods/Yuran_Fur_Shaved_For_RJW/About/About.xml`.
3. Enable the mod in the in-game mod list and put it last, as described above.

### Manual

Copy the `Yuran_Fur_Shaved_For_RJW` folder from this repository into your
RimWorld `Mods` folder.

## Credits

- **Hawkeye32** — Rimworld Hawkeye32's RJW Animations
- **AlexDuKaNa, Ryufais** — Multiple Races SA0 Patch
- **Talos** — RJW Animations adjusts HAR race offset

- THX to all mod creater!

This repository contains **only
original replacement artwork**. No other texture, Def, or asset from the mods
listed above is redistributed here. You must own and install those mods
yourself for this patch to do anything.

## Licence

Copyright (C) 2026 zoc2k. Licensed under the **GNU General Public License,
version 3 or later** (`GPL-3.0-or-later`). See [LICENSE](LICENSE) for the full
text and [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) for the third-party
exception described above.

## Disclaimer

Unofficial. Not affiliated with, endorsed by, or supported by the authors of
the target mods, RimJobWorld, Humanoid Alien Races, or Ludeon Studios.
