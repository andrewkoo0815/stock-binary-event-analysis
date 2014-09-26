# Stock_movement/get_marketcap.py

import csv
import datetime
import os; os.chdir('/Users/andrewkoo/workspace/Stock_movement/')

def get_datelist_and_pricelist(ticker, date):
	fileloc = 'Data/Price_data/' + ticker + '.csv'	
	pricedatacsv = open(fileloc, 'rU')
	allpricedata = csv.reader(pricedatacsv)
	datelist = []
	pricelist = []
	
	firstrow = True
	for row in allpricedata:
		if (firstrow == True):
			if (row[0] == 'Date'):
				[datecol, pricecol, reverse] = [0, 4, True]
			else:
				[datecol, pricecol, reverse] = [6, 3, False]
			firstrow = False
		else:
			datelist.append(row[datecol])
			pricelist.append(float(row[pricecol]))
	if (reverse == True):
		datelist.reverse()
		pricelist.reverse()
	return datelist, pricelist
	

def get_stock_price(ticker, date):
	# get stock price one year before the event
	[year, month, day] = date.split('-')
	keydate = datetime.date(int(year) - 1, int(month), int(day))
	[datelist, pricelist] = get_datelist_and_pricelist(ticker, date)

	listloc = 0
	reach = False
	while (reach == False):
		thisdate = datelist[listloc]
		[year, month, day] = thisdate.split('-')
		thisdate = datetime.date(int(year), int(month), int(day))
		if (thisdate >= keydate):
			reach = True
		listloc = listloc + 1
	return pricelist[listloc - 1]


def get_stock_pricelist(ticker, date, length, direction):
	[year, month, day] = date.split('-')
	keydate = datetime.date(int(year), int(month), int(day))
	[datelist, pricelist] = get_datelist_and_pricelist(ticker, date)
	selectedlist = []

	listloc = 0
	reach = False
	while (reach == False):
		thisdate = datelist[listloc]
		[year, month, day] = thisdate.split('-')
		thisdate = datetime.date(int(year), int(month), int(day))
		if (thisdate >= keydate):
			reach = True
		listloc = listloc + 1
	if (direction == 'after'):
		selectedlist = pricelist[listloc:(listloc + length)]
	elif (direction == 'toward'):
		selectedlist = pricelist[(listloc - length):(listloc)]
	else:
		selectedlist = pricelist[(listloc - length):(listloc + length)]
	return selectedlist


def get_stock_volume(ticker, date):
	[year, month, day] = date.split('-')
	theyear = str(int(year) - 1)
	fileloc = 'Data/Financial_data/Fin_' + ticker + '.csv'	
	findatacsv = open(fileloc, 'rU')
	allvolumedata = csv.reader(findatacsv)
	firstrow = True
	for row in allvolumedata:
		if (firstrow == True):
			datelist = row
			firstrow = False
		else:
			volumelist = row
	i = 0
	volume = volumelist[-1]
	while (i < len(datelist)):
		if (datelist[i][0:4] == theyear):
			volume = volumelist[i]
			i = len(datelist)
		else:
			i = i + 1
	return float(volume)

def get_marketcap(ticker, date):
	price = get_stock_price(ticker, date)
	volume = get_stock_volume(ticker, date)
	marketcap = price * volume
	return marketcap
			
