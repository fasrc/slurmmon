# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""slurmmon job handling"""


import slurmmon
from slurmmon import config, util


#sacct format; you can change _sacct_format_readable at will, but changing _sacct_format_parsable will break the code
_sacct_format_parsable = 'User    ,JobID    ,JobName   ,State,Partition   ,NCPUS,NNodes,CPUTime   ,TotalCPU   ,UserCPU   ,SystemCPU   ,ReqMem,MaxRSS,Start,End,NodeList'.replace(' ','')
_sacct_format_readable = 'User%-12,JobID%-15,JobName%20,State,Partition%18,NCPUS,NNodes,CPUTime%13,TotalCPU%13,UserCPU%13,SystemCPU%13,ReqMem,MaxRSS,Start,End,NodeList%-500'.replace(' ','')


#--- data structures

class Job(util.LazyDict):
	"""a representation of a slurm job, mainly in sacct context

	Attributes are named to match sacct's variables very closely.
	Plus, some derived attributes are added, and some are clarified or made consistent, e.g. MaxRSS becomes MaxRSS_kB.
	It only represents overall jobs, not steps.
	For variables that are step-specific, the value here for the job is the maximum for any given step.

	Currently, this is all geared towards getting data about completed jobs.
	In particular, it is not meant for job control.
	"""

	keys = [
		#=== data from sacct

		#--- info from main job account line

		'JobID',
		#str, but currently always representing an integer (no ".STEP_ID")
		
		'User',
		#str
		
		'JobName',
		#str
		
		'State',
		#str
		
		'Partition',
		#str
		
		'NCPUS',
		#int
		
		'NNodes',
		#int

		'CPUTime',
		#seconds, float
		
		'TotalCPU',
		#seconds, float
		
		'UserCPU',
		#seconds, float
		
		'SystemCPU',
		#seconds, float

		#--- max of any main job account line or any steps

		'MaxRSS_kB',
		#bytes in kB, int
		
		'ReqMem_bytes_per_node',
		#bytes, int, or None if not used
		
		'ReqMem_bytes_per_core',
		#bytes, int, or None if not used


		#=== derived data

		'ReqMem_bytes_total',
		#bytes, int, or None if not used
		#a computation combining the appropriate request per resource and number of resources

		'CPU_Efficiency',
		#float, should be in the range [0.0,1.0), but nothing guarantees that
		
		'CPU_Wasted',
		#seconds, float


		#=== other
		
		'JobScript',
		#the text of the job payload script.

		'JobScriptPreview',
		#a one-line, (hopefully) representative preview of the JobScript.

		'SacctReport',
		#an sacct report, formatted for humans and containing headers
	]

	primary_key = 'JobID'
	
	def load_data(self, keys=[]):
		for key in keys:
			if not self.has_key(key):
				#--- sacct data

				#(not implemented yet)


				#--- other one-off queries

				if key == 'JobScript':
					try:
						self['JobScript'] = config.get_job_script(self['JobID'])
					except NotImplementedError:
						self['JobScript'] = None
					
				elif key == 'SacctReport':
					shv = ['sacct', '--format', _sacct_format_readable, '-j', self['JobID']]
					self['SacctReport'] = util.runsh(shv).rstrip()


				#--- derived

				if key == 'ReqMem_bytes_total':
					if self.has_key('ReqMem_bytes_per_core') and self['ReqMem_bytes_per_core'] is not None:
						if self.has_key('ReqMem_bytes_per_node') and self['ReqMem_bytes_per_node'] is not None:
							raise Exception("both memory-per-node and memory-per-core used, and this cannot handle that")
						self['ReqMem_bytes_total'] = self['ReqMem_bytes_per_core'] * self['NCPUS']
					elif self.has_key('ReqMem_bytes_per_node') and self['ReqMem_bytes_per_node'] is not None:
						self['ReqMem_bytes_total'] = self['ReqMem_bytes_per_node'] * self['NNodes']
					else:
						self['ReqMem_bytes_total'] = None

				elif key == 'CPU_Efficiency':
					if self.has_key('TotalCPU') and self['TotalCPU']!=0 and \
						self.has_key('CPUTime') and self['CPUTime']!=0:
						self['CPU_Efficiency'] = float(self['TotalCPU'])/self['CPUTime']
					else:
						self['CPU_Efficiency'] = None

				elif key == 'CPU_Wasted':
					if self.has_key('TotalCPU') and self.has_key('CPUTime'):
						self['CPU_Wasted'] = max(self['CPUTime'] - self['TotalCPU'], 0)
					else:
						self['CPU_Efficiency'] = None

				elif key == 'JobScriptPreview':
					try:
						self['JobScriptPreview'] = slurmmon.job_script_preview(self['JobScript'], self)
					except KeyError:
						self['JobScriptPreview'] = None

	def load_data_from_sacct_text_block(self, saccttext):
		"""Load data from a multi-line, parsable sacct block of text.
		
		This does not respect the internal laziness setting -- everything 
		possible is loaded.
		"""
		try:
			for line in saccttext.split('\n'):
				line = line.strip()
				if line=='':
					continue

				User,JobID,JobName,State,Partition,NCPUS,NNodes,CPUTime,TotalCPU,UserCPU,SystemCPU,ReqMem,MaxRSS,Start,End,NodeList = line.split('|')
				
				#convert JobID to just the base id, and set an extra JobStep variable with the step key
				JobStep = ''
				if '.' in JobID:
					JobID, JobStep = JobID.split('.')
		
				if JobStep=='':
					#this is the main job line

					#these things should be present in this main line and better than any data in the job steps
					self['JobID'] = JobID
					self['User'] = User
					self['JobName'] = JobName
					self['State'] = State
					self['Partition'] = Partition
					self['NCPUS'] = int(NCPUS)
					self['NNodes'] = int(NNodes)
					self['CPUTime'] = slurmmon.slurmtime_to_seconds(CPUTime)
					self['TotalCPU'] = slurmmon.slurmtime_to_seconds(TotalCPU)
					self['UserCPU'] = slurmmon.slurmtime_to_seconds(UserCPU)
					self['SystemCPU'] = slurmmon.slurmtime_to_seconds(SystemCPU)

					continue
				else:
					#these are the job steps after the main entry

					#ReqMem
					if ReqMem.endswith('Mn'):
						ReqMem_bytes_per_node = int(ReqMem[:-2])*1024**2
						if self.has_key('ReqMem_bytes_per_node'):
							ReqMem_bytes_per_node = max(self['ReqMem_bytes_per_node'], ReqMem_bytes_per_node)
						self['ReqMem_bytes_per_node'] = ReqMem_bytes_per_node
						self['ReqMem_bytes_per_core'] = None
					elif ReqMem.endswith('Mc'):
						ReqMem_bytes_per_core = int(ReqMem[:-2])*1024**2
						if self.has_key('ReqMem_bytes_per_core'):
							ReqMem_bytes_per_core = max(self['ReqMem_bytes_per_core'], ReqMem_bytes_per_core)
						self['ReqMem_bytes_per_node'] = None
						self['ReqMem_bytes_per_core'] = ReqMem_bytes_per_core
						
					#MaxRSS
					MaxRSS_kB = slurmmon.MaxRSS_to_kB(MaxRSS)
					if self.has_key('MaxRSS_kB'):
						MaxRSS_kB = max(self['MaxRSS_kB'], MaxRSS_kB)
					self['MaxRSS_kB'] = MaxRSS_kB

		except Exception, e:
			raise Exception("unable to parse sacct job text [%r]: %r\n" % (saccttext, e))


