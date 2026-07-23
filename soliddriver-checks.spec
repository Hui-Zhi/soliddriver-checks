#
# spec file for package soliddriver-checks
#
# Copyright (c) 2026 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

Name:           soliddriver-checks
Version:        3.0.9
Release:        0
Summary:        Validation tool for SUSE Kernel Module Packages
License:        GPL-2.0
URL:            https://github.com/SUSE/soliddriver-checks
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  fdupes

Requires:       python3-bottle >= 0.12.23
Requires:       python3-click >= 8.1.3
Requires:       python3-dominate >= 2.7.0
Requires:       python3-Jinja2 >= 3.1.2
Requires:       python3-lark >= 1.1.0
Requires:       python3-pandas >= 2.0.0
Requires:       python3-rich >= 12.6.0
Requires:       python3-requests >= 2.28.1

%description
soliddriver-checks is a tool for KMP (Kernel Module Package) and
installed/running kernel module checking. With this tool, users can
have a report of their KMP(s) and kernel module status. The report
can be formatted in HTML, XLSX, or JSON.

This tool checks if KMPs and kernel modules are built to meet SUSE's
requirements. It does not analyze code quality or security issues
within the kernel module itself.

%prep
%setup -q

%build
%python3_build

%install
%python3_install
%fdupes %{buildroot}%{python3_sitelib}

%files
%license LICENSE
%doc README.md
%{_bindir}/soliddriver-checks
%{_bindir}/soliddriver-checks-service
%{python3_sitelib}/soliddriver_checks/
%{python3_sitelib}/soliddriver_checks-%{version}*.egg-info/

%changelog
