#!/bin/bash --login

set +euo pipefail
conda activate emishows
set -euo pipefail

exec "$@"
