import socket, subprocess



#--- settings

data_dir = '/odyssey/slurmmon_data'


#--- helpers

def shQuote(text):
	"""quote the given text so that it is a single, safe string in sh code.

	Note that this leaves literal newlines alone (sh and bash are fine with that, but other tools may mess them up and need to do some special handling on the output of this function).
	"""
	return "'%s'" % text.replace("'", r"'\''")


#--- slurm allocation queries

def getAllocations(hostname):
	"""a list [allocated cores, allocated mem in kB]"""
	
	sh = r"squeue -h -o '%%A' -t R -w %s | xargs -n 1 scontrol -dd show job | grep -P '\bNodes='" % shQuote(hostname)
	p = subprocess.Popen(sh, shell=True, stdout=subprocess.PIPE)
	stdout = p.communicate()[0].strip(); rc = p.returncode
	if rc!=0: raise Exception('non-zero exit status: %d' % str(sys.exit((rc,128-rc)[rc<0])))

	cores = 0
	memory = 0

	for line in stdout.split('\n'):
		#e.g.
		#Nodes=holy2a06104 CPU_IDs=10 Mem=4000
		#Nodes=holy2a13303 CPU_IDs=0-63 Mem=10000
		#Nodes=holy2a14208 CPU_IDs=15,28-29,31,35,45,59-60 Mem=800
		
		Nodes, CPU_IDs, Mem = line.strip().split()
		
		if Nodes.split('=')[1]==hostname:
			for x in CPU_IDs.split('=')[1].split(','):
				if '-' not in x:
					cores += 1
				else:
					start, end = x.split('-')
					cores += int(end) - int(start) + 1

			memory += int(Mem.split('=')[1]) * 1024

	return cores, memory


#--- host data queries

def getHostname():
	return socket.gethostname().split('.')[0]

#DELETE THIS
def getCPUUtilPercent():
	#running processes
	with open('/proc/loadavg','r') as f:
		used = f.read().split()[3].split('/')[0]
	
	with open('/proc/cpuinfo','r') as f:
		total = 0
		for l in f.readlines():
			if l.startswith('processor'):
				total += 1
	
	return float(used)/total * 100

def getCPU():
	#running processes
	with open('/proc/loadavg','r') as f:
		used = f.read().split()[3].split('/')[0]
	
	with open('/proc/cpuinfo','r') as f:
		total = 0
		for l in f.readlines():
			if l.startswith('processor'):
				total += 1
	
	return total, used

#DELETE THIS
def getMemUtilPercent():
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

		return float(used)/total * 100

def getMem():
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
	print getCPUUtilPercent()
	print getMemUtilPercent()
