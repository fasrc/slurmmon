Name: slurmmon
Version: 0.0.1
Release: fasrc01
Summary: gather and plot data about Slurm
Packager: Harvard FAS Research Computing -- John Brunelle <john_brunelle@harvard.edu>
Group: System Environment/Base
License: BSD
Source: %{name}-%{version}.tar.bz2

Prefix: /

%description
slurmmon is a system for monitoring Slurm scheduling and workload characteristics.
It runs daemons that query Slurm about scheduling, submit test jobs, and send metrics to ganglia.
It includes utilities to make various other plots, too.


%package daemon
Summary: slurmmon daemon that collects data
Group: System Environment/Base
Prefix: /etc
Prefix: /sbin
%description daemon
slurmmon is a system for monitoring Slurm scheduling and workload characteristics.
It runs daemons that query Slurm about scheduling, submit test jobs, and send metrics to ganglia.
It includes utilities to make various other plots, too.
This sub-package installs the slurmmon daemon that collects data.

%package ganglia
Summary: slurmmon ganglia reports
Group: System Environment/Base
Prefix: /var/www/ganglia/graph.d
%description ganglia
slurmmon is a system for monitoring Slurm scheduling and workload characteristics.
It runs daemons that query Slurm about scheduling, submit test jobs, and send metrics to ganglia.
It includes utilities to make various other plots, too.
This subpackage installs the slurmmon ganglia reports.

%package web
Summary: slurmmon web summary pages
Group: System Environment/Base
Prefix: /etc/httpd/conf.d
Prefix: /var/www/html/slurmmon
%description web
slurmmon is a system for monitoring Slurm scheduling and workload characteristics.
It runs daemons that query Slurm about scheduling, submit test jobs, and send metrics to ganglia.
It includes utilities to make various other plots, too.
This subpackages installs the slurmmon summary web pages.


%prep

%setup


%build


%install

echo %{buildroot} | grep -q %{name}-%{version} && rm -rf %{buildroot}
mkdir -p %{buildroot}/
for d in etc sbin var; do
	rsync -av "$d"/ %{buildroot}/"$d"/
done


%files daemon
/etc/init.d/slurmmond
/sbin/slurmmond

%files ganglia
/var/www/ganglia/graph.d/*

%files web
/etc/httpd/conf.d/slurmmon.conf
/var/www/html/slurmmon/index.psp
