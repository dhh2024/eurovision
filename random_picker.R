# Picking 40 non-top40 songs
# Author: Jonas Berg
table <- read.csv(file="sorted-enriched-contestants2004-2024.csv", header=TRUE, sep=",")
toplist <- table[1:40, ]
non_top <- table[-(1:40), ]
set.seed(2006)
randoms <- non_top[sample(nrow(non_top), 40), ]
# Check that we don't get too many non-qualifiers, they should be around 17
nonquals <- sum(is.na(randoms$place_final))
write.csv(randoms, file = "random40.csv", sep = ",", row.names=FALSE, fileEncoding = "UTF-8")