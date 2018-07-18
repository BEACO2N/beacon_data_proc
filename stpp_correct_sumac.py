"""Computes STP-corrected minute averages given the output of the `min_avg.py` script.

Usage:
    cat output_file | python stp_correct.py 

This outputs the results to stdout, so if you want to save the results to a file, do:
    cat output_file | python stp_correct.py > stp_correct_output

If you want you can chain the two scripts directly, e.g.:
    python min_avg.py ~/nodes/exploratorium1 | python stp_correct_output.py
"""

import fileinput
import datetime
import sys
import os
import math

import pdb
 
def main(list_of_min_averages):
    curr_date_bucket = None
    curr_rows = []

 #   pdb.set_trace()

    def compute(date_bucket, rows):
        new_values = []
        #min_value = None
        #min_original_date = None
        for row in rows:
            try:
                dew = float(row[4])
                p = float(row[1])
                co2 = float(row[19])
                t = float(row[20])
            except ValueError:
                row.append('nan') #appending string 'nan' rather than numeric 'nan' because stpp is converted to a string below
                #print ",".join(row)
                continue

            if p == 0:

                row.append('nan') #appending string 'nan' rather than numeric 'nan' because stpp is converted to a string below
                #print ",".join(row)
                continue

            else:
                w = 610.94 * math.exp((17.625 * dew) / (243.04 + dew))
                r = w / (p * 100)
                stp = co2 * (1013.25 / p) * ((t + 273.15) / 298.15) * (1 / (1 - r))
                stpp = stp * ((-0.00055 * p) + 1.5)
                row.append(str(stpp)) # adds stpp value to the end of the row

                #print ",".join(row) # prints out rows with the new stpp value appended

            continue # skips everything below
            new_value = stpp
            new_values.append(new_value)

            #if min_value is None or new_value < min_value:
            #    min_value = new_value
            #    min_original_date = row[-1]

        return # skips everything below

        # This date bucket minimum and average might be necessary for the CO2 correction (i.e. Shusterman et al. ACP 2016)
        # so we'll leave it in for now, but it doesn't do anything for the STP correction as far as
        # we can tell - Josh Laughner, Steve Decina, 17 Jul 2018

        # if len(new_values) == 0:
        #    average = float(sum(new_values)) / len(new_values)
        #    print ",".join([str(min_value), str(min_original_date), str(date_bucket)])
        #
        #else:
        #    print ",," + str(date_bucket)

    #for i, line in enumerate(fileinput.input()):
    #   row = line.strip().split(",")

    for i, row in enumerate(list_of_min_averages):

        date = datetime.datetime.strptime(row[-1], "%Y-%m-%d %H:%M:%S")
        date = date.replace(hour=12, minute=0, second=0)

        if curr_date_bucket is not None and date != curr_date_bucket:
            # We've finished a bucket, compute the thing on it.
            compute(curr_date_bucket, curr_rows)
            curr_rows = []

        curr_date_bucket = date
        curr_rows.append(row)

        if i % 10000 == 0:
            sys.stderr.write("Processed 10000 input rows. Last date: %s\n" % date)

    if curr_date_bucket is not None:
        compute(curr_date_bucket, curr_rows)

    return list_of_min_averages

if __name__ == '__main__':
    main()

