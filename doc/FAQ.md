### Real jobs are pending a long time but the probe jobs run quickly, why?

The probe jobs are meant to represent what a brand new user running a tiny test job would experience.
The default parameters define a very short, small job (two minutes and 10 MB at the time of writing).
Slurmmon also raises the priority of these jobs so that there is no hit from fairshare due to the constant probe submissions.

### Why are the monitoring daemon processes piling up?

They're not really (usually).
The "daemon" is actually several processes (four at the time of writing), running in parallel using python's `multiprocessing` feature, so they have the same command line.
The main daemon will be owned by init, with the other daemons children of the main one.
