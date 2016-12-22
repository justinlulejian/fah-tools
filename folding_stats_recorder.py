#!/usr/bin/env python
"""An application to record a user's Folding@Home user stats over time.

Warning: This script is only meant to be run hourly, as F@H has explicitly
  stated that queries of this data should not exceed 24 times in a day (hourly).

Example usage:
  folding_stats_recorder --username='PS3EdOlkkola' --record_location=/home/john
    --userdata_location='http://fah-web.stanford.edu/daily_user_summary.txt.bz2'

Note: On successive runs script will append data if the same record_location is
  specified.
"""
# pylint: disable=fixme
# TODO(jlulejian): unit tests.

import bz2
import click
import collections
import csv
import datetime
import getpass
import logging
import os
import requests
import sys


def retrieve_user_data_file(user_data_url):
  """Send an HTTP request to get the bz2 file containing user (donator data).

  Args:
    user_data_url: A string of URL where the user data file is located.

	Returns:
    The binary content of the user data file retrieved.
  """
  logging.debug('Retrieving user data file from: %s', user_data_url)
  return requests.get(user_data_url).content


def decompress_userdata_to_list(user_data_content):
  """Decompress the user data file into a string, and convert to a list.

  Args:
    user_data_content: The binary content of the file.

  Returns:
    A list containing each line of the file as an element. E.g.
      ['name    newcredit       sum(total)      team', 'PS3EdOlkkola
        11650611552     242449  224497', ...]
  """
  logging.debug('Decompressing user data file to allow searching.')
  return bz2.decompress(user_data_content).splitlines()


def find_specific_user_data(user_data_rows, target_name):
  """Given the rows of the user data file, find the targeted user's data.

  Args:
    user_data_rows: A list containing each line of the file as an element. E.g.
      ['name    newcredit       sum(total)      team', 'PS3EdOlkkola
        11650611552     242449  224497', ...]
    target_name: A string of the donator username to search for.

  Returns:
    user_data_tuple: A namedtuple object containing the data for the user. E.g.
      user_data_tuple.username would return 'Justin_N_Lulejian'.

  """
  user_data_tuple = (
    collections.namedtuple(
      'user_data_tuple',
      ['username', 'new_credits', 'sum_workunits', 'team_num'],
       verbose=False))
  # TODO(jlulejian): Data appears ordered by point rank. See if can devise a
  # a more efficient way to search data for user_name.
  # First two rows are date and header col vals.
  for user_data_row in user_data_rows[2:]:
    user_name = user_data_row.split(None, 1)[0]
    if user_name == target_name:
      logging.debug('Found user data for: %s', target_name)
      return user_data_tuple(*user_data_row.split())
  raise click.BadParameter(
    'F@H donator username could not be found, please specify an existing '
    'name.')


def record_user_data_to_csv(user_data, record_loc):
  """Record user data to a CSV file, creates the file if it doesn't exist yet.

  E.g.
  time,username,new_credits,sum_workunits,team_num
  12/15/2016 22:26,Justin_N_Lulejian,13224707,2291,0
  12/15/2016 23:26,Justin_N_Lulejian,13226388,2292,0

  Args:
    user_data: A namedtuple object containing the data for the user. Should have
      the following attributes: 'username', 'new_credits', 'sum_workunits',
      'team_num'
    record_loc: A string of that path to a desired filename to record the CSV
    of F@H user data.
  """
  fieldnames = ['time'] + list(user_data._fields)  # pylint: disable=protected-access
  # TODO(justinlulejian): Calculate useful metrics (e.g. #/% diff values) since
  # last entry.
  user_data_row_dict = {
  'time': datetime.datetime.now().strftime('%m/%d/%Y %H:%M'),
  'username': user_data.username, 'new_credits': user_data.new_credits,
  'sum_workunits': user_data.sum_workunits,
  'team_num': user_data.team_num}
  if os.path.isfile(record_loc):
    logging.debug('File: %s exists, appending to file.', record_loc)
    with open(record_loc, 'a+b') as record_file:
      user_data_writer = csv.DictWriter(record_file, fieldnames=fieldnames)
      # TODO(justinlulejian): Dynamically generate keys of dict from fieldnames.
      # TODO(justinlulejian): Figure out how to deduplicate the user_data_writer
      # lines.
      user_data_writer.writerow(user_data_row_dict)
  else:
    logging.debug('File: %s does not exist, creating.', record_loc)
    with open(record_loc, 'w+b') as record_file:
      user_data_writer = csv.DictWriter(record_file, fieldnames=fieldnames)
      user_data_writer.writeheader()
      user_data_writer.writerow(user_data_row_dict)


def validate_record_location(*args):
  """Confirm location specified for record data is writable."""
  value = args[2]
  if not os.access(value, os.W_OK):
    raise click.BadParameter('Could not obtain write access to %s.' % value)
  return value


def validate_fah_username(*args):
  """Ensure a username was specified."""
  value = args[2]
  param = args[1]
  if not value:
    raise click.BadParameter('No %s was provided' % param.human_readable_name)
  return value


@click.command()
@click.option(
  '--record_location',
   default='/home/%s/%s' % (getpass.getuser(), 'fahuserdata.csv'),
   help='Where to store CSV of user data.', callback=validate_record_location,
   show_default=True)
@click.option(
  '--userdata_location',
   default='http://fah-web.stanford.edu/daily_user_summary.txt.bz2',
   help='Where to store CSV of user data.', show_default=True)
@click.option(
  '--username',
   default=None, help='The donator username to get stats for.',
   callback=validate_fah_username, show_default=True)
@click.option(
  '--verbose',
   default=False,
   help='Show more verbose logging output.', show_default=True)
def record_folding_at_home_stats(
  record_location, userdata_location, username, verbose):
  """Primary function for gathering the user data and recording it.

  Args:
  record_location: A string of that path to a desired filename to record the CSV
    of F@H user data.
  userdata_location: A string of the URL where the bz2 files containing F@H user
    data is located.
  username: A string of the F@H donator username.
  verbose: A boolean to show debug and above logging. Otherwise, only info and
    above shown.
  """
  if verbose:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  else:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

  logging.info('Retrieving user data.')
  all_user_data = (
    decompress_userdata_to_list(
      retrieve_user_data_file(userdata_location)))
  logging.info('Searching for user: %s in user data.', username)
  target_user_data = (
    find_specific_user_data(all_user_data, username.encode('utf8')))
  logging.info('Found user data for user: %s.', username)
  record_user_data_to_csv(target_user_data, record_location)
  logging.info('Recorded data for user to: %s.', record_location)


if __name__ == '__main__':
  # Click provides arguments to function through decorators.
  record_folding_at_home_stats()  # pylint: disable=no-value-for-parameter
