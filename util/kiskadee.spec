Name:           kiskadee
Version:        0.4.3
Release:        2%{?dist}
Summary:        A continuous static analysis system

License:        AGPLv3+
URL:            https://pagure.io/kiskadee
Source0:        https://releases.pagure.org/kiskadee/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires: python3-devel
BuildRequires: python3-psutil
BuildRequires: python3-psycopg2
BuildRequires: python3-firehose
BuildRequires: python3-sqlalchemy
BuildRequires: python3-chardet
BuildRequires: python3-packaging
BuildRequires: python3-PyYAML
BuildRequires: python3-flask
BuildRequires: python3-flask-restless
BuildRequires: python3-marshmallow
BuildRequires: python3-nose
BuildRequires: python3-fedmsg
BuildRequires: python3-alembic
BuildRequires: python3-debian

BuildRequires: systemd
%{?systemd_requires}

Requires: python3-psutil
Requires: python3-psycopg2
Requires: python3-firehose
Requires: python3-sqlalchemy
Requires: python3-chardet
Requires: python3-packaging
Requires: python3-PyYAML
Requires: python3-flask
Requires: python3-flask-restless
Requires: python3-marshmallow
Requires: python3-nose
Requires: python3-fedmsg
# BUG: https://bugzilla.redhat.com/show_bug.cgi?id=1114413
Requires: python3-flask-cors
Requires: python3-alembic
Requires: python3-debian

%description
kiskadee is a system to support static analysis usage during software
development by providing ranked static analysis reports.
First, it runs multiple security-oriented static analyzers on the source code.
Then, using a classification model, the possible bugs detected by the static
analyzers are ranked based on their importance, where critical flaws are
ranked first and potential false positives are ranked last.

%prep
%autosetup

%build
%py3_build

%install
%py3_install
# install config file
mkdir -p %{buildroot}%{_sysconfdir}
install -p -m 644 util/kiskadee.conf %{buildroot}%{_sysconfdir}

# install fedmsg consumers
mkdir -p %{buildroot}%{_sysconfdir}/fedmsg.d
install -p -m 644 util/base.py %{buildroot}%{_sysconfdir}/fedmsg.d/base.py
install -p -m 644 util/anityaconsumer.py %{buildroot}%{_sysconfdir}/fedmsg.d/anityaconsumer.py

# install systemd units
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 util/kiskadee.service %{buildroot}%{_unitdir}/kiskadee.service
install -p -m 644 util/kiskadee_api.service %{buildroot}%{_unitdir}/kiskadee_api.service

%check
# We skip tests since they are running docker containers for now.

%post
%systemd_post kiskadee.service kiskadee_api.service

%preun
%systemd_preun kiskadee.service kiskadee_api.service

%postun
%systemd_postun_with_restart kiskadee.service kiskadee_api.service

%files
%license LICENSE
%doc doc
%{_bindir}/%{name}
%{_bindir}/%{name}_api
%{python3_sitelib}/%{name}
%{python3_sitelib}/%{name}*.egg-info
%{_unitdir}/kiskadee.service
%{_unitdir}/kiskadee_api.service
%config(noreplace) %{_sysconfdir}/kiskadee.conf
%config(noreplace) %{_sysconfdir}/fedmsg.d/base.py*
%config(noreplace) %{_sysconfdir}/fedmsg.d/anityaconsumer.py*

%changelog
* Thu Mar 08 2018 Athos Ribeiro <athoscr@fedoraproject.org> - 0.4.3-2
- Add missing dependency python3-debian

* Wed Mar 07 2018 Athos Ribeiro <athoscr@fedoraproject.org> - 0.4.3-1
- Update version

* Sat Dec 30 2017 Athos Ribeiro <athoscr@fedoraproject.org> - 0.4.3-0.4.20171118git5b3c751
- Remove conflicting anitya endpoints config file from fedmsg directory

* Tue Dec 05 2017 Athos Ribeiro <athoscr@fedoraproject.org> - 0.4.3-0.3.20171118git5b3c751
- Install anitya endpoint for fedmsg

* Tue Nov 21 2017 Athos Ribeiro <athoscr@fedoraproject.org> - 0.4.3-0.2.20171118git5b3c751
- Install systemd units
- Minor improvements (refactoring)
- Fix bogus date on Release VCS timestamp

* Sat Nov 18 2017 Athos Ribeiro <athoscr@fedoraproject.org> - 0.4.3-0.1.20171118git5b3c751
- Update version
- Requires and BRs python3-alembic

* Sat Nov 18 2017 Athos Ribeiro <athoscr@fedoraproject.org> - 0.4.2-3
- Fix version-release
- Add Requires for python3-flask-cors
- Fix BRs
- Set proper License tag
- Set target architecture as noarch

* Sat Nov 11 2017 David Carlos <ddavidcarlos1392@gmail.com> - 0.4.2-2
- Add fedmsg config files on /etc/fedmsg.d/ directory

* Sat Nov 11 2017 David Carlos <ddavidcarlos1392@gmail.com> - 0.4.2-1
- Fix kiskadee.conf path

* Sun Nov 05 2017 David Carlos <ddavidcarlos1392@gmail.com> - 0.4.1-1
- Initial packaging work for Fedora

