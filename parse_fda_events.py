#!/usr/bin/python
# Andrew fda_calendar.py Version 1.0

from bs4 import BeautifulSoup
from urllib2 import urlopen
import time
import datetime
import csv
import os; os.chdir('/Users/andrewkoo/Workspace/Stock_movement/')


def import_events():
	
	url = "http://www.biopharmcatalyst.com/fda-calendar/"
	html = urlopen(url).read()
	
	soup = BeautifulSoup(html, "lxml")
	fdacalendartable = soup.find("tbody")
	
	rows = fdacalendartable.findAll('tr')
	fdacalendarcsv = open('Data/FDA_Event_data/FDA_calendar_'+ time.strftime("%Y%m%d") + '.csv', 'wb')
	calendar_data = csv.writer(fdacalendarcsv)
	columntitle = ["Ticker", "Price", "MktCap", "Type", "Catalyst Date", "Notes"]
	calendar_data.writerow(columntitle)
	
	for i in range(len(rows)):
		elements = rows[i].findAll('td')
		strelements = []
		for j in range(len(elements)):
			strelements.append(unicode(elements[j].string).encode('utf-8'))
		calendar_data.writerow(strelements)
	fdacalendarcsv.close()

def select_events(event):
	file = 'Data/FDA_Event_data/FDA_calendar_'+ time.strftime("%Y%m%d") + '.csv'
	eventcsv = open(file, 'rU')
	allevents = csv.reader(eventcsv)
	i = 1
	eventdic = {}
	for row in allevents:
		if (row[3][0:5] == event):
			eventdic[i] = {}
			eventdic[i]['ticker'] = row[0]
			eventdic[i]['date'] = row[4]
			mktcap = row[2]
			value = float(mktcap[:-1])
			order = mktcap[-1]
			if (order == 'b' and value > 2):
				capsize = 'large'
			elif (order == 'b' and value <= 2):
				capsize = 'mid'
			elif (order == 'm' and value > 200):
				capsize = 'mid'
			else:
				capsize = 'small'
			eventdic[i]['mktcap'] = capsize
			i = i + 1
	return eventdic

def checkcap(capfilter, capsize):
	result = False
	for i in range(len(capfilter)):
		if (capsize == capfilter[i]):
			result = True
	return result

def create_investment_list(event, eventdic, sellweek, capfilter):
	invlistcsv = open('Data/Investment_list.csv', 'wb')
	invlist = csv.writer(invlistcsv)
	title = ['Ticker', 'Buy Date', 'Sell Date', 'Holding Weeks', 'Market Cap Size', event + ' Date']
	invlist.writerow(title)
	eventlist = eventdic.keys()
	for i in range(len(eventlist)):
		eventnum = eventlist[i]
		ticker = eventdic[eventnum]['ticker']
		capsize = eventdic[eventnum]['mktcap']
		eventdate = eventdic[eventnum]['date']
		capresult = checkcap(capfilter, capsize)
		
		[month, day, year] = eventdate.split('/')
		eventdate = datetime.date(int(year), int(month), int(day))
		selldate = eventdate + datetime.timedelta(days = sellweek * 7)
		buydate = datetime.date.today()
		
		period = selldate - buydate
		# convert to weeks
		period = int(round(period.days/7.0))

		if (period > 0 and capresult == True):
			invlist.writerow([ticker, buydate, selldate, period, capsize, eventdate])
	invlistcsv.close()


def main():
	# Import all FDA events from FDA calendar
	import_events()
	print "Event Import Complete"
	
	# Select all desired events and save it to a dictionary
	event = "PDUFA"
	eventdic = select_events(event)
	print 'Event Selection Complete'
	# Create investment to-do list
	# Set the strategy to be buy small and mid cap stocks now and sell two weeks before the event, the week of the event to be week 0
	sellweek = -2
	capfilter = ['small', 'mid'] # can add 'large'
	create_investment_list(event, eventdic, sellweek, capfilter)
	print 'Investment list generated, invest at your own risk!!!'
   	

if __name__ == '__main__':
	main()
