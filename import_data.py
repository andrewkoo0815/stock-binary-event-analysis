# Stock_movement/import_data.py

import csv
import httplib2
import requests
import cStringIO
import shutil
import xml.etree.cElementTree as et
import os; os.chdir('/Users/andrewkoo/workspace/Stock_movement/')


# This function gets the stock movement data from yahoo finance
def get_stock_price_data(symbol):
	
	# If we have already got the data from previous run, don't bother doing it again
	if (os.path.isfile('Data/Price_data/' + symbol + '.csv') == True):
		return
	
	h = httplib2.Http('.cache')
	url = 'http://ichart.finance.yahoo.com/table.csv?s=' + symbol 
	
	# First check if the yahoo finance has this stock's data, the data might be removed if the company
	# is delisted due to acquisition or bankruptcy. If true, download the data and save it as a new file.
	# If not, just copy it from the old data files generated when the stock is still listed.
	
	if (check_url_exist(url) == True):
		headers, data = h.request(url)
		stockfile = open('Price_data/' + symbol + '.csv', 'wb')
		stockfile.write(data)
		stockfile.close()
	else:
		if (os.path.isfile('Old_Price_data/' + symbol + '.csv') == True):
			shutil.copyfile('Old_Price_data/' + symbol + '.csv', 'Price_data/' + symbol + '.csv')

# This function get the number of outstanding share (with the date of the record)from morningstar
# If the stock is delisted, it will get it from the previous record.
# The number of share outstanding will be used to calculate the market cap
def get_financial_data(symbol):

	# If we have already got the data from previous run, don't bother doing it again
	if (os.path.isfile('Data/Financial_data/Fin_' + symbol + '.csv') == True):
		return

	h = httplib2.Http('.cache')
	url = 'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t=' + symbol + '&region=USA&culture=en_us&reportType=is&period=12&dataType=A&order=desc&columnYear=5&rounding=1&view=raw&productCode=usa&r=283305&denominatorView=raw&number=3'
	headers, data = h.request(url)
	
	if (data != ''):
		isdatacsv = cStringIO.StringIO(data)
		# Income statement data
		isdata = csv.reader(isdatacsv)
		findatacsv = open('Data/Financial_data/Fin_' + symbol + '.csv', 'wb')
		fin_data = csv.writer(findatacsv)
		row_count = 0
		for row in isdata:
			if (row_count == 0):
				row_count = 1
			elif (row_count == 1):
				fin_data.writerow(row[2:])
				row_count = 2
			elif (row[0] == 'Diluted' and row_count == 3):
				fin_data.writerow(row[2:])
			elif (row[0] == 'Diluted'):
				row_count = 3
		findatacsv.close()
	else:
		if (os.path.isfile('Data/Old_Financial_data/Fin_' + symbol + '.csv') == True):
			isdatacsv = open('Data/Old_Financial_data/Fin_' + symbol + '.csv', 'rU')
			isdata = csv.reader(isdatacsv)
			findatacsv = open('Data/Financial_data/Fin_' + symbol + '.csv', 'wb')
			fin_data = csv.writer(findatacsv)
			row_count = 0
			for row in isdata:
				if (row_count == 0):
					row_count = 1
					rowprime = row[:-1]
					newrow = []
					for i in range(len(rowprime)):
						element = rowprime[i]
						newrow.append(element[1:8])
					fin_data.writerow(newrow)
				elif (row[4] == 'Total Common Shares Outstanding'):
					fin_data.writerow(row[:-1])
			findatacsv.close()
		

# This function checks if the url for the data exists
def check_url_exist(url):
	r = requests.head(url)
	code = r.status_code
	if (code == 404):
		exist = False
	else:
		exist = True
	return exist


# This function load all the stock symbols in the database
def load_symbol_list(databasefile):
	lcadatabase = open(databasefile, 'rU')
	database = csv.reader(lcadatabase)
	symbollist = []
	for row in database:
		symbol = row[5]
		if (symbol != 'Ticker_1' and symbol != 'PRIVATE'):
			symbollist.append(symbol)
	return symbollist


# This function goes through the symbol list and call the get_stock_price_data(symbol) function
def get_all_data(LCADatabase):
	symbollist = load_symbol_list(LCADatabase)
	for i in range(len(symbollist)):
		get_financial_data(symbollist[i])
		get_stock_price_data(symbollist[i])

	
def import_data():  
	LCADatabase = 'Data/LCADatabase(06.14.13).csv'
	get_all_data(LCADatabase)


if __name__ == '__main__':
  import_data()
