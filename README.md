An application to record a user's Folding@Home user stats over time.

Warning: This script is only meant to be run hourly, as F@H has explicitly
  stated that queries of this data should not exceed 24 times in a day (hourly).

Example usage:
  folding_stats_recorder --username='PS3EdOlkkola' --record_file=/home/john
    --userdata_location='http://fah-web.stanford.edu/daily_user_summary.txt.bz2'

Requires: 
click Python library (http://click.pocoo.org/5/): pip install click
requests Python library (http://docs.python-requests.org/): pip install requests

Note: On successive runs script will append data if the same record_location is
  specified.