#!/usr/bin/env bash
set -euo pipefail
export HOME=/home/adepablo
export MAMBA_ROOT_PREFIX=/home/adepablo/micromamba
mkdir -p "$HOME/bin"
if [ ! -x "$HOME/bin/micromamba" ]; then
  curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj -C /tmp bin/micromamba
  mv /tmp/bin/micromamba "$HOME/bin/micromamba"
fi
if [ ! -x "$MAMBA_ROOT_PREFIX/envs/mp/bin/python" ]; then
  "$HOME/bin/micromamba" create -y -n mp -c conda-forge python=3.11 pymeep numpy pyyaml
fi
"$HOME/bin/micromamba" run -n mp python -c "import meep; print('meep_ok', meep.__version__)"
