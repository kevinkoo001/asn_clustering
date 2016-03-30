# First set the directory where 'data.csv' and this script are stored
# > setwd('D:/your/dir/somewhere/')
# > getwd()
# > source('georouting.R', print.eval  = TRUE)

readkey <- function()
{
    cat ("Press [enter] to continue")
    line <- readline()
}

# The following code for RADAR comes from R Visualization Book
RADAR <- function(x, fill=TRUE, col=c("blue", "red", "cyan","yellow","green"), alpha=0.2,
                    main="Cluster Profiles (RADAR Chart)", varname=NULL, locator=FALSE) {
      n.vars <- NCOL(x)
      n.clusters <- NROW(x)
      # min-max standardization
      std <- function(x)
          sx <- (x - min(x)) / diff(range(x)) + 0.5
      sx <- apply(x, 2, std)

      # Setting for generating a graph
      max.value <- max(sx)
      limit <- 25 * max.value / 20

      # Color setting
      cols <- col2rgb(col)/255
      cols <- rgb(cols[1,], cols[2, ], cols[3, ], alpha=alpha)

      op <- par()
      on.exit(par(op))

      # Basic graph
      plot.new()
      par(mar = c(0.5, 0.5, 1.5, 2))
      plot.window(xlim = c(-limit, limit), ylim = c(-limit, limit), asp = 1)

      # Print a score for each variable
      for (i in 1:n.clusters) {
          temp <- sx[i, ]
          theta <- seq(0, length = n.vars, by = 2 * pi/n.vars)
          x <- temp * cos(theta)
          y <- temp * sin(theta)

          # Print the scores the of variables
          if (fill) polygon(x, y, col = cols[i])
          else polygon(x, y, col = col[i], density = 0, lwd = 2, lty = i)
      }
      segments(0, 0, max.value * cos(theta), max.value * sin(theta), lty = "dotted", lwd = 0.8)
     
      # Draw a circle
      base.score <- seq(0, max.value, length=5)[-c(1, 5)]

      # Draw base circles (25, 50, 75, 100)
      phi <- seq(3, 360 - 3, length = 72) * (pi/180)
      for (r in base.score)
          lines(r * cos(phi), r * sin(phi), lty = "dotted")
      lines(max.value * cos(phi), max.value * sin(phi))

      # Print a base score guide
      pos <- c(base.score, max.value)
      text(pos, rep(0, length(pos)), c(25, 50, 75, 100))

      # Print variable names
      varname <- if (is.null(varname)) names(x) else varname
      text(25 * max.value / 20 * cos(theta), 23 * max.value / 20 * sin(theta), varname, cex=.8)
      title(main=main)
      legends <- paste("Cluster", 1:n.clusters)

      # Print legends
      if (locator) {
          if (fill) legend(locator(1), legends, fill=cols[1:length(legends)],  cex=.8)
          else legend(locator(1), legends, lty=1:length(legends), col=col, cex=.8)
      }
      else {
          if (fill) legend("topright", legends, fill=cols[1:length(legends)],  cex=.8)
          else legend("topright", legends, lty=1:length(legends), col=col, cex=.8)
      }
  }

# Standard normalization 
stand_norm <- function(data) {
    scaled <- scale(data)
    return(scaled)
}

# Scaled to [0-1]
zero_one_norm <- function(data) {
    scaled <- (data - min(data)) / (max(data) - min(data))
    return(scaled)
}

# Get top/bottom 5 spikes
print_outliers <- function(data, kind) {
    cat (kind, '\n')
    tops <- sort(data)[(length(data)-4): length(data)]
    bottoms <- sort(data)[1:5]
    cat ('[TOP5]   ', tops, '\n')
    cat ('[BOTTOM5]', bottoms, '\n')
}
  
