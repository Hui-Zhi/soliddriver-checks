# A package with "-kmp-" in its name that is NOT built with the
# kernel_module_package macro: it packages the module by hand, has no
# scriptlets, and has no automatic ksym() requirements or modalias()
# supplements. build.sh uses it for the packaging mistakes the checks must
# find, and for the module formats.
#
# --define options:
#   sdc_name         package sdc-<sdc_name>-kmp-default, module sdc_<sdc_name>
#   sdc_pkg_name     package name, overrides the one from sdc_name (optional)
#   sdc_compress     none, xz or zstd: compress the module (.ko, .ko.xz, .ko.zst)
#   sdc_requires     extra Requires: tag (optional)
#   sdc_supplements  Supplements: tag (optional)
#   sdc_no_module    package a text file instead of a module (optional)

%{!?sdc_name: %global sdc_name manual}
%{!?sdc_pkg_name: %global sdc_pkg_name sdc-%{sdc_name}-kmp-default}
%{!?sdc_compress: %global sdc_compress none}
%global sdc_module %(echo sdc_%{sdc_name} | tr - _)
%global sdc_kdir /usr/src/linux-obj/%{_target_cpu}/default
%global sdc_kver %(cat %{sdc_kdir}/include/config/kernel.release)
# usr-merged systems (Leap 16, Tumbleweed) keep modules in /usr/lib/modules
%global sdc_moddir %(test -L /lib && echo /usr/lib/modules || echo /lib/modules)

%global debug_package %{nil}
%global __os_install_post %{nil}

Name:           %{sdc_pkg_name}
Version:        1.0
Release:        1
Summary:        soliddriver-checks test package %{sdc_name}
License:        GPL-2.0-only
Vendor:         SDC Test Vendor
Source0:        sdc-module.tar.gz
BuildRequires:  kernel-default-devel
AutoReqProv:    no
%{?sdc_requires:Requires: %{sdc_requires}}
%{?sdc_supplements:Supplements: %{sdc_supplements}}

%description
Test package for the soliddriver-checks test suite. Don't install it on a real
system.

%prep
%setup -q -n module

%build
%if 0%{!?sdc_no_module:1}
make -C %{sdc_kdir} M=$PWD modules SDC_NAME=%{sdc_module} SDC_SUPPORTED=external
%endif

%install
mkdir -p %{buildroot}%{sdc_moddir}/%{sdc_kver}/updates
%if 0%{?sdc_no_module:1}
echo "no kernel module in here" > %{buildroot}%{sdc_moddir}/%{sdc_kver}/updates/README.sdc
%else
install -m 644 %{sdc_module}.ko %{buildroot}%{sdc_moddir}/%{sdc_kver}/updates/
%if "%{sdc_compress}" == "xz"
xz %{buildroot}%{sdc_moddir}/%{sdc_kver}/updates/%{sdc_module}.ko
%endif
%if "%{sdc_compress}" == "zstd"
zstd -q --rm %{buildroot}%{sdc_moddir}/%{sdc_kver}/updates/%{sdc_module}.ko
%endif
%endif

%files
%{sdc_moddir}/%{sdc_kver}

%changelog
