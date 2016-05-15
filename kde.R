# KDE
plot(d, ylim=c(0,0.1), xlim=c(-30, 45), main="",  xaxt="n")
par(new=TRUE)
plot(d_old, ylim=c(0,0.1), xlim=c(-30, 45), main="")
polygon(d, col=rgb(1, 0, 0,0.3))
polygon(d_old, col=rgb(0, 1, 1,0.3))
legend("topleft", ncol=1, c("Added AUC of robustness features", "Previous set of features"), fill=c(rgb(1, 0, 0,0.3), rgb(0, 1, 1,0.3)), title="KDE of prediction error of DT", bty="n", cex=1.5, inset=0.05, xjust = 1, yjust = 1)
title(main="KDE of prediction error")
mtext(text='Prediction Error',side=1,line=2, cex=1.5)
mtext(text='Density',side=2,line=2, cex=1.5)

