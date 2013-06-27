#!/usr/bin/python

import csv
import collections
import sqlite3 as lite
import sys
import datetime
import cStringIO
import codecs


def main():
	con = lite.connect('App-V.db')
	cur = con.cursor()
	cur2 = con.cursor()
	views_dict = dict()
	a = []
	n = datetime.datetime.now()
		
	for row in cur.execute("SELECT * FROM Threads;"):
		thread_id = row[0]		
		title = row[1]		
		views = row[3]
		replies = row[4]
		url = row[5]
		firstComment = cur2.execute('SELECT min(ROWID), commentDate FROM Comments WHERE tid=?', [str(thread_id)]).fetchone()
		p = datetime.datetime.strptime(firstComment[1], "%Y-%m-%d %H:%M:%SZ")
		date = n-p 
		views_dict[views] = (title, date.days, replies, url)

	final_dict = collections.OrderedDict(sorted(views_dict.items(), reverse=True))

	with open('/home/administrator/Documents/code/sandbox/python/lxml.html/App-V.csv', 'wb') as csvfile:
		spamwriter = CSVUnicodeWriter(csvfile)
		spamwriter.writerow(['Views', 'Title', 'Date', 'Replies', 'URL'])

		for key in final_dict:
			try:
				utf_title = final_dict[key][0]
				spamwriter.writerow([str(key), utf_title, str(final_dict[key][1]), str(final_dict[key][2]), str(final_dict[key][3])])
			except:
				a.append(key)
				pass

	print a

class CSVUnicodeWriter: # http://docs.python.org/library/csv.html
	"""
	A CSV writer which will write rows to CSV file "f",
	which is encoded in the given encoding.
	"""

	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		# Redirect output to a queue
		self.queue = cStringIO.StringIO()
		self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
		self.stream = f
		self.encoder = codecs.getincrementalencoder(encoding)()
		f.write('\xEF\xBB\xBF')

	def writerow(self, row):
		self.writer.writerow([s.encode("utf-8") for s in row])
		# Fetch UTF-8 output from the queue ...
		data = self.queue.getvalue()
		data = data.decode("utf-8")
		# ... and reencode it into the target encoding
		data = self.encoder.encode(data)
		# write to the target stream
		self.stream.write(data)
		# empty queue
		self.queue.truncate(0)

	def writerows(self, rows):
		for row in rows:
			self.writerow(row)


if __name__ == '__main__':
	main()
