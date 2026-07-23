%define kernel_version %(uname -r)

Name:           perfect-kmp
Version:        1.0
Release:        1
Summary:        Perfect Test KMP - All Validations Pass
License:        GPL-2.0
Vendor:         SUSE
Group:          System/Kernel
Source0:        module.c
Source1:        Makefile
BuildRequires:  kernel-devel

%description
Perfect test KMP demonstrating all validations passing.
This package has:
- Valid vendor (SUSE)
- GPL-2.0 license
- Weak-modules2 invocation
- GPL module with 'supported' flag
All checks should pass (green).

%prep
%setup -qcT
cp %{SOURCE0} .
cp %{SOURCE1} .

%build
make -C /lib/modules/%{kernel_version}/build M=$PWD modules

%install
mkdir -p %{buildroot}/lib/modules/%{kernel_version}/extra
install -m 644 *.ko %{buildroot}/lib/modules/%{kernel_version}/extra/

%post
/usr/lib/module-init-tools/weak-modules2 --add-kernel || :
/sbin/depmod -a %{kernel_version} || :

%postun
/usr/lib/module-init-tools/weak-modules2 --remove-kernel || :
/sbin/depmod -a %{kernel_version} || :

%files
/lib/modules/%{kernel_version}/extra/*.ko

%changelog
* Mon Jul 22 2026 - Test Suite
- Perfect test package with all validations passing