#--- job retrieval

def _yield_raw_sacct_job_text_blocks(state='COMPLETED', starttime=None, endtime=None):
	"""Yields multi-line strings of sacct text for each job.

	state can, in theory, be any string accepted by sacct --state.
	However, this has only been tested with state='COMPLETED' -- there will probably be ValueErrors with anything else.
	
	starttime and endtime should be datetime objects.
	"""
	
	shv = ['sacct', '--allusers', '--noheader', '--parsable2', '--format', _sacct_format_parsable]

	if state is not None:
		shv.extend(['--state', state])
	if starttime is not None:
		shv.extend(['--starttime', starttime.strftime('%m/%d-%H:%M')])
	if endtime is not None:
		shv.extend(['--endtime', endtime.strftime('%m/%d-%H:%M')])
	
	#this will be the text that's yielded
	text = ''

	#for line in open('_fake_data/sacct_alljobs_parsable.out').readlines():
	for line in util.runsh_i(shv):
		if line.startswith('|'):
			text += line
		else:
			if text!='': yield text
			text = line
	
	if text!='':
		yield text

def get_jobs(state='COMPLETED', starttime=None, endtime=None, filter=lambda j: True):
	"""Yield Job objects that match the given parameters."""
	for saccttext in _yield_raw_sacct_job_text_blocks(state=state, starttime=starttime, endtime=endtime):
		j = Job()
		j.load_data_from_sacct_text_block(saccttext)
		if filter(j):
			yield j

def get_jobs_running_on_host(hostname):
	"""Return jobs running on the given host."""
	shv = ['squeue', '-o', '%A %u %C %D', '--noheader', '-w', hostname]
	stdout = util.runsh(shv).strip()
	for line in stdout.split('\n'):
		line = line.strip()
		try:
			JobID, User, NCPUS, NNodes = line.split()
			
			j = Job()
			j['JobID'] = JobID
			j['User'] = User
			j['NCPUS'] = NCPUS
			j['NNodes'] = NNodes

			yield j

		except Exception, e:
			sys.stderr.write("*** ERROR *** unable to parse squeue job text [%r]: %s\n" % (line, e))


#--- utilities

def job_html_report(job, syntax_highlight_css=config.syntax_highlight_css, syntax_highlight=config.syntax_highlight):
	"""Return a full html page report on the given job."""
	html = '<html>'
	html += '<head><title>%s</title>' % job['JobID']
	html += '<style>\n%s\n</style>' % syntax_highlight_css
	html += '</head>'
	html += '<body><h1>%s</h1><hr />' % job['JobID']
	html += config.syntax_highlight(job['JobScript'])
	html += '<br /><hr /><br />'
	html += '\n<pre>%s</pre>\n' % job['SacctReport']
	html += '<br />'
	html += '</body></html>'
	return html
