Name:           acme-network-kmp
Version:        1.0.0
Release:        1
Summary:        ACME Corporation Network Driver (Test Package)
License:        GPL-2.0
Vendor:         ACME Corporation
Group:          System/Kernel
Source0:        module.c
Source1:        Makefile
BuildRequires:  kernel-devel
BuildRequires:  module-init-tools

%kernel_module_package

%description
ACME Corporation network adapter driver.
This is a test package for validating soliddriver-checks.
ACME Corporation is a fictional company.

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

%changelog
* Mon Jul 22 2026 - Test Suite
- Initial test package with valid configuration
