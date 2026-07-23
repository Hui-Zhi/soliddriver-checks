Name:           license-test-unknown-kmp
Version:        1.0
Release:        1
Summary:        Test KMP with unknown license
License:        GPL-2.0
Vendor:         SUSE
Group:          System/Kernel
Source0:        module.c
Source1:        Makefile
BuildRequires:  kernel-devel
BuildRequires:  module-init-tools

%kernel_module_package

%description
Test kernel module package with unknown license.
Used for validating soliddriver-checks license detection.

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
* Mon Jul 21 2026 - Test Suite
- Initial test package for license validation
