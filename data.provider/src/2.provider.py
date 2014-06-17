# provider.py usdchf 02

# argument 1 is a custom forex pair name
# argument 2 is a custom month number

import sys, sched, time, cql

# connect to database
con = cql.connect('ec2-54-187-166-118.us-west-2.compute.amazonaws.com',
		'9160', 'janusz_forex_rt_demo', cql_version='3.1.1')
cursor = con.cursor()

# time conversion
custom_month = -1 
forex_pair = "unknown"
if len(sys.argv) > 2:
	forex_pair = sys.argv[1]
	custom_month = sys.argv[2]

# load a file to memory
print "Loading data to memory..."
lines = [line.strip() for line in sys.stdin]
print "Loading data to memory done!"

# initialize scheduler	
s = sched.scheduler(time.time, time.sleep)

def upload(q,m):
	print m
	cursor.execute(q)

print "Loading data to scheduler..."
for line in lines:
	cols = line.split(",")
	date = cols[0].split(" ")

	year = date[0][0:4]
	month = date[0][4:6]
	if custom_month>0:
		month = custom_month
	day = date[0][6:8]

	hour = date[1][0:2]
	minute = date[1][2:4]
	second = date[1][4:6]
	milisec = date[1][6:9]
	
	bid = cols[1]
	ask = cols[2]

	q = "INSERT INTO ticks (pair_day,issued_at,bid,ask) VALUES ("
	q = q + "'" + forex_pair + ":" + year + "-" + month + "-" + day + "',"
	q = q + "'" + year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second + "." + milisec + "',"
	q = q + "" + bid + ","
	q = q + "" + ask + ");"

	m = "pushing " + forex_pair + " " + year + "-" + month
	m = m + "-" + day + " " + hour + ":" + minute + ":" + second + "." + milisec

	s.enterabs(time.mktime(time.strptime(
		year + month + day + 
		hour + minute + second + milisec + "00",
		"%Y%m%d%H%M%S%f")),1,upload,argument=(q,m))
	
print "Loading data to scheduler done!"

# run the scheduler

print "Running scheduler..."
s.run()
print "Running scheduler done!"

# cleanup when scheduler is done
cursor.close()
con.close()

