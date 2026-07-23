Name:           bsd-license-kmp
Version:        1.0
Release:        1
Summary:        BSD License Test KMP
License:        BSD-3-Clause
Vendor:         SUSE
Group:          System/Kernel
Source0:        module.c
Source1:        Makefile
BuildRequires:  kernel-devel
BuildRequires:  module-init-tools

%kernel_module_package

%description
Test KMP with BSD license (valid open source).
Tests that BSD licenses are properly recognized as valid.

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

%post
/usr/lib/module-init-tools/weak-modules2 --add-kernel || :

%postun
/usr/lib/module-init-tools/weak-modules2 --remove-kernel || :

%changelog
* Mon Jul 22 2026 - Test Suite
- BSD license test package
