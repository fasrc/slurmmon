## Overview / Requirements

Slurmmon is meant to run on a RHEL/CentOS/SL 6 based system (e.g. 6.4).
You'll of course need Slurm, and you'll also need a Ganglia installation and an Apache webserver running mod_python.

Several slurmmon components, such as submitting probe jobs and gathering allocation utilization numbers, are optional.



## Create the `slurmmon` user

The daemons run as a user named `slurmmon`.
If you'll be running probe jobs, this user must be able to submit jobs to all the partitions being probed.
Since it should be a cluster account, the rpms do not make this user -- you have to.
<!-- only need stuff to be able to run job: login shell needed, but home dir not -->

Additionally, since slurmmon doesn't want the probe jobs to suffer hits to fairshare due to the constant job turnover, it increases the priority of each job, and that currently requires sudo.
Thus, if you'll be running probe jobs, add something like this in your sudo configuration:

```
slurmmon HOSTNAME=(slurm) NOPASSWD: /usr/bin/scontrol update JobId\=* Priority\=*
```

where `HOSTNAME` is the node where you're running the main slurmmon daemon (see below).
(Note that the `*` in the above could match multiple words, it's not perfect.)
If you're not running probe jobs, you don't need the sudo config.
<!-- if sudo is not configured, you'll get error like: Dec  9 13:43:45 slurm-test slurmmond(probejob-MYQUEUE)[28115]: metrics for [slurmmond(probejob-MYQUEUE)] failed with message [job priority update ["sudo scontrol update JobId='153' Priority='999999999'"] failed with non-zero returncode [1] and/or non-empty stderr ['sudo: no tty present and no askpass program specified']] -->



## Install the RPMs

### slurmmon-daemon

#### The main `slurmmond`

Identify a host on which to run the main slurmmon daemon that queries Slurm -- the one that collects `sdiag` data, job counts, and other overall information.
This host should be in Ganglia (`gmetric` needs to work), and, if you'll be running probe jobs, it must a host where the `slurmmon` user can run sudo to change job priorities.

Install:

* [slurmmon-daemon-0.0.2-fasrc01.noarch.rpm](RPMS/slurmmon-daemon-0.0.2-fasrc01.noarch.rpm?raw=true)
* [slurmmon-python-0.0.2-fasrc01.noarch.rpm](RPMS/slurmmon-python-0.0.2-fasrc01.noarch.rpm?raw=true)

Configure it by editing `/etc/slurmmon.conf`, which is json.
Specifically, set `probejob_partitions` to be the set of partitions to which you want to send probe jobs.  (Or set it to be empty to not use this feature.)
The default is particular to FASRC.

Start the service:

``` bash
service slurmmond start
```

and `chkconfig` it on:

``` bash
chkconfig slurmmond on
```

#### The compute node `slurmmond-computenode`s

If you want to monitor job allocation utilization and generate the *whitespace* reports of cluster efficiency, each compute node needs to run slurmmon daemons, too.
They are provided by the same rpm package, but the service is named differently and no configuration is necessary.
On each compute node:

Install:

* [slurmmon-daemon-0.0.2-fasrc01.noarch.rpm](RPMS/slurmmon-daemon-0.0.2-fasrc01.noarch.rpm?raw=true)
* [slurmmon-python-0.0.2-fasrc01.noarch.rpm](RPMS/slurmmon-python-0.0.2-fasrc01.noarch.rpm?raw=true)

Start the service:

``` bash
service slurmmond-computenode start
```

and `chkconfig` it on:

``` bash
chkconfig slurmmond-computenode on
```


### slurmmon-ganglia

Identify a host running `ganglia-web`, and a `graph.d` directory into which to put the slurmmon custom reports.
By default the rpm will use `/var/www/ganglia/graph.d`, but this is an available *Relocation* in the rpm.

Install [slurmmon-ganglia-0.0.2-fasrc01.noarch.rpm](RPMS/slurmmon-ganglia-0.0.2-fasrc01.noarch.rpm?raw=true), possibly using `--prefix` to put the files in a custom location.


### slurmmon-web

Identify a host running httpd and mod_python.
By default, the package installs files to `/etc/httpd/conf.d` and `/var/www/html/slurmmon`, but these are available *Relocation*s in the rpm.

Install:

* [slurmmon-web-0.0.2-fasrc01.noarch.rpm](RPMS/slurmmon-web-0.0.2-fasrc01.noarch.rpm?raw=true)
* [slurmmon-python-0.0.2-fasrc01.noarch.rpm](RPMS/slurmmon-python-0.0.2-fasrc01.noarch.rpm?raw=true)

possible using `--prefix` or `--relocate` to put the files in custom locations.

Configure it by editing `/etc/slurmmon.conf`, which is json.
Specifically, set `ploturl_gmetaurl`, `ploturl_cluster`, and `ploturl_host` to what's needed to construct a url to reach the Ganglia plots. 

Reload the web server config:

``` bash
service httpd reload
```

You should now see plots at `http://HOSTNAME/slurmmon/` where `HOSTNAME` is this host.
