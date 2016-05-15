#########################################################
# Function for normalization scaled to [0-1]
#########################################################
zero.one.norm <- function(data) {
  scaled <- (data - min(data)) / (max(data) - min(data))
  return(scaled)
}

#########################################################
# Plot various feature plots per each feature
#########################################################
feature.plot <- function(y, data) {
  par(mfrow=c(2,2))
  for(i in names(data)) {
    t_scatter <- paste("Scatterplot of", i, sep=" ")
    t_density <- paste("Density of", i, sep=" ")
    t_hist <- paste("Histogram of", i, sep=" ")
    t_cdf <- paste("CDF of", i, sep=" ")
    t_boxplot <- paste("Boxplot of", i, "Scaled (0-1)", sep=" ")
    
    plot(data[[i]], y, main=t_scatter, xlab=i, ylab="FHI (2012)")
    abline(lm(y~data[[i]]), col="red")
    
    hist(log(data[[i]]), main=t_hist, xlab=i, breaks=20, prob=TRUE)
    plot(density(log(data[[i]])), xlab=i, ylab="Density", main=t_density)

    x <- log(data[[i]])
    plot(ecdf(x), xlim=c(min(x[x!=min(x)]), max(x[x!=max(x)])), main=t_cdf, xlab=i)
  }
}

#########################################################
# Corelationship Coefficient Dotchart
#########################################################
coeff.features <- function(cor_coeff, cor_coeff_sort) {
  dotchart(cor_coeff_sort, cex=.7, main="Distribution of Corelationship Coefficients per Feature", xlab="FHI")
  abline(v=0.2, untf=FALSE, col="gray60")
  abline(v=-0.2, untf=FALSE, col="gray60")
}

#########################################################
# Correlationship panel at a glance
# http://personality-project.org/r/r.graphics.html
#########################################################
panel.cor <- function(x, y, digits=2, prefix="", cex.cor)
{
  usr <- par("usr"); on.exit(par(usr))
  par(usr = c(0, 1, 0, 1))
  r = (cor(x, y))
  txt <- format(c(r, 0.123456789), digits=digits)[1]
  txt <- paste(prefix, txt, sep="")
  if(missing(cex.cor)) cex <- 0.8/strwidth(txt)
  text(0.5, 0.5, txt, cex=cex*0.8)
}

#########################################################
# Leave One Out Cross Validation with Linear Regression
#########################################################
loocv.lr <- function(geodata) {
  library(DAAG)
  
  spe <- 0
  perr <- 0
  
  for(i in 1:nrow(geodata))
  {
    loo_data <- geodata[c(-i),]

    pred.cc <- geodata[i,]
    fit.lm <- lm(fhi_12 ~ ., method="anova", data=loo_data)

    pred_v <- predict(fit.lm, newdata=pred.cc, interval="prediction", level=0.95)
    real_v <- geodata[i,]$fhi_12
    
    square_err <- (pred_v - real_v)^2
    #cat (pred_v, real_v, square_err, '\n')
    spe[i] <- square_err
    perr[i] <- pred_v - real_v
  }
  
  return(perr)
}

#########################################################
# Draw partition trees per feature
#########################################################
part.feature <- function(geo) 
{
  for(feature in names(geo)) {
    if(feature != 'fhi_12') {
      par(mfrow=c(1,2))
      title <- paste("Partition tree of", feature, sep=" ")
      tree.model <- tree(fhi_12~geo[[feature]], geo)
      plot(tree.model, main=title)
      text(tree.model, cex=.7)
      plot(geo[[feature]], geo$fhi_12, main=title, xlab=feature, ylab="FHI (2012)")
      partition.tree(tree.model, add=TRUE, col="red")
    }
  }
}

