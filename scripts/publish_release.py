#!/usr/bin/env python3
"""
scripts/publish_release.py

Creates a GH release tagged <pkg>-<version> and uploads all matching
wheels from a local directory.

Usage:
    python scripts/publish_release.py cryptography 47.0.0 ~/omnipkg/ci-wheel-cache/retagged/
    python scripts/publish_release.py psutil 7.2.2 ~/omnipkg/ci-wheel-cache/retagged/

Requires: gh CLI authenticated.
"""
import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 4:
        print("Usage: publish_release.py <package> <version> <wheels-dir>")
        sys.exit(1)

    pkg     = sys.argv[1]          # e.g. cryptography
    version = sys.argv[2]          # e.g. 47.0.0
    wdir    = Path(sys.argv[3]).expanduser()
    tag     = f"{pkg}-{version}"   # e.g. cryptography-47.0.0

    # Find all wheels for this package+version
    wheels = sorted(wdir.glob(f"{pkg.replace('-','_')}*{version}*.whl")) + \
             sorted(wdir.glob(f"{pkg}*{version}*.whl"))
    # Deduplicate
    seen, unique = set(), []
    for w in wheels:
        if w.name not in seen:
            seen.add(w.name)
            unique.append(w)

    if not unique:
        print(f"No wheels found for {pkg} {version} in {wdir}")
        sys.exit(1)

    print(f"Creating release {tag} with {len(unique)} wheels:")
    for w in unique:
        print(f"  {w.name}")

    cmd = [
        "gh", "release", "create", tag,
        "--title", f"{pkg} {version} — exotic platform wheels",
        "--notes", (
            f"Pre-built wheels for **{pkg} {version}** on exotic platforms "
            f"(musllinux armv7l, etc.) that have no PyPI wheels.\n\n"
            f"Install via:\n"
            f"```\n"
            f"pip install {pkg} --extra-index-url https://exotic-wheels.pages.dev/\n"
            f"```"
        ),
    ] + [str(w) for w in unique]

    subprocess.run(cmd, check=True)
    print(f"\nDone. Run build_index.py to regenerate the simple/ index.")


if __name__ == "__main__":
    main()