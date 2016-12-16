An application to record a user's Folding@Home user stats over time.

Warning: This script is meant to be run hourly, as F@H has explicitly
stated that queries of this data should not exceed 24 times in a day (hourly).

Example usage:
  python folding_stats_recorder.py --username='PS3EdOlkkola' 
  	--record_location=/home/$USER/fahuserdata.csv

Defaults: 'record_location' defaults to the above. 'username' defaults to 
'anonymous'.

Note: On successive runs script will append data to the csv if the same 
record_location is specified.