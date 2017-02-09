import http.client
import time
import sqlite3
import os
import datetime
from twitter import *
import config as cfg

#database config
db_filename = 'down.db'
fileCheck = os.path.isfile(db_filename)
conn = sqlite3.connect(db_filename)
conn.text_factory = str

t = Twitter(auth=OAuth(cfg.accessToken, cfg.accessTokenSecret, cfg.consumerKey, cfg.consumerSecret))

def nowDatetime():
	return (time.strftime("%Y-%m-%d %H:%M:%S"))

def convepoch(date):
	fmt = "%Y-%m-%d %H:%M:%S"
	now = time.localtime(date)
	fmtTime = time.strftime(fmt,now)
	return fmtTime


#create db if db is empty/new
fileSize = os.stat(db_filename)
fileSize.st_size

if fileSize.st_size == 0:
	q_down_time_table="""
	CREATE TABLE "down_time" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"start_time" TEXT,
	"end_time" TEXT,
	"total_down_time" TEXT
	);
	"""
	conn.execute(q_down_time_table)

testOut = False

q_downCount = "select count(*) from down_time where start_time > datetime('now','-1 day')"

downCount = 0

upCount = 0

startTime = time.time() 

tweet2send = ''


while True:
	#testing Check
	if testOut == True:
		print('\n')
		print('=::Testing Output::=')
		print('Downcount: '+str(downCount))
		print('Upcount: '+str(upCount))
		print('Tweet Length: '+str(len(tweet2send)))
		print('=::Testing Output::=')
		print('\n')

	#if tweet var is set and inet has been up long enought send tweet
	if len(tweet2send)>0 and upCount >= cfg.tweetUp:
		print('\n')
		print('The Following Tweet was posted to twitter sucessfully:')
		print(tweet2send)
		t.statuses.update(status=tweet2send)
		print('\n')
		tweet2send = ''

	con = http.client.HTTPConnection("www.google.com")
	try:
		con.request("HEAD", "/")
		upCount += 2

		if upCount == 2: print('\n')

		#converting seconds to proper time value for terminal output
		if upCount <= 60:
			upTime = str(upCount)+' Seconds!'
		elif upCount > 60 and upCount < 3600:
			upTime = str(round(float(upCount)/60,2))+' Minutes!'
		elif upCount >= 3600:
			upTime = str(round(float(upCount)/3600,2))+' Hours!'

		print('Internet Is Up and has been up for the last '+upTime)
		if downCount > cfg.downLog:
			timeDown = round(time.time() - startTime,3)

			#count total times down 24hrs, add one to count current time
			downTotal_q = conn.execute(q_downCount)
			downTotal = downTotal_q.fetchone()
			downTotal = str(int(downTotal[0])+1)

			insertDownTime = 'INSERT INTO down_time (start_time,end_time,total_down_time) VALUES (\''+str(convepoch(startTime))+'\',\''+str(nowDatetime())+'\','+str(timeDown)+');'
			conn.execute(insertDownTime)

			conn.commit()
			print('\n')
			print('Internet was down for '+str(timeDown)+' seconds!')
			tweet2send = 'Hey begining at '+str(convepoch(startTime))+' our internet was down for '+str(timeDown)+' seconds! Internet has dropped '+downTotal+' times in 24hrs!'
			print('\n')
		downCount = 0
	except:
		#if testOut == True: print(str(e))
		downCount+=1

		if downCount == 1: print('\n')

		#converting seconds to proper time value for terminal output
		if downCount <= 60:
			downTime = str(downCount*2)+' Seconds!'
		elif downCount > 60 and downCount < 3600:
			downTime = str(round(float(downCount)*2/60,2))+' Minutes!'
		elif downCount >= 3600:	
			downTime = str(round(float(downCount)*2/3600,2))+' Hours!'

		upCount = 0
		print('Internet is down!!!! and has been down '+downTime)
	if downCount==5:
		startTime=time.time()

	time.sleep(2)