# Leave One Out Cross Validation w/o regularization (lambda estimation)
loocv1 <- function(data) {
    sse <- 0
    ccs <- nrow(data)
    library(DAAG)
    for(i in 1:ccs)
    {
        loo_data <- data[c(-i),]
        #fit <- lm(loo_data$fhi ~ loo_data$n_foreign_asns + loo_data$n_asns_out + loo_data$radius + loo_data$density + loo_data$avg_degree + loo_data$avg_path_len + loo_data$modularity + loo_data$comm_no)
        cvlm <- CVlm(data=loo_data, form.lm = formula(fhi ~ n_foreign_asns + n_asns_out + radius + density + avg_degree + avg_path_len + modularity + comm_no), m=129, dots= FALSE, seed=29, plotit=FALSE, printit=TRUE)
        sse[i] <- sum((cvlm$fhi - cvlm$Predicted) ^ 2)
    }
    return(sse)
}
  
  
# Read the data from a file
georouting <- read.table("geodata.csv", sep=",", header=FALSE)

# Define row/col names
colnames(georouting) <- c("cc", "fhi", "di", "rwbi", "n_foreign_asns", "n_asns_out", "avg_sp", "diameter", "radius", "density", "avg_degree", "avg_path_len", "modularity", "comm_no", "gdp", "emp_r", "internet_users")
row_names <- c("United Arab Emirates", "Afghanistan", "Albania", "Armenia", "Angola", "Argentina", "Austria", "Australia", "Azerbaijan", "Bangladesh", "Belgium", "Bulgaria", "Bahrain", "Benin", "Brazil", "Bhutan", "Botswana", "Belarus", "Canada", "Switzerland", "Cote dIvoire", "Chile", "Cameroon", "China", "Colombia", "Costa Rica", "Cyprus", "Czech Republic", "Germany", "Denmark", "Dominican Republic", "Algeria", "Ecuador", "Estonia", "Egypt", "Spain", "Finland", "Fiji", "France", "United Kingdom of Great Britain and Northern Ireland", "Georgia", "Ghana", "Gambia", "Equatorial Guinea", "Greece", "Guatemala", "Hong Kong", "Honduras", "Croatia", "Haiti", "Hungary", "Indonesia", "Ireland", "Israel", "India", "Iraq", "Iran, Islamic Republic of", "Iceland", "Italy", "Jamaica", "Jordan", "Japan", "Kenya", "Kyrgyzstan", "Cambodia", "Korea, Republic of", "Kuwait", "Kazakhstan", "Lao Peoples Democratic Republic", "Lebanon", "Sri Lanka", "Lithuania", "Luxembourg", "Latvia", "Morocco", "Montenegro", "Madagascar", "Myanmar", "Mongolia", "Mauritania", "Malta", "Malawi", "Mexico", "Malaysia", "Mozambique", "Mauritius", "Namibia", "Nigeria", "Netherlands", "Norway", "Nepal", "New Zealand", "Oman", "Panama", "Peru", "Papua New Guinea", "Philippines", "Pakistan", "Poland", "Portugal", "Paraguay", "Qatar", "Romania", "Serbia", "Russian Federation", "Rwanda", "Saudi Arabia", "Sudan", "Sweden", "Singapore", "Slovenia", "Slovakia", "Senegal", "Swaziland", "Thailand", "Tajikistan", "Tunisia", "Turkey", "Trinidad and Tobago", "Tanzania, United Republic of", "Ukraine", "Uganda", "United States of America", "Uruguay", "Uzbekistan", "Venezuela, Bolivarian Republic of", "Viet Nam", "South Africa", "Zambia", "Zimbabwe")
rownames(georouting) <- row_names

cat ("SUMMARY of GEOROUTING DATA\n")
summary(georouting[-1])

geo_idxes <- subset(georouting, select=c(2,3,4,15,16,17))
geo_feats <- georouting[5:14]

