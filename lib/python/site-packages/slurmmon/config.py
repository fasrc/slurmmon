# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""slurmmon configuration"""


import socket
from slurmmon import util
#(pygments import attempts are below)


#make it work out of the box both for FASRC and in general
FASRC = socket.gethostname().endswith('.rc.fas.harvard.edu')


#--- whitespace reporting

def filter_whitespace_cpu_job(job):
	"""Approve or veto a job as a cpu waster.
	
	This should return False if the job should be excluded from the report, or 
	True otherwise.  job is a slurmmon.jobs.Job.  Note that other slurmmon 
	configuration and functionality take care of the main job characteristics.  
	This is just an opportunity to account for users, partitions, etc. that are 
	incorrectly being flagged or otherwise have been given a "pass".
	"""
	if FASRC:
		return \
		job['Partition'] != 'gpgpu' and \
		job['User'] != 'dnelson'

	else:
		return True

def filter_whitespace_cpu_node(job):
	return True

def whitespace_report_top_html():
	"""Return extra html to include at the top of the whitespace report.
	
	For example, links to the allocation vs untilization plots from 
	slurmmon-ganglia.
	"""
	if FASRC:
		return """\
		<img src="http://status.rc.fas.harvard.edu/ganglia/holyoke_compute/graph.php?r=week&z=xlarge&g=holyoke_compute&s=by+name&mc=2&g=allocation_vs_utilization_cpu_report" />
		"""
	else:
		return ""


#--- misc

#syntax highlighting
try:
	from pygments import highlight
	from pygments.lexers import BashLexer
	from pygments.formatters import HtmlFormatter

	lexer = BashLexer()
	formatter = HtmlFormatter()

	syntax_highlight_css = formatter.get_style_defs('.highlight')
	def syntax_highlight(sh):
		return highlight(sh, lexer, formatter)
except ImportError:
	syntax_highlight_css = ''
	def syntax_highlight(sh):
		return '<pre>%s</pre>' % sh

def get_job_script(JobID):
	"""Return the job payload script, or raise NotImplemented if unavailable."""
	if FASRC:
		#at FASRC, we have our slurmctld prolog store the script in a database
		shv = ['mysql', 'slurm_jobscripts', '-BNr', '-e', 'select script from jobscripts where id_job = %d;' % int(JobID)]
		return util.runsh(shv)
	else:
		raise NotImplementedError("job script retrieval requires implementation in config.py")

def job_script_line_is_interesting(line, job=None):
	"""Return whether or not the line of text is worthwhile as a job script preview.
	
	The given line will be stripped of leading and trailing whitespace and will 
	not be the empty string or a comment.
	"""
	for s in (
		'wait',
		'echo',
		'cd',
		'mkdir', '/bin/mkdir',
		'cp', '/bin/cp',
		'rm', '/bin/rm',
		'mv', '/bin/mv',
		'rsync', '/usr/bin/rsync',
		'tar', '/bin/tar',
		'gzip', '/bin/gzip',
		):
		if line==s or line.startswith(s+' '):
			return False
	return True
