#!/usr/bin/env bash
set -euo pipefail
export HOME=/home/adepablo
export MAMBA_ROOT_PREFIX=/home/adepablo/micromamba
ROOT=/mnt/c/Users/adepablo/maxwellbench
cd "$ROOT"
"$HOME/bin/micromamba" run -n mp python scripts/generate_meep_exam.py
