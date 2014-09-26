# This file present the data genereated by Python codes

setwd("/Users/andrewkoo/Workspace/Stock_movement")
source("analysis-functions.R")

# Parameters could be changed here
marketcaplist <- c("small", "mid", "large", "all")
directionlist <- c("toward", "after", "around")

direction = directionlist[1]
marketcap = marketcaplist[1]

# Plot the figures
par(mfrow=c(3,1))
marketcap = marketcaplist[4]
for (j in 1:length(directionlist) ) {
		PlotIndOutcome(marketcap, directionlist[j])
		}

readline(prompt="Press [enter] to continue")

dev.new()
par(mfrow=c(3,1))
marketcap = marketcaplist[4]
yscale = ylim=c(0.9,1.8)
for (j in 1:length(directionlist) ) {
		PlotMeanOutcome(marketcap, directionlist[j], yscale)
		}
		
readline(prompt="Press [enter] to continue")

dev.new()
par(mfrow=c(2,2))
direction = directionlist[1]
yscale = ylim=c(0.9,2.2)
for (k in 1:length(marketcaplist) ) {
		PlotMeanOutcome(marketcaplist[k], direction, yscale)
		}