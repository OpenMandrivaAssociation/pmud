%define name	pmud
%define version	0.10.1
%define release	8mdk

Summary:	Power Manager daemon for Apple Powerbooks
Name:		%{name}
Version:	%{version}
Release:	%{release}
Source0:	pmud-%{version}.tar.bz2
Source1:	batmon.16.png
Source2:	batmon.32.png
Source3:	batmon.48.png
Patch0:		pmud-kver-10.1-mdk.patch.bz2
# Add option "sysconfig" to trackpad to read /etc/sysconfig/mouse
# TRACKPAD_TAP=(yes|no)
Patch1:		pmud-0.7-sysconfig.patch.bz2
Patch2:		pmud-10.1-smarter-rc.patch.bz2
Patch3:		pmud-0.10-fcntl.patch.bz2
Patch4:		pmud-0.10-broken-initscript.patch.bz2
Patch5:		pmud-0.10-lsb-init.patch.bz2
License:	GPL
URL:		http://www3.jvc.nl/linuxppc
Group:		Monitoring
BuildRoot:	%{_tmppath}/%{name}-buildroot
Provides:	apmd
Requires(pre):	/sbin/chkconfig rpm-helper
Requires(preun):	/sbin/chkconfig rpm-helper
# Batmon requires tcl/tk
Requires:	tcl, tk, hdparm
BuildRequires:	XFree86-devel
ExclusiveArch:	ppc

%description 
Pmud is a daemon which periodically polls the PMU (power manager) and
performs functions such as enabling or disabling devices appropriately
when the power source changes. It can also be instructed to signal
init(8) that a power-failure has occured.

%prep

%setup -q -n pmud-0.10
%patch0 -p1 -b .kver
%patch1 -p1 -b .sysconfig
%patch2 -p1 -b .smarter
%patch3 -p1 -b .fcntl
%patch4 -p1 -b .broken
%patch5 -p1 -b .lsb

%build
%serverbuild
%make CC=gcc CFLAGS="$RPM_OPT_FLAGS"

%install
rm -fr $RPM_BUILD_ROOT

install -m 0744 pwrctl -D $RPM_BUILD_ROOT%{_sysconfdir}/power/pwrctl
install -m 0644 power.conf -D $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/power/power.conf
install -m 0755 pmud.rc -D $RPM_BUILD_ROOT%{_initrddir}/pmud

# install file but lowercase'ize its name first
InstallFile() {
	source="$1" perms="$2" directory="$3"
	target=`echo $source | tr '[A-Z]' '[a-z]'`
	install -m $perms $source -D $directory/$target
}

(for file in pmud wakebay snooze fblevel trackpad; do
	InstallFile $file 0755 $RPM_BUILD_ROOT/sbin
done)

(for file in xmouse Batmon backlight; do
	InstallFile $file 0755 $RPM_BUILD_ROOT%{_bindir}
done)

(for file in pmud.8 snooze.8 fblevel.8 batmon.8 xmouse.8; do
	InstallFile $file 0644 $RPM_BUILD_ROOT%{_mandir}/man8
done)
	
(cd $RPM_BUILD_ROOT%{_bindir}; ln -sf ../../sbin/snooze apm)

# mdk icons
install -m644 %SOURCE1 -D $RPM_BUILD_ROOT%{_miconsdir}/batmon.png
install -m644 %SOURCE2 -D $RPM_BUILD_ROOT%{_iconsdir}/batmon.png
install -m644 %SOURCE3 -D $RPM_BUILD_ROOT%{_liconsdir}/batmon.png

# mdk menus
mkdir -p $RPM_BUILD_ROOT%{_menudir}

cat << EOF > $RPM_BUILD_ROOT%{_menudir}/batmon
?package(pmud):command="%{_bindir}/batmon" icon="batmon.png" \
	needs="X11" section="Applications/Monitoring" title="Batmon" \
	longtitle="Battery life monitor for Apple Powerbooks"
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%pre 
[ -c /dev/pmu ] || {
	echo "creating /dev/pmu"
	mknod /dev/pmu c 10 154
}

%post 
%_post_service pmud
%update_menus

%preun
%_preun_service pmud

%postun
%clean_menus

%files
%defattr(-,root,root)
#
%doc TODO
%doc BUGS
%doc README
%doc INSTALL
%doc CHANGES
%doc THANKS
%doc pwrctl-local
#
%{_mandir}/man8/pmud.8*
%{_mandir}/man8/snooze.8*
%{_mandir}/man8/fblevel.8*
%{_mandir}/man8/batmon.8*
%{_mandir}/man8/xmouse.8*
#
%config(noreplace) %{_sysconfdir}/sysconfig/power
%config(noreplace) %{_sysconfdir}/power/pwrctl
%config(noreplace) %{_initrddir}/pmud 
#
%{_menudir}/batmon
%{_miconsdir}/batmon*
%{_iconsdir}/batmon*
%{_liconsdir}/batmon*
#
/sbin/pmud
/sbin/snooze
/sbin/wakebay
/sbin/fblevel
/sbin/trackpad
#
%{_bindir}/xmouse
%{_bindir}/batmon
%{_bindir}/backlight
%{_bindir}/apm

