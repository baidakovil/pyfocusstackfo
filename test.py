# pyfocusstackfo — Utility to reallocate photos taken for focus stacking into folders.
# Copyright (C) 2023 Ilia Baidakov <baidakovil@gmail.com>

# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <https://www.gnu.org/licenses/>.
"""This module provide simple tests units."""
import contextlib
import io
import os
import shutil
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import pyfocusstackfo

root_dir = os.path.dirname(__file__)
test_dir = 'test'
temp_dir = 'tempjpg'

answers_1 = iter([os.path.join(root_dir, test_dir), temp_dir])
answers_2 = iter([os.path.join(root_dir, test_dir), temp_dir])
answers_3 = iter([os.path.join(root_dir, test_dir), temp_dir])
answers_4 = iter([os.path.join(root_dir, test_dir), temp_dir])
answers_5 = iter([os.path.join(root_dir, test_dir), temp_dir])
answers_6 = iter(['', os.path.join(test_dir, temp_dir)])
answers_7 = iter(['', test_dir])


class Test(unittest.TestCase):
    """Unit test Test Case. All cases are with:
    MINSTACKLEN = 5, MAXDELTA = 2, BIG_STRANGE_STACKLEN = 10"""

    @patch('builtins.input', lambda msg: next(answers_1))
    def test_1(self):
        """
        This is normal case with 97 files And 9 stacks.
        """
        with ZipFile(os.path.join(root_dir, test_dir, 'test_97f.zip'), 'r') as myzip:
            myzip.extractall(path=os.path.join(root_dir, test_dir, temp_dir))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pyfocusstackfo.main()
        self.assertIn("Got 97 timestamps in JPGs", buf.getvalue())
        self.assertIn("9 folders created\n64 files moved", buf.getvalue())
        shutil.rmtree(os.path.join(root_dir, test_dir, temp_dir))

    @patch('builtins.input', lambda msg: next(answers_2))
    def test_2(self):
        """
        This is the test where no stacks in jpgs across 33 files.
        """
        with ZipFile(os.path.join(root_dir, test_dir, 'test_no_st.zip'), 'r') as myzip:
            myzip.extractall(path=os.path.join(root_dir, test_dir, temp_dir))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            with self.assertRaises(SystemExit):
                pyfocusstackfo.main()
        self.assertIn("Got 33 timestamps in JPGs", buf.getvalue())
        self.assertIn("No stacks here! Exit", buf.getvalue())
        shutil.rmtree(os.path.join(root_dir, test_dir, temp_dir))

    @patch('builtins.input', lambda msg: next(answers_3))
    def test_3(self):
        """
        This is the test with big stack with qty files more than BIG_STRANGE_STACKLEN.
        """
        with ZipFile(
            os.path.join(root_dir, test_dir, 'test_strange_big.zip'), 'r'
        ) as myzip:
            myzip.extractall(path=os.path.join(root_dir, test_dir, temp_dir))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pyfocusstackfo.main()
        self.assertIn("Strange long stack (16) elements", buf.getvalue())
        self.assertIn("1 folders created\n16 files moved", buf.getvalue())
        shutil.rmtree(os.path.join(root_dir, test_dir, temp_dir))

    @patch('builtins.input', lambda msg: next(answers_4))
    def test_4(self):
        """
        This test with stacked files in the end of file list.
        """
        with ZipFile(
            os.path.join(root_dir, test_dir, 'test_st_in_end.zip'), 'r'
        ) as myzip:
            myzip.extractall(path=os.path.join(root_dir, test_dir, temp_dir))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pyfocusstackfo.main()
        self.assertIn("Got 22 timestamps in JPGs", buf.getvalue())
        self.assertIn("Stack size  5 files: 1 stacks", buf.getvalue())
        self.assertIn("1 folders created\n5 files moved", buf.getvalue())
        shutil.rmtree(os.path.join(root_dir, test_dir, temp_dir))

    @patch('builtins.input', lambda msg: next(answers_5))
    def test_5(self):
        """
        This test with stacked files in the beginning of file list.
        """
        with ZipFile(
            os.path.join(root_dir, test_dir, 'test_st_in_begin.zip'), 'r'
        ) as myzip:
            myzip.extractall(path=os.path.join(root_dir, test_dir, temp_dir))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pyfocusstackfo.main()
        self.assertIn(
            "Got 9 timestamps in JPGs\nFROM: 2023-12-02 13:30:39", buf.getvalue()
        )
        self.assertIn("1 folders created\n5 files moved", buf.getvalue())
        shutil.rmtree(os.path.join(root_dir, test_dir, temp_dir))

    @patch('builtins.input', lambda msg: next(answers_6))
    def test_6(self):
        """
        This tests empty input on first prompt on data of test_1
        """
        with ZipFile(os.path.join(root_dir, test_dir, 'test_97f.zip'), 'r') as myzip:
            myzip.extractall(path=os.path.join(root_dir, test_dir, temp_dir))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pyfocusstackfo.main()
        self.assertIn("Got 97 timestamps in JPGs", buf.getvalue())
        self.assertIn("9 folders created\n64 files moved", buf.getvalue())
        shutil.rmtree(os.path.join(root_dir, test_dir, temp_dir))

    @patch('builtins.input', lambda msg: next(answers_7))
    def test_7(self):
        """
        This test case with no files in folder.
        """
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            with self.assertRaises(SystemExit):
                pyfocusstackfo.main()
        self.assertIn("No JPG files in folder! Exit", buf.getvalue())


if __name__ == '__main__':
    unittest.main()