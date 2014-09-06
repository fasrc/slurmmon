Name: slurmmon
Version: 0.0.2
Release: fasrc04
Summary: gather and plot data about Slurm
Packager: Harvard FAS Research Computing -- John Brunelle <john_brunelle@harvard.edu>
Group: System Environment/Base
License: BSD
Source: %{name}-%{version}.tar.bz2

Prefix: /

%description
Slurmmon is a system for gaining insight into Slurm and the jobs it runs.
It's meant for cluster administrators looking to raise cluster utilization and measure the effects of configuration changes.


%package daemon
Summary: slurmmon daemon that collects data
Group: System Environment/Base
Prefix: /etc
Prefix: /usr
%description daemon
Slurmmon is a system for gaining insight into Slurm and the jobs it runs.
It's meant for cluster administrators looking to raise cluster utilization and measure the effects of configuration changes.
This subpackage is the slurmmon daemon that collects data.

%package ganglia
Summary: slurmmon ganglia reports
Group: System Environment/Base
Prefix: /var/www/ganglia/graph.d
%description ganglia
Slurmmon is a system for gaining insight into Slurm and the jobs it runs.
It's meant for cluster administrators looking to raise cluster utilization and measure the effects of configuration changes.
This subpackage is the slurmmon ganglia reports.

%package web
Summary: slurmmon summary web pages
Group: System Environment/Base
Prefix: /etc/httpd/conf.d
Prefix: /var/www/html/slurmmon
%description web
Slurmmon is a system for gaining insight into Slurm and the jobs it runs.
It's meant for cluster administrators looking to raise cluster utilization and measure the effects of configuration changes.
This subpackage is the slurmmon web frontend.

%package python
Summary: slurmmon python library
Group: System Environment/Base
Prefix: /usr/lib/python2.6/site-packages
%description python
Slurmmon is a system for gaining insight into Slurm and the jobs it runs.
It's meant for cluster administrators looking to raise cluster utilization and measure the effects of configuration changes.
This subpackages is the general python library for interfacing with Slurm.


%prep

%setup


%build


%install

echo %{buildroot} | grep -q %{name}-%{version} && rm -rf %{buildroot}
mkdir -p %{buildroot}/
for d in etc usr var; do
	rsync -av --exclude .gitignore "$d"/ %{buildroot}/"$d"/
done
mkdir -p %{buildroot}/usr/lib/python2.6/site-packages/
rsync -av lib/python/site-packages/ %{buildroot}/usr/lib/python2.6/site-packages/


%files daemon
%defattr(-,root,root,-)
/etc/init.d/slurmmond
/etc/init.d/slurmmond-computenode
/usr/sbin/slurmmond
/usr/sbin/slurmmon_whitespace_report
%config(noreplace) /etc/slurmmon.conf

%files ganglia
%defattr(-,apache,apache,-)
/var/www/ganglia/graph.d/*
%config(noreplace) /etc/slurmmon.conf

%files web
%defattr(-,root,root,-)
/var/www/html/slurmmon/index.psp
%config(noreplace) /var/www/html/slurmmon/whitespace/latest
%config(noreplace) /etc/httpd/conf.d/slurmmon.conf
%config(noreplace) /etc/slurmmon.conf

%files python
%defattr(-,root,root,-)
/usr/lib/python2.6/site-packages/*
