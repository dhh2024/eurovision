library(ggplot2)
table <- read.csv(file="sorted-enriched-contestants2004-2024.csv", header=TRUE, sep=",")
toplist <- table[1:40, ]
toplist$class <- "Top 40"
randomlist <- read.csv(file="random40.csv", header=TRUE, sep=",")
randomlist$class <-"Random 40"
combined <- rbind(toplist, randomlist)
head(mtcars)
ggplot(combined, aes(x=as.factor(class), y=views, fill=as.factor(class))) + 
  geom_boxplot(fill=c("orange", "magenta")) + labs(title = "Youtube views by '40' Groups", x = "", y = "Youtube views") +
 xlab("") + ylab("Total views") + scale_fill_manual(values = c("orange", "magenta")) +
  theme_minimal()+
  theme(legend.position = "none")
