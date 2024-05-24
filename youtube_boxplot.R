library(ggplot2)
library(scales)
table <- read.csv(file="sorted-enriched-contestants2004-2024.csv", header=TRUE, sep=",")
toplist <- table[1:40, ]
toplist$class <- "Top 40"
randomlist <- read.csv(file="random40.csv", header=TRUE, sep=",")
randomlist$class <-"Random 40"
combined <- rbind(toplist, randomlist)

# Given a vector x, return a vector of powers of 10 that encompasses all values
# in x.
breaks_log10 <- function(x) {
  low <- floor(log10(min(x)))
  high <- ceiling(log10(max(x)))
  
  10^(seq.int(low, high))
}

png(filename="youtube_boxplot.png", bg = "transparent")
ggplot(combined, aes(x=as.factor(class), y=views, fill=as.factor(class))) + 
  geom_boxplot(fill=c("orange", "magenta")) + labs(title = "Youtube Views by '40' Groups", x = "", y = "log10(Youtube views)") +
 xlab("") + ylab("Total Views") + scale_fill_manual(values = c("orange", "magenta")) +
  theme_minimal()+
  theme(text = element_text(size=20),legend.position = "none",axis.ticks.x = element_blank()) + annotation_logticks(sides = "lr") +  scale_y_log10(breaks = breaks_log10,
                                                                                                        labels = trans_format(log10, math_format(10^.x)))
dev.off()