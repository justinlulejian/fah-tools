#!/usr/bin/env python
"""Unit tests for folding_stats_recorder.py

Note: Tests currently rely on ability to access a copy of
  daily_user_summary.txt.bz2 at http://127.0.0.1. This can be accomplished with
  'python -m SimpleHTTPServer 80' when in the testdata subdirectory.

"""
# pylint: disable=fixme

# Standard imports.
import unittest

# Non-standard imports.
import click
import folding_stats_recorder
import freezegun
import mock

# TODO(justinlulejian): Utilize proper click tests. E.g. https://goo.gl/qpvU37
class FoldingStatsRecorderTestMethods(unittest.TestCase):
  """Testing methods for the folding stats recorder."""

  @freezegun.freeze_time('2016-01-14 12:01')
  @mock.patch('os.path.getsize')
  @mock.patch('folding_stats_recorder.open')
  @mock.patch('csv.DictWriter.writerow')
  def test_fah_user_data_is_recorded(
      self, mock_csv_write, mock_open, mock_os):
    """Test if the full recording workflow succeeds."""
    fake_file_data = (
        'time,username,new_credits,sum_workunits,team_num\n12/31/2016 18:33,'
        'Justin_N_Lulejian,16781810,2434,0')
    mock_open.read(fake_file_data)
    mock_os.return_value = 1
    folding_stats_recorder.record_folding_at_home_stats(
        'testfile.csv', 'http://127.0.0.1/daily_user_summary.txt.bz2',
        'Justin_N_Lulejian', True)

    expected_row_data = {
        'username': 'Justin_N_Lulejian', 'new_credits': '16781810',
        'sum_workunits': '2434', 'team_num': '0', 'time': '01/14/2016 12:01'}
    mock_csv_write.assert_called_once_with(expected_row_data)

  def test_validate_username(self):
    """Test that username inputs are validated."""
    # Username does not exist in user data.
    with self.assertRaises(click.BadParameter):
          'testfile', 'http://127.0.0.1/daily_user_summary.txt.bz2',
          'nonexistent_user', False)

  def test_validate_userdata_loc(self):
    """Test that an inaccesssible user data location is handled."""
    # URL appears invalid/inaccessible. Scripts exits since fatal.
    with self.assertRaises(SystemExit):
      folding_stats_recorder.record_folding_at_home_stats(
          'testfile', 'totallyinvalidURL', 'username', False)
    with self.assertRaises(SystemExit):
      folding_stats_recorder.record_folding_at_home_stats(
          'testfile', 'http://urlwithnohost', 'username', False)
    with self.assertRaises(SystemExit):
      folding_stats_recorder.record_folding_at_home_stats(
          'testfile', 'urlwithnoschema.com', 'username', False)
    with self.assertRaises(SystemExit):
      folding_stats_recorder.record_folding_at_home_stats(
          'testfile', 'http://127.0.0.1/nonexistent_file', 'username', False)

  def test_validate_record_file(self):
    """Test that record file errors are handled."""
    # record_file inaccessible.
    with self.assertRaises(click.BadParameter):
      # Couldn't get mock.mock_open() (e.g. https://goo.gl/biJcgj) to work.
      with mock.patch('folding_stats_recorder.open', side_effect=IOError()):
            'inaccessible_file', 'testURL', 'testuser', False)

  @mock.patch('os.path.getsize')
  @mock.patch('folding_stats_recorder.open')
  @mock.patch('csv.DictWriter.writerow')
  @mock.patch('csv.DictWriter.writeheader')
  def test_record_file_append_row(
      self, mock_csv_head, mock_csv_write, mock_open, mock_os):
    """Test subsequent runs of recorder append data to existing file."""
    fake_file_data = (
        'time,username,new_credits,sum_workunits,team_num\n12/31/2016 18:33,'
        'Justin_N_Lulejian,16781810,2434,0')
    mock_open.read(fake_file_data)
    mock_os.return_value = 1
    folding_stats_recorder.record_folding_at_home_stats(
        'testfile.csv', 'http://127.0.0.1/daily_user_summary.txt.bz2',
        'Justin_N_Lulejian', True)
    mock_csv_head.assert_not_called()
    mock_csv_write.assert_called_once()


  def tearDown(self):
    mock.patch.stopall()
    # self.http_daemon.shutdown()

if __name__ == '__main__':
  unittest.main()
