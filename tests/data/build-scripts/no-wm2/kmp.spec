Name:           no-wm2-kmp
Version:        1.0
Release:        1
Summary:        No Weak-modules2 Test KMP
License:        GPL-2.0
Vendor:         SUSE
Group:          System/Kernel
Source0:        module.c
Source1:        Makefile
BuildRequires:  kernel-devel
BuildRequires:  module-init-tools

%kernel_module_package

%description
Test KMP that does NOT invoke weak-modules2.
Should trigger ERROR for missing weak-modules2 invocation.

%prep
%setup -qcT
cp %{SOURCE0} .
cp %{SOURCE1} .

%build
export EXTRA_CFLAGS='-DVERSION=\"%version\"'
for flavor in %flavors_to_build; do
    rm -rf obj/$flavor
    mkdir -p obj/$flavor
    cp -r * obj/$flavor/ || true
    make -C /lib/modules/%{kernel_version $flavor}/build M=$PWD/obj/$flavor modules
done

%install
export INSTALL_MOD_PATH=$RPM_BUILD_ROOT
export INSTALL_MOD_DIR=updates
for flavor in %flavors_to_build; do
    make -C /lib/modules/%{kernel_version $flavor}/build M=$PWD/obj/$flavor INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install
done

# NOTE: No %post or %postun - intentionally missing weak-modules2

%changelog
* Mon Jul 22 2026 - Test Suite
- Test package without weak-modules2 invocation