#########################################################
# Leave One Out Cross Validation with Regression Tree
#########################################################
loocv.rt <- function(geodata) {
  library(rpart)
  library(rpart.plot)
  
  perr <- 0   # prediction error
  spe <- 0    # square prediction error

  for(i in 1:nrow(geodata))
  {
    loo_data <- geodata[c(-i),]
    pred.cc <- geodata[i,]
    rpart.fit <- rpart(fhi_12 ~ ., method="anova", data=loo_data)
    pred_v <- predict(rpart.fit, newdata=pred.cc, interval="prediction", level=0.95)
    real_v <- geodata[i,]$fhi_12
    square_err <- (pred_v - real_v)^2
    #cat (pred_v, real_v, square_err, '\n')
    spe[i] <- square_err
    perr[i] <- pred_v - real_v
  }
  
  return(perr)
}

#########################################################
# Linear Regression with regularization (Ridge or LASSO)
#########################################################
loocv.lr.reg <- function(kind, lambdas, x, y, b.no, lambda.plt) {
  library(glmnet)
  
  if (kind == 'Ridge') {
    type = 0
  }
  else if (kind == 'LASSO') {
    type = 1
  }
  else {
    cat("Wrong regularization method!!")
    quit("yes")
  }
  
  # Cross-validation (LOOCV) for picking up the best lambda
  set.seed(10)
  lambda.cv.out <- cv.glmnet(x,y, alpha=type, grouped=FALSE)
  if (b.no == 0) {
    xlab_reg = paste("log(Lambda)", "using", kind, "globally", sep=" ")
  }
  else {
    xlab_reg = paste("log(Lambda)", "using", kind, "in", "Bucket", b.no, sep=" ")
  }

  if (lambda.plt == TRUE) {
    par(mfrow=c(1,1))
    plot(lambda.cv.out, xlab=xlab_reg)
  }
  
  best.lambda <- lambda.cv.out$lambda.min
  final.model <- glmnet(x, y, alpha=type, lambda = best.lambda)
  
  cat("Best lambda with", kind, best.lambda, "\n")
  
  # Best coefficients from the best lambda value
  pred.coeffs <- predict(final.model, type="coefficients", s=best.lambda)[2:ncol(x)+1,]
  cat ("Predicted coefficients:", pred.coeffs[2:length(pred.coeffs)], "\n")
  
  # Make predictions
  fit <- glmnet(x, y, family="gaussian", alpha=type, lambda=best.lambda)
  pred.values <- predict(fit, x, type="link")
  cat ("Predictions", pred.values, "\n")
  
  # Calculate mean square errors of prediction
  pse <- (y - pred.values)^2
  perr <- pred.values - y

  return (perr)
}


###################################################################
###################################################################
##                  MAIN WORKFLOW
## (-) Data normalized, and global outliers removed
## (0) Global linear regression without regularization
## (1) Global linear regression with LASSO
## (2) Regression tree with leaf-averages
## (x) Regression tree with linear-regression at the leaves 
##     using root-to-leaf intermediate features
## (3) Regression tree with linear-regression at the leaves 
##     using all features with LASSO
###################################################################
###################################################################


#########################################################
# A. Initialization for processing
#########################################################

# Read the data from a file
#DATAFILE <- "geodata5.csv" # "features_rachee.csv"
DATAFILE <- "feature_may14.csv" # "features_rachee.csv"

geodata <- read.table(DATAFILE, sep=",", header=TRUE)

# Define row/col names and subset of data
rownames(geodata) <- geodata$cn #ADJUSTED
subset.col1 = c("fhi_12", "ip_density", "diameter", "percentile_cust_cone", "percentile_degree", 
               "stub_count", "num_intl_countries", "tot_peer_edges", "num_edges", "num_nodes", 
               "num_large_providers", "avg_deg", "num_intl_nodes", "num_large_nodes", 
               "num_announced_ip", "max_h_im", "max_p_len", "max_v_im")