cat ("\nTop/Bottom 5 Spikes\n")
print_outliers(georouting$fhi, "FHI")
print_outliers(georouting$di, "DI")
print_outliers(georouting$rwbi, "RWBI")
print_outliers(georouting$n_foreign_asns, "# of foreign ASNs")
print_outliers(georouting$n_asns_out, "# of ASNs outward")
print_outliers(georouting$avg_sp, "Shortest Path")
print_outliers(georouting$diameter, "Diameter")
print_outliers(georouting$radius, "Radius")
print_outliers(georouting$density, "Density")
print_outliers(georouting$avg_degree, "Degree")
print_outliers(georouting$avg_path_len, "Average Path")
print_outliers(georouting$modularity, "Modularity")
print_outliers(georouting$gdp, "GDP")
print_outliers(georouting$emp_r, "Employment Rate")
print_outliers(georouting$internet_users, "Internet users Rate")

# Boxplot to see the distribution at a glance (Normal Dist.)
op <- par(no.readonly = TRUE)
par(mfrow=c(4,4))

boxplot(stand_norm(georouting$fhi), main="FHI")
boxplot(stand_norm(georouting$di), main="DI")
boxplot(stand_norm(georouting$rwbi), main="RWBI")
boxplot(stand_norm(georouting$gdp), main="GDP")
boxplot(stand_norm(georouting$emp_r), main="Employment Rate")
boxplot(stand_norm(georouting$internet_users), main="Internet users Rate")
boxplot(stand_norm(georouting$n_foreign_asns), main="# of foreign ASNs")
boxplot(stand_norm(georouting$n_asns_out), main="# ASNs out")
boxplot(stand_norm(georouting$avg_sp), main="Shortest Path on Avg per Node")
boxplot(stand_norm(georouting$diameter), main="Diameter")
boxplot(stand_norm(georouting$radius), main="Radius")
boxplot(stand_norm(georouting$density), main="Density")
boxplot(stand_norm(georouting$avg_degree), main="Avg Degree")
boxplot(stand_norm(georouting$avg_path_len), main="Path Length")
boxplot(stand_norm(georouting$modularity), main="Modularity")
#title("Boxplot to see the distribution of indexes and features (std norm)", outer=TRUE)

readkey()
par(op)

# Boxplot to see the distribution at a glance (0-1 scaled)
op <- par(no.readonly = TRUE)
par(mfrow=c(2,1))
boxplot(zero_one_norm(georouting$fhi), zero_one_norm(georouting$di), zero_one_norm(georouting$rwbi), 
        zero_one_norm(georouting$gdp), zero_one_norm(georouting$emp_r), 
        zero_one_norm(georouting$internet_users),
        names=c("FHI", "DI", "RWBI", "GDP", "Emp Rate", "Intnt Users"), 
        notch=TRUE, col=(c("red", "green", "blue", "red", "green", "blue")), 
        pars = list(boxwex = 0.9, staplewex = 0.5, outwex = 0.5), cex.axis=0.8, tck=-.01,
        xlab="Indexes", ylab="0-1 scaled value", main="Distribution of Indexes  (0-1 Scaled)")

boxplot(zero_one_norm(georouting$n_foreign_asns), zero_one_norm(georouting$n_asns_out),
        zero_one_norm(georouting$avg_sp), zero_one_norm(georouting$diameter),
        zero_one_norm(georouting$radius), zero_one_norm(georouting$density), 
        zero_one_norm(georouting$avg_degree), zero_one_norm(georouting$avg_path_len), 
        zero_one_norm(georouting$modularity), las=2, pars = list(boxwex = 0.9, staplewex = 0.5, outwex = 0.5),
        cex.axis=0.7, tck=-.01,
        names=(c("Foreign ASNs", "ASNs outward", 
        "Shortest Path", "Diameter", "Radius", "Density", "Degree", 
        "Path Length", "Modularity")), ylab="0-1 scaled value",
        notch=TRUE, main="Distribution of Features (0-1 Scaled)")
# title("Boxplot to see the distribution of indexes and features (scaled 0-1)", outer=TRUE)

readkey()
dev.off()

