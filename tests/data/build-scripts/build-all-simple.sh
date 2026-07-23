#!/bin/bash
set -e

echo "============================================"
echo "Building Comprehensive Test KMP Packages"
echo "Simple approach: build modules then package"
echo "============================================"

SCRIPT_DIR="$(dirname "$0")"
KERNEL_VER=$(uname -r)
KM_BUILD_DIR="/home/claude/soliddriver-checks/km-build"
SPECS_DIR="/home/claude/soliddriver-checks/test-data/SPECS"

# Create build directories
mkdir -p "$KM_BUILD_DIR"/{perfect,bsd,nowm2}
mkdir -p "$SPECS_DIR"

echo ""
echo "Step 1: Building kernel modules..."
echo "-----------------------------------"

# Build perfect module
echo "[1/6] Building perfect module..."
cd "$SCRIPT_DIR/perfect"
make clean || true
make
cp *.ko "$KM_BUILD_DIR/perfect/"

# Build BSD module
echo "[2/6] Building BSD module..."
cd "$SCRIPT_DIR/bsd-license"
make clean || true
make
cp *.ko "$KM_BUILD_DIR/bsd/"

# Build no-wm2 module
echo "[3/6] Building no-wm2 module..."
cd "$SCRIPT_DIR/no-wm2"
make clean || true
make
cp *.ko "$KM_BUILD_DIR/nowm2/"

# Update existing modules (already built)
echo "[4/6] Using existing proprietary module..."
echo "[5/6] Using existing unknown module..."
echo "[6/6] Using existing nosupported module..."

echo ""
echo "Step 2: Creating RPM spec files..."
echo "-----------------------------------"

# Perfect KMP spec
cat > "$SPECS_DIR/perfect-kmp.spec" << 'SPEC1'
Name:           perfect-kmp
Version:        1.0
Release:        1
Summary:        Perfect Test KMP - All Validations Pass
License:        GPL-2.0
Vendor:         SUSE
Group:          System/Kernel
BuildArch:      x86_64

%description
Perfect test KMP with all validations passing

%install
mkdir -p %{buildroot}/lib/modules/$(uname -r)/extra
cp /home/claude/soliddriver-checks/km-build/perfect/perfect_test.ko %{buildroot}/lib/modules/$(uname -r)/extra/

%post
/usr/lib/module-init-tools/weak-modules2 --add-kernel || :

%postun
/usr/lib/module-init-tools/weak-modules2 --remove-kernel || :

%files
/lib/modules/*/extra/perfect_test.ko

%changelog
* Mon Jul 22 2026 - Test
- Perfect KMP test package
SPEC1

# BSD KMP spec
cat > "$SPECS_DIR/bsd-license-kmp.spec" << 'SPEC2'
Name:           bsd-license-kmp
Version:        1.0
Release:        1
Summary:        BSD License Test KMP
License:        BSD-3-Clause
Vendor:         SUSE
Group:          System/Kernel
BuildArch:      x86_64

%description
Test KMP with BSD license

%install
mkdir -p %{buildroot}/lib/modules/$(uname -r)/extra
cp /home/claude/soliddriver-checks/km-build/bsd/bsd_test.ko %{buildroot}/lib/modules/$(uname -r)/extra/

%post
/usr/lib/module-init-tools/weak-modules2 --add-kernel || :

%postun
/usr/lib/module-init-tools/weak-modules2 --remove-kernel || :

%files
/lib/modules/*/extra/bsd_test.ko

%changelog
* Mon Jul 22 2026 - Test
- BSD license test package
SPEC2

# No WM2 KMP spec (no %post/%postun)
cat > "$SPECS_DIR/no-wm2-kmp.spec" << 'SPEC3'
Name:           no-wm2-kmp
Version:        1.0
Release:        1
Summary:        No Weak-modules2 Test KMP
License:        GPL-2.0
Vendor:         SUSE
Group:          System/Kernel
BuildArch:      x86_64

