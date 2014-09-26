# This file plots the data genereated by Python codes and conducts statistical analysis on the data

library("Hmisc")

# Get Timing and xaxis
GetTimeData <- function(stockdata, direction){
	
	timepoints = nrow(stockdata)
	if (direction == "around") {
	  xaxis <- c(ceil(- 0.5 * nrow(stockdata)):(ceil(0.5 * nrow(stockdata)) - 1))  
	} else if (direction == "after") {
	  xaxis <- c(0:(timepoints - 1))
	} else {
	  xaxis <- c((-1 * timepoints + 1):0)      
	} 
	return(xaxis)
}

# Get Stock Movement data
GetStockData <- function(marketcap, direction){
	# Parse the stock price data from the csv file
	folder <- "Data/Data_for_Analysis"
	
	filename <- paste(direction, '_pdufa_', marketcap, '-cap.csv' , sep="")
	file <- paste(folder, filename, sep = '/')
	stockdata <- read.csv(file, head = FALSE)
	stockdata <- t(stockdata)
	mode(stockdata) <- "numeric"
	
	# Normalize stockdata with the first element
	reference = stockdata[1,]
	stockdata <- sweep(stockdata, MARGIN=2, reference,`/`)
	
	# Generate the proper xaxis for the data
	xaxis <- GetTimeData(stockdata, direction)

	return(list(xaxis, stockdata))	
}


# Plot time series of all events
PlotIndOutcome <- function(marketcap, direction){
	
	data = GetStockData(marketcap, direction)
	xaxis = data[[1]]
	stockdata = data[[2]]
	timepoints = nrow(stockdata)
	totalevents = ncol(stockdata)
	colors = rainbow(totalevents)
	x  = xaxis[seq(1, timepoints, 5)]/5
	y  = stockdata[,2][seq(1, timepoints, 5)]
	
	# dev.new()
	
	par(bg = 'white')
	plot(x,y, type = "l", col = colors[1], ylim=c(0,11), xlab=paste("Weeks", direction, "PDUFA"), ylab="Normalized Stock Price")
	title(main=paste("Individual Biotech Stock Trend", direction, "PDUFA", paste("(" , marketcap , "-cap)", sep="")), font.main = 2)
	title(sub=paste("N =", totalevents, sep = " "),  cex.sub = 0.6)
	
	for (i in 2:totalevents ) {
		y  = stockdata[,i][seq(1, timepoints, 5)]
		lines(x,y, type = "l", col = colors[i])
	}
	# dev.copy(png,'plot1.png')
	# dev.off()
}


# Plot time series of averaged outcome with standard error
PlotMeanOutcome <- function(marketcap, direction, yscale){
	
	data = GetStockData(marketcap, direction)
	xaxis = data[[1]]
	stockdata = data[[2]]
	mean <- rowMeans(stockdata)
	stdev <- apply(stockdata,1,sd)
	se <- stdev / length(stdev)^0.5
	timepoints = nrow(stockdata)
	totalevents = ncol(stockdata)
	
	# dev.new()
	
	d = data.frame(
	  x  = xaxis[seq(1, timepoints, 5)]/5
	  , y  = mean[seq(1, timepoints, 5)]
	  , sd = se[seq(1, timepoints, 5)]
	)
	par(bg = 'white')
	# plot(d$x, d$y, type="n")
	with (
	  data = d
	  , expr = errbar(x, y, y+sd, y-sd, add=F, pch=1, cap=.015, xlab=paste("Weeks", direction, "PDUFA"), ylab="Normalized Stock Price", ylim = yscale)
	)
	ypred <- FindNlsFit(xaxis, stockdata)
	lines(xaxis[seq(1, timepoints, 5)]/5,ypred[seq(1, timepoints, 5)], type = "l", col = 'red')
	title(main=paste("Adveraged Biotech Stock Trend\n", direction, "PDUFA", paste("(" , marketcap , "-cap)", sep="")), font.main = 2)
	title(sub=paste("Error Bars = Standard Error, N =", totalevents, sep = " "),  cex.sub = 0.6)
}


# For nonlinear-regression
FindNlsFit <- function(xaxis, stockdata){
	totalevents = ncol(stockdata)
	xdata <- NULL
	ydata <- NULL
	for (i in 1:totalevents ) {
		xdata = c(xdata, xaxis)
		ydata = c(ydata, stockdata[,i]) 
		}
	fit = nls(ydata ~ p0 + p1*xdata + p2*xdata^2 + p3*xdata^3, start=list(p0=0, p1=0, p2=0, p3=0))
	parameters = fit$m$getPars()
	ypred = parameters[1] + parameters[2] * xaxis + parameters[3] * xaxis^2 + parameters[4] * xaxis^3
	return(ypred)
}

AnalyzeIndInv <- function(marketcap, buydate, selldate){
	
	direction <- "toward"
	folder <- "Data/Data_for_Analysis"
	filename <- paste(direction, '_pdufa_', marketcap, '-cap.csv' , sep="")
	file <- paste(folder, filename, sep = '/')
	stockdata <- read.csv(file, head = FALSE)
	stockdata <- t(stockdata)
	mode(stockdata) <- "numeric"
	xaxis <- GetTimeData(stockdata, direction)
	timepoints = nrow(stockdata)
	
	xaxis <- xaxis[(timepoints + buydate):(timepoints + selldate)]
	xaxis <- xaxis - min(xaxis)
	stockdata <- stockdata[(timepoints + buydate):(timepoints + selldate),]
	
	# Normalize stockdata with the first element
	reference = stockdata[1,]
	stockdata <- sweep(stockdata, MARGIN=2, reference,`/`)
	ypred <- FindNlsFit(xaxis, stockdata)
	mean <- rowMeans(stockdata)
	stdev <- apply(stockdata,1,sd)
	
	# profit <- tail(ypred, n = 1)
	profit <- tail(mean, n = 1)
	
	risk <- tail(stdev, n = 1)	
	# PlotMeanOutcome(xaxis, stockdata, marketcap, direction)
	return(list(profit, risk, xaxis, mean, stdev))
}

AddToPortfolio <- function(portfoliox, portfolioy, portfoliosd, x, y, sd){

	if (length(x) > length(portfoliox)){
		portfoliox = x
	}
	if (ncol(portfolioy) == 0){
		portfolioy = matrix(y, ncol = 1)
		portfoliosd = matrix(sd, ncol = 1)
	}
	else{
		while(nrow(portfolioy) < length(y)){
			portfolioy = rbind(portfolioy, tail(portfolioy, n = 1))
			portfoliosd = rbind(portfoliosd, tail(portfoliosd, n = 1))
		}
		portfolioy = cbind(portfolioy, y)
		portfoliosd = cbind(portfoliosd, sd)
	}
	return(list(portfoliox, portfolioy, portfoliosd))
}


