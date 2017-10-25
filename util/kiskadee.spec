Name:           kiskadee
Version:        0.3.1
Release:        1%{?dist}
Summary:        kiskadee is a continuous static analysis tool which writes the analysis results into a Firehose database.

License:        GPLv3
URL:            https://pagure.io/kiskadee
Source0:        %{name}-%{version}.tar.gz

BuildRequires: openssl-devel
BuildRequires: python3-devel
BuildRequires: gcc
BuildRequires: redhat-rpm-config

Requires: docker

%description


%prep
%autosetup


%build
%py3_build


%install
%py3_install


%files
%license add-license-file-here
%doc add-docs-here



%changelog
* Wed Oct 25 2017 David Carlos <ddavidcarlos1392@gmail.com>
-