# CDF plots per each indexes and features
par(mfrow=c(4,4))
plot(ecdf(georouting$fhi), xlab='FHI', ylab='cdf', main="FHI cdf")
plot(ecdf(georouting$di), xlab='DI', ylab='cdf', main="DI cdf")
plot(ecdf(georouting$rwbi), xlab='RWBI', ylab='cdf', main="RWBI cdf")
plot(ecdf(georouting$gdp), xlab='GDP', ylab='cdf', main="GDP cdf")
plot(ecdf(georouting$emp_r), xlab='Emp. rate', ylab='cdf', main="Emp. Rate cdf")
plot(ecdf(georouting$internet_users), xlab='Itnt users', ylab='cdf', main="Internet Users cdf")
plot(ecdf(log(georouting$n_foreign_asns)), xlab='LOG(# of foreign ASNs)', ylab='cdf', main="# of foreign ASNs cdf")
plot(ecdf(log(georouting$n_asns_out)), xlab='LOG(ASNs outward)', ylab='cdf', main="# ASNs with outside world cdf")
plot(ecdf(georouting$avg_sp), xlab='shortest path', ylab='cdf', main="Shortest Path cdf")
plot(ecdf(georouting$diameter), xlab='diameter', ylab='cdf', main="Diameter cdf")
plot(ecdf(georouting$radius), xlab='radius', ylab='cdf', main='Radius cdf')
plot(ecdf(georouting$density), xlab='density', ylab='cdf', main='Density cdf')
plot(ecdf(georouting$avg_degree), xlab='degree', ylab='cdf', main="Avg Degree cdf")
plot(ecdf(georouting$avg_path_len), xlab='Path Len', ylab='cdf', main="Path Length cdf")
plot(ecdf(georouting$modularity), xlab='modurality', ylab='cdf', main="Modularity cdf")
#title("CDF plots for all indexes and features", outer=TRUE)


# Calculate all corelationship coefficients
cat ("Corelationship Coefficients btn Indexes and Features\n")
cor(geo_idxes, geo_feats)

readkey()
dev.off()

# Choose the best number of clusters for K-means
#geo_feats_scaled <-scale(geo_feats)

n_foreign_asns <-zero_one_norm(geo_feats$n_foreign_asns)
n_asns_out <- zero_one_norm(geo_feats$n_asns_out)
avg_sp <- zero_one_norm(geo_feats$avg_sp)
diameter <- zero_one_norm(geo_feats$diameter)
radius <- zero_one_norm(geo_feats$radius)
density <- zero_one_norm(geo_feats$density)
avg_degree <- zero_one_norm(geo_feats$avg_degree)
avg_path_len <- zero_one_norm(geo_feats$avg_path_len)
modularity <- zero_one_norm(geo_feats$modularity)
comm_no <- zero_one_norm(geo_feats$comm_no)

geo_feats_scaled <- data.frame(n_foreign_asns, n_asns_out, avg_sp, diameter, radius, density, avg_degree, avg_path_len, modularity, comm_no)

wss <- 0
for (i in 1:15) {
     wss[i]<-sum(kmeans(geo_feats_scaled, centers=i)$withinss)
}
plot(1:15, wss, type="b", xlab="# of clusters", ylab="Within cluster sum of squares by cluster")

# Check out the result of K-means for different centers
cat ("K-Means test where there are 4-6 centers\n")
kmeans(geo_feats_scaled, centers=4)
kmeans(geo_feats_scaled, centers=5)
kmeans(geo_feats_scaled, centers=6)

readkey()
dev.off()

# Draw a dendogram using 4 different methods
rownames(geo_feats_scaled) <- row_names
distance<-dist(geo_feats_scaled)

hc1<-hclust(distance, method="single")      # Single linkage
plot(hc1, main="Cluster dendrogram with single linkage")
rect.hclust(hc1, k=5, border="red")
cutree(hc1, 5)
readkey()
dev.off()

