# Picking 40 non-top40 songs
# Author: Jonas Berg
table <- read.csv(file="sorted-enriched-contestants2004-2024.csv", header=TRUE, sep=",")
toplist <- table[1:40, ]
non_top <- table[-(1:40), ]
#non_top <- non_top[non_top$year!=2020,]
set.seed(2006)
randoms <- non_top[sample(nrow(non_top), 40), ]
# First version included songs from 2020 which can't be analyzed for networks and visuals
# To minimize extra work, just re-draw those with other non-2020 songs
rejects <- randoms$year==2020
new_draw_size <- sum(rejects)
randoms <- randoms[randoms$year!=2020,]
non_top_non_corona <- non_top[non_top$year!=2020,]
new_draw <- non_top_non_corona[sample(nrow(non_top_non_corona), new_draw_size),]
final_randoms <- rbind(randoms, new_draw) 
# Check that we don't get too many non-qualifiers, they should be around 17
nonquals <- sum(is.na(final_randoms$place_final))
write.csv(final_randoms, file = "random40.csv", sep = ",", row.names=FALSE, fileEncoding = "UTF-8")