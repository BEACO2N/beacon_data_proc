"""Computes minute averages from the beacon data.

Usage:
    python min_avg.py ~/folder/to/node/for/example/exploratorium1

This outputs the results to stdout, so if you want to save the results to a file, do:
    python min_avg.py ~/folder/to/node/for/example/exploratorium1 > output_file
"""
from __future__ import print_function
import csv
import datetime
import sys
import os

import pdb

from datetime import (
    datetime,
    timedelta,
)
 
NUM_COLUMNS_WITHOUT_DATE = 21
def main(lastdayofmonth,temporary_directory):
    
    def average_and_output_bucket(bucket, date):
        if bucket == []:
            averaged_row = None
        else:                     
            averaged_row = []
            for j in range(len(bucket[0]) - 1):
                try:
                    col_values = [float(r[j]) for r in bucket if float(r[j]) != -999]
                except ValueError:
                    sys.stderr.write("Error computing avg for col %d in: %s\n" % (j, str(bucket)))
                    col_values = None

                if col_values:
                    col_avg = round(sum(col_values)/float(len(col_values)), 4)
                else:
                    col_avg = None
                averaged_row.append(col_avg)

        if averaged_row is None:
            master_list.append([''] * NUM_COLUMNS_WITHOUT_DATE + [str(date.replace(second=30))])
            
        else:
            master_list.append([str(s) for s in averaged_row] + [str(date.replace(second=30))])

    def fill_in_missing_minutes(start, end):
        """Helper function to fill in wholes in the data."""
        while start < end:
            average_and_output_bucket([], start)
            start += timedelta(minutes=1)

    def process_hour_file(hour_start, hour_path):
        # Parse the CSV and bucket as we go!
        curr_date_bucket = hour_start
        curr_bucket = []
        with open(hour_path, 'rU') as csv_file:
            # Read and drop NULL bytes
            csv_reader = csv.reader((line.replace('\0', '') for line in csv_file), 
                                    delimiter=',')
            i=-1
            for i, row in enumerate(csv_reader):
                if len(row) != NUM_COLUMNS_WITHOUT_DATE + 1:
                    sys.stderr.write("Skipping row that doesn't have the right columns! %d : %r\n" % (i, row))
                    continue

                try:
                    date = datetime.strptime(row[-1], "%Y-%m-%d %H:%M:%S")
                    date_bucket = date.replace(second=0)

                    if date_bucket != curr_date_bucket and curr_bucket:
                        # This is a new bucket (e.g. we were in the 0th minute, now
                        # we're in the 1st or 4th, etc). As a result, average the
                        # bucket we were working on (e.g. the 0th), then fill in any
                        # holes between that bucket and the next bucket.
                        average_and_output_bucket(curr_bucket, curr_date_bucket)
                        fill_in_missing_minutes(
                            curr_date_bucket + timedelta(minutes=1), 
                            date_bucket
                        )
                        curr_bucket = []
                    
                    elif not curr_bucket:
                        # If this is a new bucket but there were no rows in the
                        # previous bucket, there are rows missing from the beginning of
                        # the file.
                        fill_in_missing_minutes(curr_date_bucket, date_bucket)

                    curr_date_bucket = date_bucket
                    curr_bucket.append(row)

                except ValueError:
                    print ("Hit that ValueError")
                    continue

            sys.stderr.write("Processed %d rows of %r.\n" % (i + 1, hour_path))

        # Lastly, finish out the current bucket we're working on and 
        # pad the end of the hour as necessary.
        average_and_output_bucket(curr_bucket, curr_date_bucket)
        fill_in_missing_minutes(
            curr_date_bucket + timedelta(minutes=1),
            hour_start + timedelta(hours=1),
        )

    # Specifies when we expect the data to start and end. The script
    # will ensure that there are exactly as many lines in the resulting
    # output as there are minutes between the start and end date. 
    list_of_temporary_folders = sorted(os.listdir(temporary_directory))
    curr_date = datetime(year=int(list_of_temporary_folders[0][0:4]), month=int(list_of_temporary_folders[0][5:7]), day=1, hour=0, minute=0, second=0)  # Inclusive
    end_date = datetime(year=int(list_of_temporary_folders[-1][0:4]), month=int(list_of_temporary_folders[-1][5:7]), day=int(lastdayofmonth), hour=23, minute=59, second=59)  # Non-inclusive

    master_list = []
    for year_month in sorted(list_of_temporary_folders):
        year_month_path = os.path.join(temporary_directory, year_month)
        sys.stderr.write("Processing folder: %s\n" % year_month_path)

        month_date = datetime.strptime(year_month, "%Y_%m")
        
        if month_date < curr_date or month_date > end_date:
            continue

        for hour_filename in sorted(os.listdir(year_month_path)):
            if hour_filename.startswith(".") or not hour_filename.endswith(".csv"):
                continue
                
            hour_date = datetime.strptime(hour_filename[hour_filename.index("-")+1:], "%Y_%m_%d-%H.csv")
            if hour_date >= end_date:
                break

            # There's no guarantee that there aren't missing files entirely, so fill them
            # in as necessary.
            fill_in_missing_minutes(curr_date, hour_date)

            hour_path = os.path.join(year_month_path, hour_filename)
            sys.stderr.write("Processing hour: %s\n" % hour_path)
            process_hour_file(hour_date, hour_path)

            #Put data into list

            # Now that we've processed that hour's file, we expect the next hour.
            curr_date = hour_date + timedelta(hours=1)

        # Fill in until the end (files may be missing in the month).
        next_month = month_date.replace(month=month_date.month + 1 if month_date.month != 12 else 1, 
                                        year=month_date.year if month_date.month != 12 else month_date.year + 1)
        fill_in_missing_minutes(curr_date, min(next_month, end_date))
        curr_date = min(next_month, end_date)

    # Fill in until the end (months may be missing).
    fill_in_missing_minutes(curr_date, end_date)

    return master_list

if __name__ == '__main__':
    main()
