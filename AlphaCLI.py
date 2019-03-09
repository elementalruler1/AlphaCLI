import argparse
import urllib2
import csv
import sqlite3
import os

# TO DO: REMOVE SECTOR OPTION OR CREATE PARENT ARGPARSER
# ERROR: REQUESTS TICKER AS OPTION, WHEN NO TICKER SHOULD BE PROVIDED TO
# REQUEST SECTOR DATA



parser = argparse.ArgumentParser(description="Request stock data from AlphaVantage")

parser.add_argument("ticker", metavar="TCKR", 
        help="Company ticker")

#optional arguments
parser.add_argument("-a", "--adjusted", action="store_true",
        help="Get adjusted time series data")
parser.add_argument("-o", "--output_size", choices=['full', 'compact'],
        default='compact',
        help="Specify full or compact output size, default is compact (returns last 100 data points)")

parser.add_argument("-D", "--Datatype", choices=['json','csv','db'],
        default='csv',
        help="Specify data storage type")

#primary required arguments
t_series = parser.add_mutually_exclusive_group(required=True)

t_series.add_argument("-i", "--intraday", type=int, choices=[1,5,15,30,60],
        default=0,
        help="Get intraday time-series data in intervals of 1, 5, 15, 30, or 60 minutes")
t_series.add_argument("-d", "--daily", action="store_true",
        help="Get daily time-series data")
t_series.add_argument("-w", "--weekly", action="store_true",
        help="Get weekly time-series data")
t_series.add_argument("-m", "--monthly", action="store_true",
        help="Get monthly time-series data")
t_series.add_argument("-s", "--sector", action="store_true",
        help="Get current sector data")

args = parser.parse_args()

# READ SETTINGS FROM CONFIG.TXT
# TODO: IMPLEMENT CHANGING SETTINGS FROM COMMAND LINE AND
# ADD A VIEW SETTINGS OPTION

def get_settings():
    config_file = open('config.txt', 'r')
    lines = []
    for ln in config_file:
        lines.append(ln)

    config_data = []
    for setting in lines:
        line = setting.split('=')
        if(len(line) > 1):
            config_data.append(line[1].strip())
    return config_data

settings = get_settings()
# EXTRACT AND STORE SETTINGS
apikey = settings[0]
default_dataStorage = settings[1].lower()
db_name = settings[2].lower()
table_name = settings[3].lower()
log_file = settings[4].lower()
update_log = settings[5].lower()
stock_list = settings[6].lower()

domain = "https://www.alphavantage.co/query?"
symbol = args.ticker

time_series = ""
datatype = ""
interval = ""
output_size = ""

if args.intraday > 0:
    time_series = "TIME_SERIES_INTRADAY"
    interval = str(args.intraday) + "min"
elif args.daily:
    time_series = "TIME_SERIES_DAILY"
elif args.weekly:
    time_series = "TIME_SERIES_WEEKLY"
elif args.monthly:
    time_series = "TIME_SERIES_MONTHLY"
elif args.sector:
    time_series = "SECTOR"

if time_series is not "SECTOR":
    if args.adjusted and time_series is not "TIME_SERIES_INTRADAY":
        time_series += "_ADJUSTED"
    if args.output_size == 'full':
        output_size = "full"
    if args.Datatype == 'csv':
        datatype = 'csv'

full_url = "%sfunction=%s&symbol=%s" % (domain, time_series, symbol)

if time_series == "TIME_SERIES_INTRADAY":
    full_url += "&interval=%s" % interval

if len(output_size) > 0:
    full_url += "&output_size=%s" % output_size

full_url += "&apikey=%s" % apikey
if len(datatype) > 0:
    full_url += "&datatype=%s" % datatype

if time_series == "SECTOR":
    full_url = "%sfunction=%s&apikey=%s" % (domain, time_series, apikey)

print "Requesting data from: www.alphavantage.co/"
print "Function: %s" % time_series
print "Datatype: %s" % datatype


f = urllib2.urlopen(full_url)

dtype = ""
if args.Datatype == 'csv' or args.Datatype == 'db':
    dtype = 'csv'
else:
    dtype = 'json'

f_name = "%s_%s.%s" % (symbol, time_series, dtype)
dfile = open(f_name, "wb")

print "Writing data to %s" % f_name

for ln in f:
    dfile.write(ln)

dfile.close()
print "Finished writing data"

if args.Datatype == "db":
    # implement db loader from 'getAlpha.py'
    # customize for options
    pass
