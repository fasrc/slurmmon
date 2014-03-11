# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""general utilities"""


import os, select, subprocess, socket


#--- LazyDict

class LazyDict(dict):
	"""A dict-like structure for lazily pulling in data only when needed.
	
	A value of None means this has tried to get the data and it is not available or applicable.
	A KeyError means data retrieval has been blocked by LAZINESS_LOCKED or it's an invalid key.
	"""

	LAZINESS_LOCKED = 0
	#the data is considered complete -- no more queries will be issued

	LAZINESS_DATA_OPTIMIZED = 1
	#data size is minimized, by not pre-fetching or loading any extra attributes

	LAZINESS_QUERY_OPTIMIZED = 2
	#queries are minimized, by pre-fetching and loading as many attributes as possible per query

	#subclasses should override these
	keys = []
	primary_key = None

	def __init__(self, *arg, **kw):
		dict.__init__(self, *arg, **kw)

		self._laziness = self.LAZINESS_QUERY_OPTIMIZED

	def __str__(self):
		try:
			s = self[self.primary_key]
		except KeyError:
			s = '(empty)'
		return '<%s %s>' % (self.primary_key, s)

	def __getitem__(self, key):
		"""__getitem__
		
		This method itself is rather optimized for LAZINESS_QUERY_OPTIMIZED, as 
		it uses try/except instead of if/hasattr, which assumes success will be 
		more frequent than failure.
		"""
		try:
			return dict.__getitem__(self, key)
		except KeyError:
			if self._laziness == self.LAZINESS_LOCKED:
				raise
			else:
				self.load_data(keys=[key,])
				return dict.__getitem__(self, key)  #a key error at this point really means it's not available

	def set_laziness(self, laziness):
		"""Set this instance's laziness."""
		if laziness == self.LAZINESS_DATA_OPTIMIZED:
			raise NotImplementedError("LAZINESS_DATA_OPTIMIZED is not yet implemented")

		self._laziness = laziness
	
	def load_data(self, keys=[]):
		"""Load data.

		If keys is the empty list, this should load as much as possible, within 
		the laziness constraints.
		"""
		raise NotImplementedError()


#--- basic resource utilization

def get_hostname():
	"""Return the short hostname of the current host."""
	return socket.gethostname().split('.',1)[0]

def get_cpu():
	"""Return the CPU capacity and usage on this host.
	
	The returns a two-item list:
	[total number of cores (int), number of running tasks (int)]
	
	This is just a normal resource computation, independent of Slurm.
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

def get_mem():
	"""Return the memory capacity and usage on this host.
	
	This returns a two-item list:
	[total memory in kB (int), used memory in kB (int)]

	This is just a normal resource computation, independent of Slurm.
	The used memory does not count Buffers, Cached, and SwapCached.
	"""
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


#--- subprocess handling

def shquote(text):
	"""Return the given text as a single, safe string in sh code.

	Note that this leaves literal newlines alone; sh and bash are fine with 
	that, but other tools may require special handling.
	"""
	return "'%s'" % text.replace("'", r"'\''")

def sherrcheck(sh=None, stderr=None, returncode=None, verbose=True):
	"""Raise an exception if the parameters indicate an error.

	This raises an Exception if stderr is non-empty, even if returncode is 
	zero.  Set verbose to False to keep sh and stderr from appearing in the 
	Exception.
	"""
	if (returncode is not None and returncode!=0) or (stderr is not None and stderr!=''):
		msg = "shell code"
		if verbose: msg += " [%s]" % repr(sh)
		if returncode is not None:
			if returncode>=0:
				msg += " failed with exit status [%d]" % returncode
			else:
				msg += " killed by signal [%d]" % -returncode
		if stderr is not None:
			if verbose: msg += ", stderr is [%s]" % repr(stderr)
		raise Exception(msg)

def runsh(sh):
	"""Run shell code and return stdout.

	This raises an Exception if exit status is non-zero or stderr is non-empty.
	"""
	if type(sh)==type(''):
		shell=True
	else:
		shell=False
	p = subprocess.Popen(
		sh,
		shell=shell,
		stdin=open('/dev/null', 'r'),
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
	)
	stdout, stderr = p.communicate()
	sherrcheck(sh, stderr, p.returncode)
	return stdout

def runsh_i(sh):
	"""Run shell code and yield stdout lines.
	
	This raises an Exception if exit status is non-zero or stderr is non-empty. 
	Be sure to fully iterate this or you will probably leave orphans.
	"""
	BLOCK_SIZE = 4096
	if type(sh)==type(''):
		shell=True
	else:
		shell=False
	p = subprocess.Popen(
		sh,
		shell=shell,
		stdin=open('/dev/null', 'r'),
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
	)
	stdoutDone, stderrDone = False, False
	stdout = ''
	stderr = ''
	while not (stdoutDone and stderrDone):
		rfds, ignored, ignored2 = select.select([p.stdout.fileno(), p.stderr.fileno()], [], [])
		if p.stdout.fileno() in rfds:
			s = os.read(p.stdout.fileno(), BLOCK_SIZE)
			if s=='':
				stdoutDone = True
			else:
				i = 0
				j = s.find('\n')
				while j!=-1:
					yield stdout + s[i:j+1]
					stdout = ''
					i = j+1
					j = s.find('\n',i)
				stdout += s[i:]
		if p.stderr.fileno() in rfds:
			s = os.read(p.stderr.fileno(), BLOCK_SIZE)
			if s=='':
				stderrDone = True
			else:
				stderr += s
	if stdout!='':
		yield stdout
	sherrcheck(sh, stderr, p.wait())


if __name__=='__main__':
	pass