subset.col2 = c("fhi_12", "ip_density", "diameter", "percentile_cust_cone", 
                "percentile_degree", "stub_count", "num_intl_countries", 
                "tot_peer_edges", "num_edges", "num_nodes", "num_large_providers", 
                "avg_deg", "num_intl_nodes", "num_large_nodes", "num_announced_ip", 
                "avg_h_im", "max_p_len", "avg_v_im", "max_load_cen",
                "avg_clustering", "graph_clique_number", "transitivity",
                "alg_conn", "frac_conn")

geo_subset <- subset(geodata, select=subset.col2) #ADJUSTED


#########################################################
# B. Basic Information for georouting data
#########################################################

# Plot scatterplot/cdf/pdf/histogram per each feature
#fhi <- subset(geodata, select=c("fhi_12"))[,1:1]
#features <- geo_subset[, -1]
#feature.plot(fhi, features)

# Draw the Distribution of Corelationship Coefficients for all features
#par(mfrow=c(1,1))
#cor_coeff <- cor(features, fhi)
#coeff.features(cor_coeff, cor_coeff[order(cor_coeff),])

# Get the Scatterplot Matrices
#pairs(~., data=geo_subset, lower.panel=panel.smooth, upper.panel=panel.cor, main="Scatterplot Matrix for all features")


#########################################################
# (0) Global linear regression without regularization
#########################################################
global.pse.lm <- loocv.lr(geo_subset)
global.pse.lm <- data.matrix(global.pse.lm)
colnames(global.pse.lm) <- c('global.pse.lm')
cat ("(0) Mean(PSE) in LR: ", mean(global.pse.lm), "\n")


#########################################################
# (1) Global linear regression with LASSO
#########################################################

# Ranges [10^-4:10^1]
lambda.candidates = 10^(seq(1,-4,length=100))

xx <- model.matrix(fhi_12~., data=geo_subset)[,-1]
yy <- geo_subset$fhi_12

global.pse.lasso <- loocv.lr.reg('LASSO', lambda.candidates, xx, yy, 0, FALSE)
colnames(global.pse.lasso) <- c('global.pse.lasso')
cat ("(1) Mean(PSE) in LR with LASSO: ", mean(global.pse.lasso), "\n")


#########################################################
# (2) Regression tree with leaf-averages
# "class": classification tree, "anova": regression tree
# Regression Tree: Here we use rpart package for recursive partitioning
# [References]
#   http://www.di.fc.ul.pt/~jpn/r/tree/tree.html
#   http://www.statmethods.net/advstats/cart.html
#########################################################

library(rpart)
library(rpart.plot)
library(partykit)

fit <- rpart(fhi_12 ~ ., method="anova", data=geo_subset)
#printcp(fit)

par(mfrow=c(1,1))
prp(fit, type=2, extra=100, tweak=.8, xcompact=TRUE, ycompact=TRUE)

rpart.tree <- as.party(fit)
plot(rpart.tree, which.plot=2, cex=0.8)

par(mfrow=c(1,3))
plotcp(fit)
rsq.rpart(fit)

# How to tabulate some of the data with a condition
# table(subset(geodata, ip_density<0.44)$num_node)

# Leave one out Regression Tree
#   For each country, leave it out when generating partition with regression tree
#   For each model, predict the FHI of the country that has been left out
#   For each country, compute the square prediction error (i.e., spe=(pred-real)^2)
#   Sort out all SPEs and plot them for all countries

rt.pse.avg <- loocv.rt(geo_subset)
rt.pse.avg <- data.matrix(rt.pse.avg)

colnames(rt.pse.avg) <- c('rt.pse.avg')
rt.pse.avg.sorted <- rt.pse.avg[order(rt.pse.avg),]

par(mfrow=c(1,3))
num.cc <- length(rt.pse.avg.sorted)
cat ("(3) Mean(PSE) of LOORT: ", mean(rt.pse.avg), "\n")

