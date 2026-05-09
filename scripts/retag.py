#!/usr/bin/env python3
"""
scripts/retag.py — retag linux_<arch> wheels to musllinux_1_2_<arch>.

Usage:
    python scripts/retag.py <wheels-dir> [from_tag] [to_tag]

    # armv7l (default)
    python scripts/retag.py ~/podman-builder/wheels/

    # ppc64le
    python scripts/retag.py ~/podman-builder/wheels/ linux_ppc64le musllinux_1_2_ppc64le

    # aarch64
    python scripts/retag.py ~/podman-builder/wheels/ linux_aarch64 musllinux_1_2_aarch64
"""
import sys, zipfile
from pathlib import Path

DEFAULT_FROM = "linux_armv7l"
DEFAULT_TO   = "musllinux_1_2_armv7l"


def retag(src: Path, from_tag: str, to_tag: str) -> Path:
    dst = Path(str(src).replace(from_tag, to_tag))
    if dst.exists():
        print(f"  skip (exists): {dst.name}")
        return dst
    tmp = dst.with_suffix(".tmp")
    with zipfile.ZipFile(src, "r") as zi, \
         zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for item in zi.infolist():
            data = zi.read(item.filename)
            if item.filename.endswith("/WHEEL") or item.filename == "WHEEL":
                data = data.decode().replace(from_tag, to_tag).encode()
            item.filename = item.filename.replace(from_tag, to_tag)
            zo.writestr(item, data)
    tmp.replace(dst)
    print(f"  retagged → {dst.name}")
    return dst


def main():
    if len(sys.argv) < 2:
        print("Usage: retag.py <wheels-dir> [from_tag] [to_tag]")
        sys.exit(1)

    wdir     = Path(sys.argv[1]).expanduser()
    from_tag = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_FROM
    to_tag   = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_TO

    wheels = sorted(wdir.glob(f"*-{from_tag}.whl"))
    if not wheels:
        print(f"No *-{from_tag}.whl files found in {wdir}")
        sys.exit(0)

    print(f"Retagging {len(wheels)} wheels: {from_tag} → {to_tag}")
    for w in wheels:
        retag(w, from_tag, to_tag)
    print("\nDone.")


if __name__ == "__main__":
    main()