# A KMP built the way SUSE requires, with the kernel_module_package macro.
#
# build.sh builds it several times with different --define options, to get
# KMPs that differ in exactly one property:
#   sdc_name        package sdc-<sdc_name>, module sdc_<sdc_name>
#   sdc_license     RPM License tag
#   sdc_vendor      RPM Vendor tag, "none" for no Vendor tag
#   sdc_km_license  MODULE_LICENSE() of the module
#   sdc_supported   "supported" flag of the module, "none" for no flag
#   sdc_supported2  a second "supported" flag (optional)
#   sdc_sign_dir    sign the module with signing_key.pem/signing_key.x509 in this
#                   directory (optional)

%{!?sdc_name: %global sdc_name good}
%{!?sdc_license: %global sdc_license GPL-2.0-only}
%{!?sdc_vendor: %global sdc_vendor SDC Test Vendor}
%{!?sdc_km_license: %global sdc_km_license GPL}
%{!?sdc_supported: %global sdc_supported external}
%global sdc_module %(echo sdc_%{sdc_name} | tr - _)

# keep the module as built: stripping would remove its signature
%global debug_package %{nil}
%global __os_install_post %{nil}

Name:           sdc-%{sdc_name}
Version:        1.0
Release:        1
Summary:        soliddriver-checks test KMP %{sdc_name}
License:        %{sdc_license}
%if "%{sdc_vendor}" != "none"
Vendor:         %{sdc_vendor}
%endif
Source0:        sdc-module.tar.gz
BuildRequires:  kernel-default-devel
%kernel_module_package -x 64kb

%description
Test package for the soliddriver-checks test suite. Don't install it on a real
system.

%prep
%setup -q -n module
set -- *
mkdir source
mv "$@" source/
mkdir obj

%build
for flavor in %flavors_to_build; do
    rm -rf obj/$flavor
    cp -r source obj/$flavor
    make -C %{kernel_source $flavor} M=$PWD/obj/$flavor modules \
        SDC_NAME=%{sdc_module} \
        SDC_LICENSE="%{sdc_km_license}" \
%if "%{sdc_supported}" != "none"
        SDC_SUPPORTED="%{sdc_supported}" \
%endif
        SDC_SUPPORTED2="%{?sdc_supported2}"
%if 0%{?sdc_sign_dir:1}
    %{kernel_source $flavor}/scripts/sign-file sha256 \
        %{sdc_sign_dir}/signing_key.pem %{sdc_sign_dir}/signing_key.x509 \
        obj/$flavor/%{sdc_module}.ko
%endif
done

%install
export INSTALL_MOD_PATH=%{buildroot}
export INSTALL_MOD_DIR=updates
for flavor in %flavors_to_build; do
    make -C %{kernel_source $flavor} M=$PWD/obj/$flavor modules_install
done
# modules_install doesn't know about the module of an out-of-tree build
rm -f %{buildroot}/lib/modules/*/modules.* %{buildroot}/usr/lib/modules/*/modules.*

%changelog