# Draw three dot charts per country
dotchart(rt.pse.avg.sorted[1:as.integer(num.cc/3)], cex=.7, main="Prediction Square Errors per Country (1)", xlab="PSE")
dotchart(rt.pse.avg.sorted[as.integer(num.cc/3+1):as.integer(num.cc/3*2)], cex=.7, main="Prediction Square Errors per Country (2)", xlab="PSE")
dotchart(rt.pse.avg.sorted[as.integer(num.cc/3*2+1):num.cc], cex=.7, main="Prediction Square Errors per Country (3)", xlab="PSE")


#########################################################
## (3) Regression tree with linear-regression at the leaves 
##     using root-to-leaf intermediate features
#########################################################

# TO-DO MANUALLY HERE
# Node 6 (n=14)
# subset(geodata[c("Argentina","Bangladesh","Colombia","Iran","Jordan","Kyrgyzstan","Kuwait","Kazakhstan","Mauritania","Mexico","Pakistan","Qatar","Sudan","Tunisia"),], select=c("ip_density", "max_p_len", "percentile_degree", "transitivity"))
# Node 16 (n=16)
# subset(geodata[c("Afghanistan","Burkina Faso","Burundi","Brunei Darussalam","Congo","Cote dIvoire","Cameroon","Gabon","Guinea","Haiti","Liberia","Lesotho","Niger","Senegal","Chad","Togo"),],select=c("ip_density", "max_p_len", "num_nodes", "avg_deg", "max_cen", "max_load_cen", "tot_peer_edges", "num_intl_nodes"))
# Node 17 (n=14)
# subset(geodata[c("Angola","Bosnia and Herzegovina","Bhutan","Botswana","Egypt","Jamaica","Lebanon","Sri Lanka","Madagascar","Mongolia","Maldives","Malawi","Nigeria","Papua New Guinea"),], select=c("ip_density", "max_p_len", "num_nodes", "avg_deg", "max_cen", "max_load_cen", "tot_peer_edges", "num_intl_nodes"))
# Node 18 (n=24)
# subset(geodata[c("Albania","Benin","Bolivia","Congo, DR","Dominican Republic","Algeria","Ecuador","Fiji","Ghana","Guatemala","Honduras","Mozambique","Nicaragua","Nepal","Panama","Peru","Paraguay","Sierra Leone","El Salvador","Tajikistan","Trinidad and Tobago","Tanzania","Samoa","Zambia"),], select = c("ip_density", "max_p_len", "num_nodes", "avg_deg", "max_cen"))
# Node 19 (n=16)
# subset(geodata[c("Armenia","Brazil","Indonesia","India","Kenya","Malaysia","Namibia","Philippines","Romania","Serbia","Slovakia","Thailand","Ukraine","Uganda","Vanuatu","South Africa"),], select=c("ip_density", "max_p_len", "num_nodes", "avg_deg"))
# Node 22 (n=38); only ip_density


#########################################################
## (4) Regression tree with linear-regression at the leaves 
##     using all features with LASSO
#########################################################

buckets <- fit$where
bucket_no<-unique(buckets)
bdf <- as.data.frame(buckets)

rt.pse.full <- NULL

for(i in 1:length(bucket_no)) {
  cc_bucket = rownames(bdf)[bdf$buckets==bucket_no[i]]
  cat ("\nBucket", bucket_no[i], "(", length(cc_bucket), "Countries)", "\n")
  cat (cc_bucket, "\n")
  
  bucket_data <- NULL
  for (j in 1:length(cc_bucket)) {
    bucket_data<-rbind(geodata[cc_bucket[j],], bucket_data)
  }
  
  bucket_data<-bucket_data[,-1:-2] #ADJUSTED
  
  if (nrow(bucket_data) > 0) {
    # Linear Regression without regularization
    # lm.out <- lm(zero.one.norm(fhi_12)~., data=bucket_data)
    # lm_summary <- summary(lm.out)
    # par(mfrow=c(2,2))
    # plot(lm.out)
    
    x <- model.matrix(fhi_12~., data=bucket_data)[,-1]
    y <- bucket_data$fhi_12
    
    mse <- loocv.lr.reg('LASSO', lambda.candidates, x, y, bucket_no[i], FALSE)
    rt.pse.full <- c(rt.pse.full, mse)
    rt.pse.full <- data.matrix(rt.pse.full)
    colnames(rt.pse.full) <- c('rt.pse.full')
    
  }
  
  #cat("Residuals\n", lm_summary$residuals, "\n")
  #cat("Coefficients\n", lm_summary$coefficients, "\n")
  #cat("R^2 value:", lm_summary$r.squared, "\n")
  
}

