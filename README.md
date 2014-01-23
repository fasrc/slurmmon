## Overview

Slurmmon is a system for gathering and plotting data about [Slurm](http://www.schedmd.com/) scheduling and job characteristics.
It currently simply sends the data to ganglia, but it includes some custom reports and a web page for an organized summary.

It collects all the data from `sdiag` as well as total counts of running and pending jobs in the system and the maximum such values for any single user.
It can also submit *probe* jobs to various partitions in order to trend the times spent pending in them, which is often a good bellwether of scheduling problems.

There are three components to slurmmon:

* [slurmmon-daemon](slurmmon-daemon-0.0.1-fasrc01.noarch.rpm?raw=true) -- the daemons that run Slurm commands such as `sdiag`, `squeue`, etc., submit probe jobs (if configured), and send data to ganglia using `gmetric`
* [slurmmon-ganglia](slurmmon-ganglia-0.0.1-fasrc01.noarch.rpm?raw=true) -- the ganglia custom reports that use php to stack rrd data (to be dropped in a `graph.d` directory in some ganglia installation)
* [slurmmon-web](slurmmon-web-0.0.1-fasrc01.noarch.rpm?raw=true) -- a psp web page that organizes all the reports and relevant plots (which can run on an independent web server)

Here is a screenshot from the production cluster at FASRC:

![slurmmon screenshot](slurmmon_screenshot_small.png "slurmmon screenshot")



## Installation

### Requirements

Slurmmon is meant to run on a RHEL/CentOS/SL 6 based system (e.g. 6.4).
You'll of course need Slurm, and you'll also need a ganglia installation and an apache webserver running mod_python.


### Create the `slurmmon` user

The daemons run as a user named `slurmmon`.
Assuming you'll be running probe jobs, this user should be able to submit jobs to all the partitions being probed.
Therefore, since it should be a cluster account, the rpms do not make this user -- you have to.

Additionally, since slurmmon doesn't want the probe jobs to suffer hits to fairshare due to the constant job turnover, it increases the priority of each job, and that currently requires sudo.
Thus, add something like this in the sudo configuration:

```
slurmmon HOSTNAME=(slurm) NOPASSWD: /usr/bin/scontrol update JobId\=* Priority\=*
```

where `HOSTNAME` is the node where you're running the daemons.
(Note that the `*` in the about could match multiple words, it's not perfect.)
If you're not running probe jobs, you don't need the sudo config.


### Install the RPMs

#### slurmmon-daemon

Identify a Slurm client host on which to run the daemons that query slurm.
This host should also be in ganglia (`gmetric` needs to work), and it should be same host where the `slurmmon` user can run sudo to change job priorities.

Install [slurmmon-daemon-0.0.1-fasrc01.noarch.rpm](slurmmon-daemon-0.0.1-fasrc01.noarch.rpm?raw=true).

Configure it by editing `/etc/slurmmon.conf`, which is json.
Specifically, set `probejob_partitions` to be the set of names of partitions to which you want to send probe jobs.
(The default is particular to FASRC.)

Start the service:

``` bash
service slurmmond start
```

and `chkconfig` it on:

``` bash
chkconfig slurmmond on
```


#### slurmmon-ganglia

Identify a host running `ganglia-web`, and a `graph.d` directory into which to put the slurmmon custom reports.
By default the rpm will use `/var/www/ganglia/graph.d`, but this is an available *Relocation* in the rpm.

Install [slurmmon-ganglia-0.0.1-fasrc01.noarch.rpm](slurmmon-ganglia-0.0.1-fasrc01.noarch.rpm?raw=true), possibly using `--prefix` to put the files in a custom location.


#### slurmmon-web

Identify a host running httpd and mod_python.
By default, the package installs files to `/etc/httpd/conf.d` and `/var/www/html/slurmmon`, but these are available *Relocation*s in the rpm.

Install [slurmmon-web-0.0.1-fasrc01.noarch.rpm](slurmmon-web-0.0.1-fasrc01.noarch.rpm?raw=true), possible using `--prefix` to put the files in custom locations.

Configure it by editing `/etc/slurmmon.conf`, which is json.
Specifically, set `ploturl_gmetaurl`, `ploturl_cluster`, and `ploturl_host` to what's needed to construct a url to reach the ganglia plots. 

Reload the web server config:

``` bash
service httpd reload
```

You should now see plots at `http://HOSTNAME/slurmmon/` where `HOSTNAME` is this host.



## FAQ

### Real jobs are pending a long time but the probe jobs run quickly, why?

The probe jobs are meant to represent what a brand new user running a tiny test job would experience.
The default parameters define a very short, small job (two minutes and 10 MB at the time of writing).
The code also raises the priority of these jobs so that there is no hit to fairshare due to the constant probe submissions.

### Why are the monitoring daemon processes piling up?

They're not really (usually).
The "daemon" is actually several processes (four at the time of writing), running in parallel using python's `multiprocessing` feature, so they have the same command line.
The main daemon will be owned by init, with the other daemons children of the main one.
