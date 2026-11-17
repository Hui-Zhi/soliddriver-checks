#!/bin/bash
# Build the test KMPs into OUTDIR, from module/ and specs/.
#
# Every package differs from sdc-good in one property, so each check can be
# tested on its own. The tests (tests/conftest.py) run this once per session.
# It needs kernel-default-devel, rpm-build, gcc, make, openssl, gpg2, xz and
# zstd; see tests/container_env/Dockerfile.

set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
out=${1:?usage: build.sh OUTDIR}

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$out" "$work/SOURCES" "$work/keys"
tar -czf "$work/SOURCES/sdc-module.tar.gz" -C "$here" module

# key to sign kernel modules with
openssl req -new -x509 -newkey rsa:2048 -nodes -days 36500 \
    -subj "/CN=soliddriver-checks test/" \
    -keyout "$work/keys/signing_key.pem" \
    -outform DER -out "$work/keys/signing_key.x509" 2>/dev/null

# key to sign RPMs with
export GNUPGHOME="$work/gnupg"
mkdir -m 700 "$GNUPGHOME"
gpg --batch --quiet --passphrase '' \
    --quick-gen-key "soliddriver-checks test <sdc-test@example.com>" rsa2048 sign never

build() {
    local spec=$1
    shift
    if ! rpmbuild -bb --define "_topdir $work" "$@" "$here/specs/$spec" \
        >"$work/build.log" 2>&1; then
        cat "$work/build.log" >&2
        return 1
    fi
}

# KMPs built with the kernel_module_package macro
build sdc-kmp.spec --define "sdc_name good" --define "sdc_sign_dir $work/keys"
build sdc-kmp.spec --define "sdc_name unsigned"
build sdc-kmp.spec --define "sdc_name novendor" --define "sdc_vendor none"
build sdc-kmp.spec --define "sdc_name proprietary" \
    --define "sdc_license Proprietary" --define "sdc_km_license Proprietary"
build sdc-kmp.spec --define "sdc_name spdx" \
    --define "sdc_license GPL-2.0-only WITH Linux-syscall-note OR GPL-2.0-or-later"
build sdc-kmp.spec --define "sdc_name spdx-mit" --define "sdc_license GPL-2.0-only AND MIT"
build sdc-kmp.spec --define "sdc_name nosupported" --define "sdc_supported none"
build sdc-kmp.spec --define "sdc_name supported-yes" --define "sdc_supported yes"
build sdc-kmp.spec --define "sdc_name supported-bad" --define "sdc_supported vendor"
build sdc-kmp.spec --define "sdc_name supported-multi" --define "sdc_supported2 yes"

# packages that are not built with the kernel_module_package macro
build sdc-manual.spec --define "sdc_name nowm2"
build sdc-manual.spec --define "sdc_name badksym" \
    --define "sdc_requires ksym(default:_printk) = deadbeef"
build sdc-manual.spec --define "sdc_name allalias" \
    --define "sdc_supplements modalias(kernel-default:*)"
build sdc-manual.spec --define "sdc_name xz" --define "sdc_compress xz"
build sdc-manual.spec --define "sdc_name zst" --define "sdc_compress zstd"
build sdc-manual.spec --define "sdc_name nomodule" --define "sdc_no_module 1"
build sdc-manual.spec --define "sdc_name debug" \
    --define "sdc_pkg_name sdc-debug-kmp-default-debuginfo"

find "$work/RPMS" -name '*.rpm' -exec cp {} "$out" \;
rpmsign --addsign --define "_gpg_name sdc-test@example.com" "$out"/sdc-good-kmp-*.rpm >/dev/null
