#!/usr/bin/env python3
"""Copy replacement textures from edit/ into the mod folder.

Reads nothing but edit/ (author artwork) and ref/ (upstream mods, read-only,
used only to look up the expected pixel dimensions). Never writes outside the
mod folder.

Images whose dimensions differ from the upstream original are downscaled with
LANCZOS so the mod ships textures at the same resolution the target mods use.

Usage:  python tools/build_textures.py [--dry-run]
"""

import os
import shutil
import sys

from PIL import Image

MOD_DIR = "Yuran_Fur_Shaved_For_RJW"

# edit/ prefix  ->  destination folder inside the mod.
# The prefix strips each upstream mod's LoadFolders virtual root so that only
# the in-game texture path (everything after "Textures/") is reproduced.
ROUTES = [
    (
        "Hawk_Anims-master/Common/Textures/",
        "Mods/HawkAnims/Textures/",
    ),
    (
        "Multiple-Races-SA0-Patch-main/Commons/Yuran/Textures/",
        "Mods/MultipleRacesSA0/Textures/",
    ),
    (
        "rjw-animations-adjusts-har-race-offset-master/1.6/Legs_Textures/Yuran_Legs/Textures/",
        "Mods/HarRaceOffset/Textures/",
    ),
]

# Upstream ships these two as 32x32 fully transparent placeholders. Matching
# that size would destroy the artwork, so they follow the size used by the
# other north-facing files in the same folder.
SIZE_OVERRIDES = {
    "Multiple-Races-SA0-Patch-main/Commons/Yuran/Textures/SizedApparel/BodyParts/"
    "Yuran_Race_Miko_BlackSnake/Belly/BellyBulge_Thin_1_north.png": (256, 256),
    "Multiple-Races-SA0-Patch-main/Commons/Yuran/Textures/SizedApparel/BodyParts/"
    "Yuran_Race_Miko_BlackSnake/Belly/BellyBulge_Thin_2_north.png": (256, 256),
}


def route(rel):
    """Map an edit/-relative path to its path inside the mod, or None."""
    for prefix, dest in ROUTES:
        if rel.startswith(prefix):
            return dest + rel[len(prefix):]
    return None


def main():
    dry_run = "--dry-run" in sys.argv

    if not os.path.isdir("edit") or not os.path.isdir("ref"):
        sys.exit("error: run this from the repository root (edit/ and ref/ must exist)")

    copied = resized = skipped = 0

    for root, _, files in os.walk("edit"):
        for name in sorted(files):
            src = os.path.join(root, name).replace(os.sep, "/")
            rel = src[len("edit/"):]

            if not name.lower().endswith(".png"):
                print("SKIP   %s (not a png)" % rel)
                skipped += 1
                continue

            dst_rel = route(rel)
            if dst_rel is None:
                print("SKIP   %s (no route)" % rel)
                skipped += 1
                continue

            ref = "ref/" + rel
            if not os.path.isfile(ref):
                print("SKIP   %s (no upstream counterpart)" % rel)
                skipped += 1
                continue

            dst = os.path.join(MOD_DIR, dst_rel).replace(os.sep, "/")
            want = SIZE_OVERRIDES.get(rel) or Image.open(ref).size
            have = Image.open(src).size

            if not dry_run:
                os.makedirs(os.path.dirname(dst), exist_ok=True)

            if have == want:
                if not dry_run:
                    shutil.copy2(src, dst)
                copied += 1
            else:
                print("RESIZE %s  %dx%d -> %dx%d" % ((rel,) + have + want))
                if not dry_run:
                    with Image.open(src) as im:
                        im.convert("RGBA").resize(want, Image.LANCZOS).save(dst, "PNG")
                resized += 1

    print("\ncopied=%d resized=%d skipped=%d%s" % (
        copied, resized, skipped, " (dry run)" if dry_run else ""))


if __name__ == "__main__":
    main()
