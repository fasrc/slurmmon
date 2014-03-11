#!/usr/bin/env python

# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""\
NAME
	whitespace_report - report poor utilization vs. allocation ratios

SYNOPSIS
	whitespace_report

DESCRIPTION
	n/a

OPTIONS
	-h, --help
		Print this help.

REQUIREMENTS
	n/a

BUGS/TODO
	n/a

AUTHOR
	Copyright (c) 2013-2014
	Harvard FAS Research Computing
"""


import sys, os, time, datetime, getopt
try:
	import slurmmon
except ImportError:
	#try adding where it exists if this is being run out of the source tree
	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'lib/python/site-packages')))
	import slurmmon
from slurmmon import config, jobs, nodes


def write_report(completed_jobs_cpu=True, live_nodes_cpu=True):
	#=== config

	#time range in which to look, if applicable (historical vs live data)
	range = datetime.timedelta(days=1)

	#the amount of entries to include in tables
	limit = 15

	state = 'COMPLETED'

	page_title = 'slurm whitespace -- poor allocation vs utilization'
	page_filename = 'index.html'
	jobs_dirname = 'jobs'



	#=== intro

	html = '<html>'
	html += '<head><title>%s</title>' % page_title
	html += '<style>\n%s\n</style>\n' % config.syntax_highlight_css
	html += '</head>'
	html += '<body>'

	html += config.whitespace_report_top_html()



	#=== completed jobs cpu

	if completed_jobs_cpu:
		html += '<h1>completed jobs</h1>'


		#--- get jobs

		endtime = datetime.datetime.now()
		starttime = endtime - range

		jobs_all = jobs.get_jobs(state=state, starttime=starttime, endtime=endtime, filter=config.filter_whitespace_cpu_job)

		
		#--- cpu wasters
		
		jobs_cpu_wasters = sorted(jobs_all, lambda j1, j2: -cmp(j1['CPU_Wasted'],j2['CPU_Wasted']))[:limit]

		#description
		html += '<h2>CPU wasters</h2>'
		html += '<h3>top CPU-wasteful %s jobs in last %s</h3>' % (state, range)
		html += '<table border="2" cellpadding="10">\n'

		#header
		html += '<tr>'
		for s in ('user', 'job', 'CPU days wasted', 'CPU efficiency', 'cores allocated', 'job script preview (click job link for full details)'):
			html += '<th>%s</th>' % s
		html += '</tr>'
		
		#entries
		for j in jobs_cpu_wasters:
			html += '<tr>'
			for i, x in enumerate((j['User'], j['JobID'], int(round(j['CPU_Wasted']/(60*60*24))), '%d%%' % int(round(j['CPU_Efficiency']*100)), j['NCPUS'], config.syntax_highlight(j['JobScriptPreview']))):
				if i==1:
					html += '<td><a href="jobs/%s.html">%s</a></td>' % (x, x)
				elif i==2:
					html += '<td style="text-align:right;"><strong>%s</strong></td>' % x
				elif i in (3, 4):
					html += '<td style="text-align:right;">%s</td>' % x
				else:
					html += '<td>%s</td>' % x
			html += '</tr>\n'

			with open(os.path.join(jobs_dirname, '%s.html' % j['JobID']), 'w') as f:
				f.write(jobs.job_html_report(j))
		
		#wrap-up
		html += '</table>'



	#=== live node state

	if live_nodes_cpu:
		html += '<h1>live node state</h1>'


		#--- get nodes

		nodes_all = nodes.get_nodes(filter=config.filter_whitespace_cpu_node)


		#--- cpu wasters

		nodes_cpu_wasters = sorted(nodes_all, lambda n1, n2: -cmp(n1['Cores_Wasted'],n2['Cores_Wasted']))[:limit]

		#description
		html += '<h2>CPU wasters</h2>'
		html += '<h3>top CPU-wasting nodes</h3>'
		html += '<table border="2" cellpadding="10">'
		
		#header
		html += '<tr>'
		for s in ('host', 'cores wasted', 'jobs'):
			html += '<th>%s</th>' % s
		html += '</tr>'

		#entries
		for n in nodes_cpu_wasters:
			html += '<tr>'
			for i, x in enumerate((n['NodeName'], n['Cores_Wasted'])):
				if i==1:
					html += '<td style="vertical-align:text-top;text-align:right;""><strong>%s</strong></td>' % x
				else:
					html += '<td style="vertical-align:text-top;">%s</td>' % x
			
			html += '<td style="vertical-align:text-top;">'
			for j in jobs.get_jobs_running_on_host(n['NodeName']):
				html += '<a href="jobs/%s.html">%s</a> %s / %s core(s) / %s node(s)<br />' % (j['JobID'], j['JobID'], j['User'], j['NCPUS'], j['NNodes'])
				with open(os.path.join(jobs_dirname, '%s.html' % j['JobID']), 'w') as f:
					f.write(jobs.job_html_report(j))
			html += '</td>'
			
			html += '</tr>'
		
		#wrap-up
		html += '</table>'



	#=== wrap-up
	
	html += '<br />page last updated: <strong>%s</strong><br />' % time.ctime()
	html += '</body>'
	html += '</html>'
	
	with open(page_filename,'w') as f:
		f.write(html)


if __name__=='__main__':
	try:
		opts, args = getopt.gnu_getopt(sys.argv[1:], 'h', ('help',))
	except getopt.GetoptError, e:
		sys.stderr.write("*** ERROR **** unable to process command line options: %s\n" % e)
		sys.exit(1)
	for opt, optarg in opts:
		if opt in ('-h', '--help'):
			sys.stdout.write(__doc__)
			sys.exit(0)

	write_report(
		completed_jobs_cpu=True,
		live_nodes_cpu=True,
	)
