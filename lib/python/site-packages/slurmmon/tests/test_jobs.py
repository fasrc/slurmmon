# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""unit tests"""

import sys, os
import unittest, mock

try:
	import slurmmon
except ImportError:
	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
	import slurmmon
from slurmmon import jobs as j


class SacctTestCase(unittest.TestCase):
	def test_sacct(self):
		with mock.patch('slurmmon.jobs._yield_raw_sacct_job_lines') as m:
			#sacct --allusers --noheader --parsable2 --format User,JobID,JobName,State,Partition,NCPUS,NNodes,CPUTime,TotalCPU,UserCPU,SystemCPU,ReqMem,MaxRSS,Start,End,NodeList --state COMPLETED --starttime 04/30-00:00:00 --endtime 05/01-23:59:59 > _mock_data/sacct_parsable_day.out

			m.return_value = open(os.path.join(os.path.dirname(__file__), '_mock_data', 'sacct_parsable_day.out'))

			for x in j._yield_raw_sacct_job_text_blocks():
				print x


if __name__=='__main__':
	unittest.main()
