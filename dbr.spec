Summary: A GTK application to read Daisy Talking Books
Name: daisy book reader
Version: 0.1.1
Release: 1
License: GPL
Group: Desktop/Accessibility
#URL: http://dbr.sourceforge.net/
Source0: dbr-%{version}.tar.gz

%define python_version 2.4
%define pygtk2_version 2.6.2
%define gnome_python_version 2.6.2
%define libspi_version 1.7.6

BuildRoot: %{_tmppath}/dbr-%{version}-%{release}-buildroot
BuildRequires:	gnome-common >= 2.12.0
BuildRequires:  python >= %{python_version}
BuildRequires:  pygtk2 >= %{pygtk2_version}
Requires:       python >= %{python_version}
Requires:       pygtk2 >= %{pygtk2_version}

%description
An easy and simple GTK application for reading Daisy Talking Books
thats supports Daisy 2.02 format.

%prep
%setup -q

%build
%configure
make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc
%{_bindir}/dbr
%{_libdir}/python?.?/site-packages/dbr
%{_datadir}/locale/*/*
%{_datadir}/applications/dbr.desktop

%changelog
* Wed Dec 16 2015 Anes P A <anes.pa@gmail.com>
- First attempt to create this file.

