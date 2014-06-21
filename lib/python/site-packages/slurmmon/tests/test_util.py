# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""unit tests"""

import sys, os
import unittest

try:
	import slurmmon
except ImportError:
	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
	import slurmmon
from slurmmon import util as u


class ShTestCase(unittest.TestCase):
	funky_string = r"""foo'bar "more" \' \" \n zzz"""
	funky_string_quoted = r"""'foo'\''bar "more" \'\'' \" \n zzz'"""

	#runsh() focused
	def test_runsh_string(self):
		"""That runsh() works on sh code as a string."""
		self.assertEqual(
			u.runsh('echo foo'),
			'foo\n',
		)
	def test_runsh_list(self):
		"""That runsh() works on an argv list."""
		self.assertEqual(
			u.runsh(['echo','foo']),
			'foo\n',
		)

	#runsh_i() focused
	def test_runsh_i_string(self):
		"""That runsh_i() works on sh code as a string."""
		self.assertEqual(
			[line for line in u.runsh_i("echo -e 'foo\nbar'")],
			['foo\n', 'bar\n'],
		)
	def test_runsh_list(self):
		"""That runsh_i() works on an argv list."""
		self.assertEqual(
			[line for line in u.runsh_i(['echo', '-e', 'foo\nbar'])],
			['foo\n', 'bar\n'],
		)

	#shquote() focused
	def test_shquote(self):
		"""That quoting with shquote() == quoting manually."""
		self.assertEqual(
			u.shquote(ShTestCase.funky_string),
			ShTestCase.funky_string_quoted
		)
	def test_shquote_runsh(self):
		"""That echo is identity for a funky_string."""
		self.assertEqual(
			u.runsh('echo -n %s' % u.shquote(ShTestCase.funky_string)),
			ShTestCase.funky_string
		)
	
	#sherrcheck() focused
	def test_sherrcheck_status(self):
		self.assertRaises(Exception, u.runsh, ['false'])
	def test_sherrcheck_stderr(self):
		self.assertRaises(Exception, u.runsh, 'echo foo >&2')


if __name__=='__main__':
	unittest.main()