hc2<-hclust(distance, method="complete")    # Complete linkage
plot(hc2, main="Cluster dendrogram with complete linkage")
rect.hclust(hc2, k=5, border="red")
cutree(hc2, 5)
readkey()
dev.off()

hc3<-hclust(distance, method="centroid")    # Btn centroids
plot(hc3, main="Cluster dendrogram with centroids method")
rect.hclust(hc3, k=5, border="red")
cutree(hc3, 5)
readkey()
dev.off()

hc4<-hclust(distance, method="average")     # Pairwise between all nodes + average
plot(hc4, main="Cluster dendrogram with average method")
rect.hclust(hc4, k=5, border="red")
cutree(hc4, 5)
readkey()
dev.off()

# Plot the result of K-means for 5 clusters
geo_idxes_scaled <- geo_idxes
geo_idxes_scaled$gdp <- zero_one_norm(geo_idxes$gdp)
geo_idxes_scaled$emp_r <- zero_one_norm(geo_idxes$emp_r)
geo_idxes_scaled$internet_users <- zero_one_norm(geo_idxes$internet_users)
fit <- kmeans(geo_feats_scaled, centers=5)
cluster.mean <- aggregate(geo_feats_scaled, by=list(fit$cluster), FUN=mean)

plot(geo_idxes_scaled, main="Relationships by Indexes", pch = fit$cluster, col = fit$cluster)
readkey()
dev.off()

plot(geo_feats_scaled, main="Relationships by Features", pch = fit$cluster, col = fit$cluster)
readkey()
dev.off()

geo_all_scaled <- geo_feats_scaled
geo_all_scaled$fhi <- geo_idxes_scaled$fhi
geo_all_scaled$di <- geo_idxes_scaled$di
geo_all_scaled$rwbi <- geo_idxes_scaled$rwbi
geo_all_scaled$gdp <- geo_idxes_scaled$gdp
geo_all_scaled$emp_r <- geo_idxes_scaled$emp_r
geo_all_scaled$internet_users <- geo_idxes_scaled$internet_users

# Plot radar to profile the contribution of each feature for clustering
RADAR(cluster.mean[, -1])

readkey()
dev.off()


# Linear Regression Model
# Removed the features that have the dependency: avg_sp, diameter (due to avg_path_len)
#geo_all_scaled$index <- c((geo_idxes_scaled$fhi + geo_idxes_scaled$di + geo_idxes_scaled$rwbi + geo_idxes_scaled$gdp + geo_idxes_scaled$emp_r + geo_idxes_scaled$internet_users)/6)

#lmfit <- lm(georouting$index ~ georouting$n_foreign_asns + georouting$n_asns_out + georouting$avg_sp + georouting$diameter + georouting$radius + georouting$density + georouting$avg_degree + georouting$avg_path_len + georouting$modularity + georouting$comm_no)

#lmfit <- lm(geo_all_scaled$fhi ~ geo_all_scaled$n_foreign_asns + geo_all_scaled$n_asns_out + geo_all_scaled$radius + geo_all_scaled$density + geo_all_scaled$avg_degree + geo_all_scaled$avg_path_len + geo_all_scaled$modularity + geo_all_scaled$comm_no)

#layout(matrix(c(1,2,3,4),2,2))
#summary(lmfit)    # show results
#plot(lmfit)       # Diagnostic Plots

sse <- loocv1(geo_all_scaled)
histogram(sse)


# K-fold Cross Validation where k=5
#CVlm(data=georouting, form.lm = formula(index ~ n_foreign_asns + n_asns_out + avg_sp + diameter + radius + density + avg_degree + avg_path_len + modularity + comm_no), m=5, dots= FALSE, seed=29, plotit=TRUE, printit=TRUE)

#CVlm(data=geo_all_scaled, form.lm = formula(fhi ~ n_foreign_asns + n_asns_out + radius + density + avg_degree + avg_path_len + modularity + comm_no), m=130, dots= FALSE, seed=29, plotit=TRUE, printit=TRUE)