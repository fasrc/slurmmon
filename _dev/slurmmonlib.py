import sys, socket, subprocess



#--- settings

data_dir = '/odyssey/slurmmon_data'


#--- helpers

def shQuote(text):
	"""quote the given text so that it is a single, safe string in sh code.

	Note that this leaves literal newlines alone (sh and bash are fine with that, but other tools may mess them up and need to do some special handling on the output of this function).
	"""
	return "'%s'" % text.replace("'", r"'\''")


#--- slurm allocation queries

def getAllocations(hostname, method=2):
	"""return a two-item list [number of allocated cores (int), allocated mem in kB (int)]"""

	if method==1:
		#round-about: get all the jobs using the host, and from the jobs get the allocations

		sh = r"squeue -h -o '%%A' -t R -w %s | xargs -n 1 scontrol -dd show job | grep -P '\bNodes='" % shQuote(hostname)
		p = subprocess.Popen(sh, shell=True, stdout=subprocess.PIPE)
		stdout = p.communicate()[0].strip(); rc = p.returncode
		if rc!=0: raise Exception('non-zero exit status: %d' % str(sys.exit((rc,128-rc)[rc<0])))

		cores = 0
		memory = 0

		for line in stdout.split('\n'):
			#total up CPU_ID counts and Mem for each node entry that matches the host of interest
			#some possible lines:
			#	Nodes=holy2a06104 CPU_IDs=10 Mem=4000
			#	Nodes=holy2a13303 CPU_IDs=0-63 Mem=10000
			#	Nodes=holy2a14208 CPU_IDs=15,28-29,31,35,45,59-60 Mem=800
			
			Nodes, CPU_IDs, Mem = line.strip().split()
			
			if Nodes.split('=')[1]==hostname:
				for x in CPU_IDs.split('=')[1].split(','):
					if '-' not in x:
						cores += 1
					else:
						start, end = x.split('-')
						cores += int(end) - int(start) + 1

				memory += int(Mem.split('=')[1]) * 1024  #this factor might need work -- in general slurm sometimes uses 2**10 and sometimes uses 10**3

		return cores, memory
	
	if method==2:
		#more direct: use the numbers from scontrol show node

		sh = r"scontrol show node %s" % shQuote(hostname)
		p = subprocess.Popen(sh, shell=True, stdout=subprocess.PIPE)
		stdout = p.communicate()[0].strip(); rc = p.returncode
		if rc!=0: raise Exception('non-zero exit status: %d' % str(sys.exit((rc,128-rc)[rc<0])))

		cores = None
		memory = None

		#extract CPUAlloc and AllocMem
		for kv in stdout.split():
			if kv.startswith('CPUAlloc'):
				cores = int(kv.split('=')[1])
				if memory is not None:
					break
			elif kv.startswith('AllocMem'):
				memory = int(kv.split('=')[1]) * 1024
				if cores is not None:
					break

		return cores, memory

	raise Exception("internal error: invalid method for getAllocations()")


#--- host data queries

def getHostname():
	"""return the short hostname of this host"""
	return socket.gethostname().split('.')[0]

def getCPU():
	"""return a two-item list [total number of cores (int), number of running tasks (int)]
	
	The number of running tasks is from the 4th colum of /proc/loadavg;
	it's decremented by one in order to account for this process asking for it.
	"""
	#running processes
	with open('/proc/loadavg','r') as f:
		#e.g. 52.10 52.07 52.04 53/2016 54847 -> 53-1 = 52
		used = max(int(f.read().split()[3].split('/')[0]) - 1, 0)
	
	with open('/proc/cpuinfo','r') as f:
		total = 0
		for l in f.readlines():
			if l.startswith('processor'):
				total += 1
	
	return total, used

def getMem():
	"""return a two-item list [total memory in kB (int), used memory in kB (int)]

	The used memory does not count Buffers, Cached, and SwapCached.
	"""
	#in kB
	with open('/proc/meminfo','r') as f:
		total = 0
		free = 0

		for line in f.readlines():
			fields = line.split()
			if fields[0]=='MemTotal:':
				total = int(fields[1])
			if fields[0] in ('MemFree:', 'Buffers:', 'Cached:', 'SwapCached'):
				free += int(fields[1])

		used = total - free

		return total, used


#--- misc

def hostname2gangliaurl(hostname):
	return 'http://status.rc.fas.harvard.edu/ganglia/holyoke_compute/?c=holyoke_compute_odyssey2&h=%s.rc.fas.harvard.edu' % hostname



#--- tests

if __name__=='__main__':
	"""
	print getAllocations(getHostname(), method=1) == getAllocations(getHostname(), method=2)
	"""