cat ("(4) Mean(PSE) of LR at each bucket of RT: ", mean(rt.pse.full), "\n")


#########################################################
# Keep track of PSE (Prediction Square Errors) per each
#########################################################

par(mfrow=c(2,4))
hist(global.pse.lm, breaks=20, main="(0) PSE for global L/R \nwithout regularization")
hist(global.pse.lasso, breaks=20,main="(1) PSE for global L/R \nwith LASSO")
hist(rt.pse.avg, breaks=20,main="(2) PSE for R/T \nwith leaf-averages")
#hist(rt.pse.part, main="(3) PSE for R/T with L/R \n(root-leaf features) at the leaves")
hist(rt.pse.full, breaks=20,main="(3) PSE for R/T with L/R \n(full features) at the leaves")

par(mfrow=c(1,1))
d_1<-density(global.pse.lm, bw="SJ")
d_2<-density(global.pse.lasso,  bw="SJ")
d_3<-density(rt.pse.avg,  bw="SJ")
d_4<-density(rt.pse.full,  bw="SJ")
plot(d_1, ylim=c(0,0.06), xlim=c(-80, 70), main="",  xaxt="n", xlab="", ylab="")
par(new=TRUE)
plot(d_2, ylim=c(0,0.06), xlim=c(-80, 70), main="",xaxt="n", xlab="", ylab="")
par(new=TRUE)
plot(d_3, ylim=c(0,0.06), xlim=c(-80, 70), main="",xaxt="n", xlab="", ylab="")
par(new=TRUE)
plot(d_4, ylim=c(0,0.06), xlim=c(-80, 70), main="", xlab="", ylab="")
polygon(d_1, col=rgb(1, 0, 0,0.3))
polygon(d_2, col=rgb(0, 1, 1,0.3))
polygon(d_3, col=rgb(1, 1, 0,0.3))
polygon(d_4, col=rgb(0, 1, 0,0.3))
legend("topleft", ncol=1, c("LR (no regularisation)", "LASSO LR", "Decision Tree (leaf avg)", "Decision Tree (LR in leaves)"), fill=c(rgb(1, 0, 0,0.3), rgb(0, 1, 1,0.3), rgb(1, 1, 0,0.3),rgb(0, 1, 0,0.3)) , title="KDE of prediction error of DT", bty="n", cex=1.5, inset=0.05, xjust = 1, yjust = 1)

title(main="KDE of prediction error")
mtext(text='Prediction Error',side=1,line=2, cex=1.5)
mtext(text='Density',side=2,line=2, cex=1.5)

plot(d, main="Kernel Density of Error", ylim=c(0,0.1))
polygon(d, col="red", border="blue")
plot(ecdf(global.pse.lm), main="CDF of Case (0)", xlab="PSE", ylab="CDF")
plot(ecdf(global.pse.lasso), main="CDF of Case (1)", xlab="PSE", ylab="CDF")
plot(ecdf(rt.pse.avg), main="CDF of Case (2)", xlab="PSE", ylab="CDF")
#plot(ecdf(rt.pse.part), main="CDF of Case (3)", xlab="PSE", ylab="CDF")
plot(ecdf(rt.pse.full), main="CDF of Case (3)", xlab="PSE", ylab="CDF")

