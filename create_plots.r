


times1 <- read.table("runs/:stablestates/PyBoolNet_stablestates/timings.txt", header=FALSE)
times2 <- read.table("runs/:stablestates/GINsim_stablestates/timings.txt", header=FALSE)



plot(times1, type="o", xlab="networks", ylab="time (s)", xaxt='n', main='stablestates', ylim=c(0,4))
points(times2, col="red")




