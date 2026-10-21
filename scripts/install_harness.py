#!/usr/bin/env python3
"""Install a harness version into a real project as .claude/ (after you reviewed it).

Example
  python scripts/install_harness.py harnesses/v2 ~/code/my-shop
"""
import argparse
from pathlib import Path

from common import copy_harness


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("harness")
    ap.add_argument("project")
    args = ap.parse_args()
    dest = Path(args.project).expanduser() / ".claude"
    copy_harness(args.harness, dest)
    print(f"Installed {args.harness} into {dest}")


if __name__ == "__main__":
    main()
