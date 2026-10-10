"""Replace symlinks in the Hugging Face cache snapshots of VieNeu models with real files.

ONNX Runtime refuses external-data files reached through a symlink ("External data
path escapes model directory"). On Windows with Developer Mode, huggingface_hub
stores snapshots as symlinks into blobs/, so VieNeu v3 Turbo fails to load.

Only the repos VieNeu v3 Turbo needs are touched. Blobs are kept; each snapshot
symlink becomes a copy of its blob (disk use roughly doubles for these models).

Usage: python fix_hf_symlinks.py [--dry-run]
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

REPOS = (
    "models--pnnbao-ump--VieNeu-TTS-v3-Turbo",
    "models--OpenMOSS-Team--MOSS-Audio-Tokenizer-Nano-ONNX",
)


def hub_dir() -> Path:
    if os.environ.get("HF_HUB_CACHE"):
        return Path(os.environ["HF_HUB_CACHE"])
    if os.environ.get("HF_HOME"):
        return Path(os.environ["HF_HOME"]) / "hub"
    return Path.home() / ".cache" / "huggingface" / "hub"


def fix(dry_run: bool = False) -> int:
    fixed = 0
    for repo in REPOS:
        snaps = hub_dir() / repo / "snapshots"
        if not snaps.is_dir():
            continue
        for link in snaps.rglob("*"):
            if not link.is_symlink():
                continue
            target = link.resolve()
            if not target.is_file():
                print(f"BỎ QUA (đích không tồn tại): {link}")
                continue
            print(f"{'SẼ SỬA' if dry_run else 'SỬA'}: {link.relative_to(hub_dir())}")
            if not dry_run:
                tmp = link.with_name(link.name + ".tmp-copy")
                shutil.copy2(target, tmp)
                link.unlink()
                tmp.rename(link)
            fixed += 1
    return fixed


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    n = fix(ap.parse_args().dry_run)
    print(f"Xong: {n} symlink.")
