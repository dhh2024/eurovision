#library(plotrix)
slices <- c(1/3, 1/6, 1/6, 1/3)
lbls <- c("Jury votes 33%", "Spotify popularity 17%", "YouTube views 17%", "Televote 33%")

png(filename="success_pie_with_labels.png", bg = "transparent")
pie(slices,labels = lbls, col=hcl.colors(length(lbls), palette = "Heat 2"),
    main="Weights of success factors")
dev.off()
png(filename="success_pie_without_labels.png", bg = "transparent")
pie(slices, labels=c("","","",""), col=hcl.colors(length(lbls), palette = "Heat 2"))
dev.off()