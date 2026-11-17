#!/bin/bash
# Run the test suite in the test container.
#
# Builds the image from tests/container_env/, mounts the repository read-only,
# and runs pytest in a throw-away container: the tests install KMPs and change
# /lib/modules. Arguments are passed to pytest, e.g.
#   tests/run_tests.sh -k filter -v

set -euo pipefail

repo=$(cd "$(dirname "$0")/.." && pwd)
image=opensuse-leap-soliddriver-checks

docker build -q -t "$image" "$repo/tests/container_env" >/dev/null

tty=""
[ -t 1 ] && tty=-t

docker run --rm $tty \
    --mount type=bind,source="$repo",target=/root/source_codes,readonly \
    "$image" \
    bash -c './build_install.sh >/tmp/install.log 2>&1 || { cat /tmp/install.log; exit 1; }
             cd /tmp && exec python3.13 -m pytest -p no:cacheprovider /root/source_codes/tests "$@"' \
    bash "$@"
