#!/usr/bin/env python3
"""Copy-only entry point.

Copies the bundled entry.png (rendered by render.py, committed in
this repository) to /output/entry.png. No network, no drawing, no
timestamps: the same input bytes always produce the same output.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    dst = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    parent = os.path.dirname(dst)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
