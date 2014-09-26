# Stock_movement/parse_data.py

import csv
import datetime
import import_data
import get_data
import os; os.chdir('/Users/andrewkoo/workspace/Stock_movement/')

# Load all database info
fileloc = 'Data/LCADatabase(06.14.13).csv'	
lcadatabase = open(fileloc, 'rU')
database = csv.reader(lcadatabase)
ndainfo = {}
count = 0
for row in database:
	if (count == 0):
		count = 1
	else:
		ndainfo[count] = {}
		ndainfo[count]['omit'] = row[0]
		ndainfo[count]['resolved'] = row[1]
		
		ticker = row[5]
		ndainfo[count]['ticker'] = ticker
		ndainfo[count]['adcom_result'] = row[22]
		ndainfo[count]['pdufa_result'] = row[23]
		ndainfo[count]['nda_date'] = 'N/A'
		ndainfo[count]['adcom_date'] = 'N/A'
		ndainfo[count]['pdufa_date'] = 'N/A'
		
		keydates = row[24].split(';')
		for i in range(len(keydates)):
			if (keydates[i][0:6] == 'ADCOM/'):
				ndainfo[count]['adcom_date'] = keydates[i][6:]
			elif (keydates[i][0:5] == 'PDUFA'):
				ndainfo[count]['pdufa_date'] = keydates[i][6:]
			elif (keydates[i][0:5] == 'NDA-F'):
				ndainfo[count]['nda_date'] = keydates[i][6:]
		if (os.path.isfile('Data/Financial_data/Fin_' + ticker + '.csv') == True and os.path.isfile('Data/Price_data/' + ticker + '.csv') == True):
			ndainfo[count]['stock_data_exist'] = 'Yes'
		else:
			ndainfo[count]['stock_data_exist'] = 'No'
		count = count +1
		
def data_filter(number, event):
	ndainfo[number]['keep'] = True
	
	if (ndainfo[number]['omit'] == 'Yes'):
		ndainfo[number]['keep'] = False
	elif (ndainfo[number]['resolved'] == 'No'):
		ndainfo[number]['keep'] = False
	elif (ndainfo[number]['nda_date'] == 'N/A' and event == "nda"):
		ndainfo[number]['keep'] = False
	elif (ndainfo[number]['nda_date'] == 'XXXX-XX-XX' and event == "nda"):
		ndainfo[number]['keep'] = False
	elif (ndainfo[number]['pdufa_date'] == 'N/A' and event == "pdufa"):
		ndainfo[number]['keep'] = False
	elif (ndainfo[number]['adcom_date'] == 'N/A' and event == "adcom"):
		ndainfo[number]['keep'] = False
	elif (ndainfo[number]['pdufa_result'] != 'Approval' and ndainfo[number]['pdufa_result'] != 'CRL'):
		ndainfo[number]['keep'] = False
	elif (ndainfo[number]['stock_data_exist'] == 'No'):
		ndainfo[number]['keep'] = False
		
def get_filtered_list(event):
	goodlist = []
	for i in range(1, count):
		data_filter(i, event)
		if (ndainfo[i]['keep'] == True):
			goodlist.append(i)
	return goodlist
	
def company_size_filter(companysize, ticker, date):
	marketcap = get_data.get_marketcap(ticker, date)
	if (companysize == 'all'):
		return True
	elif (companysize == 'small' and marketcap <= 200):
		return True
	elif (companysize == 'mid' and marketcap > 200 and marketcap <= 2000):
		return True
	elif (companysize == 'large' and marketcap > 2000):
		return True
	else:
		return False
			
			
def write_data(goodlist, event, direction, length, companysize):
	stockdatacsv = open('Data/Data_for_Analysis/' + direction + '_' + event + '_' + companysize + '-cap.csv', 'wb')
	stock_data = csv.writer(stockdatacsv)
	eventdate = event + "_date"
	
	for i in range(len(goodlist)):
		number = goodlist[i]
		ticker = ndainfo[number]['ticker']
		date = ndainfo[number][eventdate]
		
		if (company_size_filter(companysize, ticker, date) == True):
			pricelist = get_data.get_stock_pricelist(ticker, date, length, direction)
			if (len(pricelist) == length and direction != "around"):
				stock_data.writerow(pricelist)
			elif (len(pricelist) == 2*length):
				stock_data.writerow(pricelist)
	stockdatacsv.close()
	
			
def main():	
	print "Starting Data Import..."
	import_data.import_data()
	print "Data Import Complete"
	raw_input("Press Enter to Start Data Parsing")
	length = 225 # trading days: 225 days about 10.5 month or 45 weeks
	event = "pdufa"	# choice: "nda", "adcom", "pdufa"
	goodlist = get_filtered_list(event)	
	directionlist = ["around", "toward", "after"]
	sizelist = ["all" , "small" , "mid", "large"]

	for i in range(len(directionlist)):
		for j in range(len(sizelist)):
			write_data(goodlist, event, directionlist[i], length, sizelist[j])
	print "Data Parsing Complete"


if __name__ == '__main__':
	main()