%description
Test KMP without weak-modules2 invocation

%install
mkdir -p %{buildroot}/lib/modules/$(uname -r)/extra
cp /home/claude/soliddriver-checks/km-build/nowm2/nowm2_test.ko %{buildroot}/lib/modules/$(uname -r)/extra/

%files
/lib/modules/*/extra/nowm2_test.ko

%changelog
* Mon Jul 22 2026 - Test
- No weak-modules2 test package
SPEC3

# Update existing specs to add vendor and WM2
cat > "$SPECS_DIR/license-test-proprietary-kmp.spec" << 'SPEC4'
Name:           license-test-proprietary-kmp
Version:        1.0
Release:        1
Summary:        Proprietary Module License Test
License:        GPL-2.0
Vendor:         SUSE
Group:          System/Kernel
BuildArch:      x86_64

%description
Test KMP with proprietary module license

%install
mkdir -p %{buildroot}/lib/modules/$(uname -r)/extra
cp /home/claude/soliddriver-checks/km-build/proprietary/proprietary_test.ko %{buildroot}/lib/modules/$(uname -r)/extra/

%post
/usr/lib/module-init-tools/weak-modules2 --add-kernel || :

%postun
/usr/lib/module-init-tools/weak-modules2 --remove-kernel || :

%files
/lib/modules/*/extra/proprietary_test.ko

%changelog
* Mon Jul 22 2026 - Test
- Proprietary license test
SPEC4

cat > "$SPECS_DIR/license-test-unknown-kmp.spec" << 'SPEC5'
Name:           license-test-unknown-kmp
Version:        1.0
Release:        1
Summary:        Unknown Module License Test
License:        GPL-2.0
Vendor:         SUSE
Group:          System/Kernel
BuildArch:      x86_64

%description
Test KMP with unknown module license

%install
mkdir -p %{buildroot}/lib/modules/$(uname -r)/extra
cp /home/claude/soliddriver-checks/km-build/unknown/unknown_test.ko %{buildroot}/lib/modules/$(uname -r)/extra/

%post
/usr/lib/module-init-tools/weak-modules2 --add-kernel || :

%postun
/usr/lib/module-init-tools/weak-modules2 --remove-kernel || :

%files
/lib/modules/*/extra/unknown_test.ko

%changelog
* Mon Jul 22 2026 - Test
- Unknown license test
SPEC5

cat > "$SPECS_DIR/license-test-nosupported-kmp.spec" << 'SPEC6'
Name:           license-test-nosupported-kmp
Version:        1.0
Release:        1
Summary:        No Supported Flag Test
License:        GPL-2.0
Vendor:         SUSE
Group:          System/Kernel
BuildArch:      x86_64

%description
Test KMP without supported flag

%install
mkdir -p %{buildroot}/lib/modules/$(uname -r)/extra
cp /home/claude/soliddriver-checks/km-build/nosupported/nosupported_test.ko %{buildroot}/lib/modules/$(uname -r)/extra/

%post
/usr/lib/module-init-tools/weak-modules2 --add-kernel || :

%postun
/usr/lib/module-init-tools/weak-modules2 --remove-kernel || :

%files
/lib/modules/*/extra/nosupported_test.ko

%changelog
* Mon Jul 22 2026 - Test
- No supported flag test
SPEC6

echo ""
echo "Step 3: Building RPMs..."
echo "-----------------------------------"

cd /home/claude/soliddriver-checks/test-data

# Build all RPMs
for spec in "$SPECS_DIR"/*.spec; do
    name=$(basename "$spec" .spec)
    echo "Building $name..."
    rpmbuild -bb "$spec" \
        --define "_rpmdir ." \
        --buildroot=/tmp/rpm-build-$name
done

echo ""
echo "============================================"
echo "✓ All packages built successfully"
echo "============================================"
ls -lh *.rpm
SPEC