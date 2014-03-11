# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""slurmmon node handling"""


import socket
import slurmmon
from slurmmon import config, util


class Node(util.LazyDict):
	"""a representation of a slurm compute node, mainly in scontrol context

	This is dict-like.
	Attributes are named to match scontrol's variables very closely.
	"""
	
	keys = [
		#=== scontrol data

		#
		'NodeName',
		#str

		'CPUTot',
		#int

		'CPUAlloc',
		#int

		'CPULoad',
		#float


		#=== os data

		'OS_Cores_total',
		#int

		'OS_Cores_Used',
		#int
		#number of running tasks, derived from the 4th colum of /proc/loadavg

		'OS_Memory_total',
		#int
		#in kB

		'OS_Memory_used',
		#int
		#in kB
		#does not count Buffers, Cached, and SwapCached


		#=== derived data

		'Cores_Wasted'
		#float
	]

	primary_key = 'NodeName'
	
	def load_data(self, keys=[]):
		for key in keys:
			if not self.has_key(key):
				#--- scontrol data

				self.load_data_from_scontrol_text(_yield_raw_scontrol_node_texts(util.get_hostname()).next())


				#--- os data

				if self['NodeName'] == util.get_hostname():
					self['OS_Cores_Total'] , self['OS_Cores_Used']  = util.get_cpu()
					self['OS_Memory_Total'], self['OS_Memory_Used'] = util.get_mem()
				else:
					self['OS_Cores_Total'] , self['OS_Cores_Used']  = None, None
					self['OS_Memory_Total'], self['OS_Memory_Used'] = None, None


				#--- derived

				if key=='Cores_Wasted':
					try:
						self['Cores_Wasted'] = float(self['CPUAlloc']) - self['CPULoad']
					except KeyError:
						self['Cores_Wasted'] = None

	def load_data_from_scontrol_text(self, scontroltext):
		"""Load data from a scontrol text.
		
		This does not respect the internal laziness setting -- everything 
		possible is loaded.
		"""
		try:
			for kv in scontroltext.split():
				if kv.startswith('NodeName'):
					self['NodeName'] = kv.split('=')[1]
				elif kv.startswith('CPUTot'):
					self['CPUTot'] = int(kv.split('=')[1])
				elif kv.startswith('CPULoad'):
					try:
						self['CPULoad'] = float(kv.split('=')[1])
					except ValueError:
						#often 'N/A'
						pass
				elif kv.startswith('CPUAlloc'):
					self['CPUAlloc'] = int(kv.split('=')[1])
				elif kv.startswith('AllocMem'):
					self['AllocMem_kB'] = slurmmon.AllocMem_to_kB(kv.split('=')[1])
				#elif kv.startswith('AllocMem'):
				#	memory = int(kv.split('=')[1]) * 1024
				#	if cores is not None:
				#		break

		except Exception, e:
			raise Exception("unable to parse scontrol node text [%r]: %r\n" % (scontroltext, e))


#--- node retrieval

def _yield_raw_scontrol_node_texts(NodeName=None):
	shv = ['scontrol', 'show', 'node', '--oneliner']
	if NodeName is not None:
		shv.append(NodeName)
	for line in util.runsh_i(shv):
		line = line.strip()
		if line!='': yield line

def get_nodes(filter=lambda j: True):
	for scontroltext in _yield_raw_scontrol_node_texts():
		n = Node()
		n.load_data_from_scontrol_text(scontroltext)
		if filter(n):
			yield n


if __name__=='__main__':
	n = Node(NodeName=util.get_hostname())

	print n['OS_Cores_Total']
	print n['OS_Cores_Used']
	print n['CPUAlloc']

	print n['OS_Memory_Total']
	print n['OS_Memory_Used']
	print n['AllocMem_kB']
