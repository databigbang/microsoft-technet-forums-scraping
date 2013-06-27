#!/usr/bin/python

import urllib
from lxml import etree
import lxml.html
import sqlite3 as lite
import sys

urllib.URLopener.version = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15"

def get_threads(num):
	url = 'http://social.technet.microsoft.com/Forums/en-US/mdopappv/threads?outputAs=xml&page=%d' % num
	xml = urllib.urlopen(url).read()
	root = etree.fromstring(xml)
	threads = root.xpath("//topic")
	threads_creator_id = root.xpath("//thread/@authorId")
	threads_creator = []

	for element in threads_creator_id:
		threads_creator.append(root.xpath("//user[@id='{0}']/displayName".format(element)))

	threads_replies = root.xpath("//thread/@replies")
	threads_views = root.xpath("//thread/@views")

	threads_url, threads_url_incomplete = get_threads_url(url)
	
	return threads, threads_creator, threads_replies, threads_views, threads_url, threads_url_incomplete

def retrieve_all_threads():
	forum_page = 1
	tid = 0
	page = 0
	ThreadID = 0
	con = lite.connect('App-V.db')

	with con:
		cur = con.cursor()
		try:
			cur.execute("CREATE TABLE Threads(id INT, title TEXT, creator TEXT, views INT, replies INT, url TEXT);")
			cur.execute("CREATE TABLE Comments(ROWID INTEGER PRIMARY KEY, tid INT, user TEXT, comment TEXT, commentDate TEXT, commentScore INT);")
			cur.execute("CREATE INDEX idIndex on Threads(id);")
			cur.execute("CREATE INDEX viewsIndex on Threads(views);")
			cur.execute("CREATE INDEX rowIdindex on Comments(ROWID);")
			cur.execute("CREATE INDEX tidIndex on Comments(tid);")
			cur.execute("CREATE INDEX scoreIndex on Comments(commentScore);")
		
		except:
			pass

		while True:
			threads, threads_creator, threads_replies, threads_views, threads_url, threads_url_incomplete = get_threads(forum_page)
			
			if (threads==[]):
				break

			for i in xrange(0, len(threads)):
				print 'Thread ID: ', tid
				print 'Forum Page: ', forum_page
				print 'Thread: ', threads[i].text
				print 'Thread Creator: ', threads_creator[i][0].text
				print 'Threads Replies:', threads_replies[i]
				print 'Threads Views: ', threads_views[i]
				print 'Thread Url: ', threads_url_incomplete[i].text
			
				thread_comments, thread_users, thread_comments_date = retrieve_all_comments_and_users_in_thread(threads_url[i])
				user_comment_score = get_score(threads_url[i])

				cur.execute("INSERT INTO Threads(id, title, views, creator, replies, url) VALUES(?, ?, ?, ?, ?, ?);", (tid, threads[i].text, threads_views[i], threads_creator[i][0].text, threads_replies[i], threads_url_incomplete[i].text))

				for i in xrange(0, len(thread_users)):
					print 'Comment User: ', thread_users[i][0].text
					print 'Comment: ', thread_comments[i].text_content()
					print 'Comment Date: ', thread_comments_date[i].text
					print 'Comment Score: ', user_comment_score[i]
					print '----------------------------------------------------------------------------'

					cur.execute("INSERT INTO Comments(tid, user, comment, commentDate, commentScore) VALUES(?, ?, ?, ?, ?);", (tid, thread_users[i][0].text, thread_comments[i].text_content(), thread_comments_date[i].text, user_comment_score[i]))

					con.commit()

				tid += 1

			forum_page += 1


def get_threads_url(url):
	xml = urllib.urlopen(url).read()
	root = etree.fromstring(xml)
	threads_url_incomplete = root.xpath("//thread/url")
	threads_url = []
	for i in xrange(0, len(threads_url_incomplete)):
		threads_url.append(threads_url_incomplete[i].text + '?outputAs=xml')

	return threads_url, threads_url_incomplete


def retrieve_all_comments_and_users_in_thread(url):
	xml = urllib.urlopen(url).read()
	xml_root = etree.fromstring(xml)
	thread_comments_xml = xml_root.xpath("//body")
	thread_comments_html = []
	for element in thread_comments_xml:
		root = lxml.html.fromstring(element.text)
		thread_comments_html.append(root)

	thread_users_id = xml_root.xpath("//message/@authorId")
	thread_users = []

	for element in thread_users_id:
		thread_users.append(xml_root.xpath("//user[@id='{0}']/displayName".format(element)))
	
	thread_comments_date = xml_root.xpath("//createdOn")
	del thread_comments_date[0]

	return thread_comments_html, thread_users, thread_comments_date

def get_score(url):
	xml = urllib.urlopen(url).read()
	xml_root = etree.fromstring(xml)
	user_comment_score = xml_root.xpath("//message/@helpfulVotes")

	return user_comment_score


def main():
	retrieve_all_threads()


if __name__ == '__main__':
	main()
