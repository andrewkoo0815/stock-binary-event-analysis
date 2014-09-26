# This file analyze the potential risk and return for a proposed investment plan

setwd("/Users/andrewkoo/Workspace/Stock_movement")
library("scales")
source("analysis-functions.R")

# Parse the list of investment from the csv file
folder <- "Data"
filename <- "Investment_list.csv"
file <- paste(folder, filename, sep = '/')
invlist <- read.csv(file, head = TRUE)
counts = nrow(invlist)

# Sell two weeks before PDUFA
selldate = -10

# Create data matrix storing data for the portfolio

portfoliox = NULL
portfolioy = matrix(, nrow = 0, ncol = 0)
portfoliosd = matrix(, nrow = 0, ncol = 0)


profitlist <- NULL
risklist <- NULL

for (i in 1:counts) {
	marketcap = toString(invlist[i,5])
	period = invlist[i,4] * 5
	buydate = selldate - period
	outcome <- AnalyzeIndInv(marketcap, buydate, selldate)
	profitlist = c(profitlist, outcome[[1]])
	risklist = c(risklist, outcome[[2]])
	x = outcome[[3]]
	y = outcome[[4]]
	sd = outcome[[5]]
	
	timepoints = length(x)
	x  = x[seq(1, timepoints, 5)]/5
	y  = (y[seq(1, timepoints, 5)] - 1) * 100
	sd  = sd[seq(1, timepoints, 5)]	* 100
	
	portoutcome <- AddToPortfolio(portfoliox, portfolioy, portfoliosd, x, y, sd)
	portfoliox = portoutcome[[1]]
	portfolioy = portoutcome[[2]]
	portfoliosd = portoutcome[[3]]
	
	lastx = tail(x, n=1)
	lasty = tail(y, n=1)
	lastsd = tail(sd, n=1)
	if (i == 1){
		plot(x,y, type = "l", col = "gray", ylim=c(-60, 120), xlim=c(0, 42), xlab="Weeks from Today", ylab="Investment Return (%)")
		arrows(lastx, lasty-lastsd, lastx, lasty+lastsd, col = "gray", code=3, angle=90, length=0.1)
	}
	else{
		lines(x,y, type = "l", col = "gray")
		arrows(lastx, lasty-lastsd, lastx, lasty+lastsd, col = "gray", code=3, angle=90, length=0.1)
	}		
}

portfoliomean = rowMeans(portfolioy)
portfoliosd = sqrt(rowSums(portfoliosd^2))/counts
lines(portfoliox,portfoliomean, type = "l", col = "red")
grid(col = "lightgray", lty = "dotted")

for (j in 2:length(portfoliomean)){
	arrows(portfoliox[j], portfoliomean[j]-portfoliosd[j], portfoliox[j], portfoliomean[j]+portfoliosd[j], col = "red", code=3, angle=90, length=0.03)
}

profit <- percent(mean(profitlist) - 1)
risk <- percent(sqrt(sum(risklist^2))/counts)

title(main=paste("Expected Portfolio Stock Performance toward PDUFAs\n", counts, "Total Investments in Small & Mid-cap Companies\n", "Profit =", profit, "/ Risk (SD) =", risk, sep=" "), font.main = 2)
legend(1,120, c("Individual","Portfolio"), lty=c(1,1), lwd=c(1.5,1.5), col=c("gray","red"), bg = "white")