pse_all <- cbind.data.frame(global.pse.lm, global.pse.lasso, rt.pse.avg, rt.pse.full)

# For 174 countries, and 23 features in total
# > summary(pse_all)
# global.pse.lm     global.pse.lasso      rt.pse.avg       rt.pse.full       
# Min.   :   0.00   Min.   :   0.0487   Min.   :   0.04   Min.   :   0.0003  
# 1st Qu.:  36.51   1st Qu.:  28.2135   1st Qu.:  19.34   1st Qu.:   5.4444  
# Median : 153.04   Median : 147.6377   Median :  81.02   Median :  27.2872  
# Mean   : 348.06   Mean   : 311.1351   Mean   : 273.54   Mean   :  88.4955  
# 3rd Qu.: 467.56   3rd Qu.: 532.4056   3rd Qu.: 264.53   3rd Qu.:  90.2500  
# Max.   :4769.26   Max.   :1577.1391   Max.   :2715.57   Max.   :1056.2500 

#par(mfrow=c(2,4))
#hist(log(global.pse.lm), main="(0) log(PSE) for global L/R \nwithout regularization")
#hist(log(global.pse.lasso), main="(1) log(PSE) for global L/R \nwith LASSO")
#hist(log(rt.pse.avg), main="(2) log(PSE) for R/T \nwith leaf-averages")
#hist(log(rt.pse.part), main="(3) log(PSE) for R/T with L/R \n(root-leaf features) at the leaves")
#hist(log(rt.pse.full), main="(3) log(PSE) for R/T with L/R \n(full features) at the leaves")

#plot(ecdf(log(global.pse.lm)), main="log(CDF) of Case (0)", xlab="log(PSE)", ylab="CDF")
#plot(ecdf(log(global.pse.lasso)), main="log(CDF) of Case (1)", xlab="log(PSE)", ylab="CDF")
#plot(ecdf(log(rt.pse.avg)), main="log(CDF) of Case (2)", xlab="log(PSE)", ylab="CDF")
#plot(ecdf(log(rt.pse.part)), main="log(CDF) of Case (3)", xlab="log(PSE)", ylab="CDF")
#plot(ecdf(log(rt.pse.full)), main="log(CDF) of Case (3)", xlab="log(PSE)", ylab="CDF")

par(mfrow=c(1,1))
plot(c(-40,40), c(0,1), main="CDF of Prediction Errors (Pred - FHI)", xlab="Prediction Error", ylab="CDF")
lines(ecdf(global.pse.lm), col="black")
lines(ecdf(global.pse.lasso), col="green")
lines(ecdf(rt.pse.avg), col="red")
lines(ecdf(rt.pse.full), col="blue")
legend(20, 0.2, c("global.pse.lm", "global.pse.lasso", "rt.pse.avg", "rt.pse.full"),
       lwd=c(5, 2.5), col=c("black", "green", "red", "blue"))


all_errs <- (cbind(pse_all, data.frame(geodata$fhi_12)))
actual_fhi <-all_errs$geodata.fhi_12
par(mfrow=c(1,1))
plot(c(0,3), c(0,1), main="Rate CDF (Pred over Actual FHI)", xlab="Pred/FHI", ylab="CDF")
lines(ecdf((all_errs$global.pse.lm + actual_fhi)/actual_fhi), col="black")
lines(ecdf((all_errs$global.pse.lasso + actual_fhi)/actual_fhi), col="green")
lines(ecdf((all_errs$rt.pse.avg + actual_fhi)/actual_fhi), col="red")
lines(ecdf((all_errs$rt.pse.full + actual_fhi)/actual_fhi), col="blue")
legend(2.3, 0.4, c("global.pse.lm", "global.pse.lasso", "rt.pse.avg", "rt.pse.full"),
       lwd=c(5, 2.5), col=c("black", "green", "red", "blue"))
abline(v=1.5)
abline(v=0.5)
