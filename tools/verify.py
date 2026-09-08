#!/usr/bin/env python3
"""Verify the built mod folder against the upstream mods in ref/.

Standard library plus Pillow. No network access.

Checks
  1. Every texture in the mod maps to an existing upstream file, case exact.
  2. Replacement resolution versus the upstream original.
  3. Directional (_north/_south/_east) and mask (_m) sets that upstream has
     but the mod does not replace.
  4. About.xml and LoadFolders.xml are well formed.
  5. packageIds used in LoadFolders.xml match the upstream About.xml values.
  6. No Hangul anywhere in the published text files.
  7. No upstream asset was copied into the mod folder.

Usage:  python tools/verify.py
Exit code 1 if any FAIL was reported.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image

MOD_DIR = "Yuran_Fur_Shaved_For_RJW"
REF_DIR = "ref"
EDIT_DIR = "edit"

# Mod-relative folder -> the edit/ and ref/ prefix it was built from.
# The prefix strips each upstream mod's LoadFolders virtual root, so only the
# in-game texture path (everything after "Textures/") is reproduced.
ROUTES = [
    ("Mods/HawkAnims/Textures/",
     "Hawk_Anims-master/Common/Textures/"),
    ("Mods/MultipleRacesSA0/Textures/",
     "Multiple-Races-SA0-Patch-main/Commons/Yuran/Textures/"),
    ("Mods/HarRaceOffset/Textures/",
     "rjw-animations-adjusts-har-race-offset-master/1.6/Legs_Textures/Yuran_Legs/Textures/"),
]

# Upstream files this project is allowed to ship verbatim. Each entry needs a
# recorded permission from its author, documented in THIRD-PARTY-NOTICES.md.
# They are still reported on every run, as WARN rather than FAIL.
PERMITTED_UPSTREAM = {
    "Mods/HarRaceOffset/Textures/Yuran/Yuranlike/Bodies/BlackSnake/RJW_VLegs/Naked_Thin_eastm.png",
    "Mods/HarRaceOffset/Textures/Yuran/Yuranlike/Bodies/BlackSnake/RJW_VLegs/Naked_Thin_northm.png",
    "Mods/HarRaceOffset/Textures/Yuran/Yuranlike/Bodies/BlackSnake/RJW_VLegs/Naked_Thin_southm.png",
}
NOTICES = "THIRD-PARTY-NOTICES.md"

# Upstream folder name -> the mod folder its packageId must gate.
UPSTREAM = {
    "Hawk_Anims-master": "Mods/HawkAnims",
    "Multiple-Races-SA0-Patch-main": "Mods/MultipleRacesSA0",
    "rjw-animations-adjusts-har-race-offset-master": "Mods/HarRaceOffset",
}

# Hangul syllables U+AC00..U+D7A3 plus compatibility jamo U+3131..U+318E.
# Built from code points so this file itself stays pure ASCII and passes check 6.
HANGUL = re.compile("[%c-%c%c-%c]" % (0xAC00, 0xD7A3, 0x3131, 0x318E))
TEXT_EXT = {".xml", ".cs", ".md", ".txt", ".yml", ".yaml", ".json", ".py"}
# Files with no extension, or whose whole name is the extension.
TEXT_NAMES = {"LICENSE", ".gitignore", ".gitattributes"}
DIRECTIONS = ("_north", "_south", "_east", "_west")

fails = []
warns = []


def fail(check, msg):
    fails.append((check, msg))
    print("FAIL  [%s] %s" % (check, msg))


def warn(check, msg):
    warns.append((check, msg))
    print("WARN  [%s] %s" % (check, msg))


def ok(check, msg):
    print("OK    [%s] %s" % (check, msg))


def walk(root):
    """Yield paths under root, relative to root, with forward slashes."""
    for base, _, files in os.walk(root):
        for name in sorted(files):
            full = os.path.join(base, name).replace(os.sep, "/")
            yield full[len(root) + 1:]


def exists_exact(path):
    """True only if every path segment matches on disk with exact case.

    os.path.isfile is case insensitive on Windows, which would hide the very
    mistake that breaks the mod for Linux and Proton players.
    """
    parts = path.split("/")
    cur = parts[0]
    if not os.path.isdir(cur):
        return False
    for seg in parts[1:]:
        try:
            entries = os.listdir(cur)
        except OSError:
            return False
        if seg not in entries:
            return False
        cur = cur + "/" + seg
    return os.path.isfile(cur)


def source_of(mod_rel):
    """Map a mod-relative texture path to its edit/ and ref/ relative path."""
    for dest, prefix in ROUTES:
        if mod_rel.startswith(dest):
            return prefix + mod_rel[len(dest):]
    return None


def read(path):
    with open(path, "rb") as fh:
        return fh.read()


def check_textures():
    """Checks 1, 2 and 7."""
    textures = [p for p in walk(MOD_DIR)
                if p.lower().endswith(".png") and not p.startswith("About/")]
    if not textures:
        fail("1", "no textures found under %s" % MOD_DIR)
        return []

    mapped = 0
    size_diff = 0
    in_place = []
    for rel in textures:
        src_rel = source_of(rel)
        if src_rel is None:
            fail("1", "%s is not under any known Mods/<target>/Textures/ route" % rel)
            continue

        ref_path = REF_DIR + "/" + src_rel
        if not exists_exact(ref_path):
            fail("1", "no upstream counterpart (case sensitive): %s -> %s"
                 % (rel, ref_path))
            continue
        mapped += 1

        mod_path = MOD_DIR + "/" + rel
        edit_path = EDIT_DIR + "/" + src_rel

        # check 2 - resolution against the upstream original
        with Image.open(mod_path) as a, Image.open(ref_path) as b:
            got, want = a.size, b.size
        if got != want:
            warn("2", "%s is %dx%d, upstream is %dx%d" % ((rel,) + got + want))
            size_diff += 1

        # check 7 - a shipped file must never be a byte copy of the upstream
        # original. Files authored straight into the mod folder are allowed,
        # they just cannot be rebuilt by tools/build_textures.py.
        blob = read(mod_path)
        if os.path.isfile(edit_path) and blob == read(edit_path):
            continue
        if blob == read(ref_path):
            if rel in PERMITTED_UPSTREAM:
                warn("7", "verbatim upstream asset, shipped by permission "
                          "(see %s): %s" % (NOTICES, rel))
            else:
                fail("7", "upstream asset copied into the mod: %s" % rel)
        elif not os.path.isfile(edit_path):
            in_place.append(rel)

    if not [f for f in fails if f[0] == "1"]:
        ok("1", "%d textures map to an existing upstream path, case exact" % mapped)
    if size_diff == 0:
        ok("2", "all %d replacement resolutions match upstream" % len(textures))
    else:
        ok("2", "%d of %d textures differ in resolution (see WARN above)"
           % (size_diff, len(textures)))
    if not [f for f in fails if f[0] == "7"]:
        ok("7", "no undeclared upstream asset in the mod folder")

    # Every permitted exception must be real and must be documented, so the
    # allowlist cannot quietly outlive the file or the permission notice.
    notices = ""
    if os.path.isfile(NOTICES):
        with open(NOTICES, encoding="utf-8") as fh:
            notices = fh.read()
    else:
        fail("7", "missing %s, required to justify PERMITTED_UPSTREAM" % NOTICES)
    for rel in sorted(PERMITTED_UPSTREAM):
        if rel not in set(textures):
            fail("7", "PERMITTED_UPSTREAM lists %s but the mod does not ship it" % rel)
        elif notices and os.path.basename(rel) not in notices:
            fail("7", "%s is not documented in %s" % (rel, NOTICES))

    for rel in in_place:
        print("INFO  [7] authored in place, no edit/ source, "
              "not reproducible by build_textures.py: %s" % rel)
    return textures


def check_sets(textures):
    """Check 3."""
    shipped = set(textures)
    seen = set()  # a gap is found once per sibling, not once per direction
    gaps = 0
    for rel in sorted(textures):
        if source_of(rel) is None:
            continue
        stem = rel[:-len(".png")]

        # directional siblings
        for d in DIRECTIONS:
            if not stem.endswith(d):
                continue
            base = stem[:-len(d)]
            for other in DIRECTIONS:
                if other == d:
                    continue
                sib = base + other + ".png"
                if sib in shipped or sib in seen:
                    continue
                seen.add(sib)
                sib_src = source_of(sib)
                if sib_src and exists_exact(REF_DIR + "/" + sib_src):
                    warn("3", "incomplete direction set: upstream has %s, "
                              "mod does not replace it" % sib)
                    gaps += 1
            break

        # colour mask sibling, upstream names it "<stem>m.png"
        mask = stem + "m.png"
        if mask not in shipped:
            mask_src = source_of(mask)
            if mask_src and exists_exact(REF_DIR + "/" + mask_src):
                warn("3", "mask not replaced: upstream has %s, "
                          "mod ships only the base texture" % mask)
                gaps += 1

    if gaps == 0:
        ok("3", "no missing direction or mask variants")
    else:
        ok("3", "%d set gaps reported above" % gaps)


def check_xml():
    """Checks 4 and 5."""
    about_path = MOD_DIR + "/About/About.xml"
    lf_path = MOD_DIR + "/LoadFolders.xml"

    trees = {}
    for path in (about_path, lf_path):
        if not os.path.isfile(path):
            fail("4", "missing %s" % path)
            continue
        try:
            trees[path] = ET.parse(path)
        except ET.ParseError as exc:
            fail("4", "%s is not well formed: %s" % (path, exc))
    if len(trees) == 2:
        ok("4", "About.xml and LoadFolders.xml are well formed")
    else:
        return

    about = trees[about_path].getroot()
    lf = trees[lf_path].getroot()

    # supportedVersions must line up with the version blocks in LoadFolders
    versions = sorted(li.text.strip() for li in about.findall("./supportedVersions/li"))
    blocks = sorted(el.tag[1:] for el in lf if el.tag.startswith("v"))
    if versions != blocks:
        fail("4", "supportedVersions %s does not match LoadFolders blocks %s"
             % (versions, blocks))
    else:
        ok("4", "supportedVersions %s covered by LoadFolders blocks" % versions)

    # check 5 - packageIds used as load conditions
    used = {}
    for block in lf:
        for li in block.findall("li"):
            for attr in ("IfModActive", "IfModActiveAll", "IfModActiveAny"):
                if attr not in li.attrib:
                    continue
                for pid in li.attrib[attr].split(","):
                    used.setdefault(pid.strip(), set()).add((li.text or "").strip())

    expected = {}
    for folder, mod_path in sorted(UPSTREAM.items()):
        ref_about = "%s/%s/About/About.xml" % (REF_DIR, folder)
        if not os.path.isfile(ref_about):
            fail("5", "cannot read %s" % ref_about)
            continue
        node = ET.parse(ref_about).getroot().find("packageId")
        if node is None or not node.text:
            fail("5", "no packageId in %s" % ref_about)
            continue
        expected[node.text.strip()] = mod_path

    for pid, mod_path in sorted(expected.items()):
        if pid not in used:
            fail("5", "packageId %r from %s is not used in LoadFolders.xml"
                 % (pid, mod_path))
        elif mod_path not in used[pid]:
            fail("5", "packageId %r does not gate %s (gates %s)"
                 % (pid, mod_path, sorted(used[pid])))
        else:
            ok("5", "%s gated by %r, exact match with upstream About.xml"
               % (mod_path, pid))

    external = sorted(set(used) - set(expected))
    if external:
        print("INFO  [5] extra load conditions, not verifiable from ref/: %s"
              % ", ".join(external))


def check_hangul():
    """Check 6."""
    files = []
    for root in (MOD_DIR, "tools", ".github"):
        if os.path.isdir(root):
            files += [root + "/" + p for p in walk(root)]
    for name in ("README.md", "LICENSE", ".gitignore", ".gitattributes"):
        if os.path.isfile(name):
            files.append(name)

    scanned = 0
    for path in files:
        ext = os.path.splitext(path)[1].lower()
        if ext not in TEXT_EXT and os.path.basename(path) not in TEXT_NAMES:
            continue
        scanned += 1
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except UnicodeDecodeError:
            fail("6", "%s is not valid UTF-8" % path)
            continue
        hits = HANGUL.findall(text)
        if hits:
            line = text[:text.index(hits[0])].count("\n") + 1
            fail("6", "Hangul in %s line %d: %s"
                 % (path, line, "".join(sorted(set(hits))[:10])))

    if not [f for f in fails if f[0] == "6"]:
        ok("6", "no Hangul in %d published text files" % scanned)


def main():
    if not os.path.isdir(MOD_DIR) or not os.path.isdir(REF_DIR):
        sys.exit("error: run this from the repository root")

    print("=== texture mapping, resolution, provenance ===")
    textures = check_textures()
    print("")
    print("=== direction and mask sets ===")
    check_sets(textures)
    print("")
    print("=== xml ===")
    check_xml()
    print("")
    print("=== hangul ===")
    check_hangul()

    print("")
    print("-" * 60)
    print("RESULT: %d fail, %d warn" % (len(fails), len(warns)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
