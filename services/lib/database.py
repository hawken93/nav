"""
database

$Author: magnun $
$Id: database.py,v 1.12 2002/06/20 14:41:29 magnun Exp $
$Source: /usr/local/cvs/navbak/navme/services/lib/Attic/database.py,v $
"""
import thread
from psycopg import connect
from job import Event,jobmap
from Queue import Queue

db = None

queue = Queue()

def startup(dsn):
	global db
	db = connect(dsn)
	thread.start_new_thread(run,())
def run():
	c = db.cursor()
	while 1:
		statement = queue.get()
		c.execute(statement)
def newEvent(event):
	print "New event. Id: %i Status: %s Info: %s"% (event.serviceid, event.status, event.info)
	if event.status == event.UP:
		value = 100
	else:
		value = 0
	statement = "INSERT INTO eventq (deviceid,boksid,eventtypeid,statefull,value,descr) values (%i, %i, %s, '%s', %i, '%s' " % (event.serviceid, event.boksid, event.type, 't',value,event.info)
	queue.put(statement)
def newVersion(serviceid,version):
	print "New version. Id: %i Version: " % (serviceid,version)
	statement = "UPDATE service SET version = '%s' where serviceid = %i" % (version,serviceid)
	queue.put(statement)
def getJobs():
	c = db.cursor()
	query = """SELECT serviceid, property, value
	FROM serviceproperty
	order by serviceid"""
	c.execute(query)

	for serviceid,prop,value in c.fetchall():
		if serviceid not in property:
			property[serviceid] = {}
		property[serviceid][prop] = value

	query = """SELECT serviceid ,boksid, handler, version, ip
	FROM service NATURAL JOIN boks order by serviceid"""
	c.execute(query)
	jobs = []
	for serviceid,boksid,handler,version,ip in c.fetchall():
		job = jobmap.get(handler,'')
		if not job:
			print 'no such handler:',handler
		newJob = job(serviceid,boksid,ip,property.get(serviceid,{}),version)
		print "Property: %s" % property
		jobs += [newJob]
	db.commit()
	return jobs


if __name__ == '__main__':
	startup('host = localhost user = manage dbname = manage password = eganam')
	jobs = getJobs()
	for i in jobs:
		print jobs
