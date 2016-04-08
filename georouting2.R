# First set the directory where 'data.csv' and this script are stored
# > setwd('D:/your/dir/somewhere/')
# > getwd()
# > source('geodata.R', print.eval  = TRUE)

readkey <- function()
{
    cat ("Press [enter] to continue")
    line <- readline()
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
loocv1 <- function(geodata) {
    spe <- 0
    library(DAAG)
    for(i in 1:nrow(geodata))
    {
        loo_data <- geodata[c(-i),]
        y <- loo_data$fhi
        x1 <- loo_data$n_foreign_asns
        x2 <- loo_data$n_asns_out
        x3 <- loo_data$avg_sp
        x4 <- loo_data$radius
        x5 <- loo_data$density
        x6 <- loo_data$avg_path_len
        x7 <- loo_data$modularity
        x8 <- loo_data$comm_no
        x9 <- loo_data$ip_density
        x10 <- loo_data$diameter
        x11 <- loo_data$avg_pgrank
        x12 <- loo_data$num_intl_countries
        x13 <- loo_data$num_edges
        x14 <- loo_data$num_nodes
        x15 <- loo_data$num_large_providers
        x16 <- loo_data$avg_degree
        x17 <- loo_data$avg_bcen
        x18 <- loo_data$largest_cust_cone
        x19 <- loo_data$num_announced_ip
        x20 <- loo_data$num_intl_nodes
        
        fit.lm <- lm(y ~ x1 + x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10 + x11 + x12 + x13 + x14 + x15 + x16 + x17 + x18 + x19 + x20)
        idx_pred <- data.frame(x1 = geodata[i,]$n_foreign_asns, x2 = geodata[i,]$n_asns_out, x3 = geodata[i,]$avg_sp, x4 = geodata[i,]$radius, x5 = geodata[i,]$density, x6 = geodata[i,]$avg_path_len, x7 = geodata[i,]$modularity, x8 = geodata[i,]$comm_no, x9 = geodata[i,]$ip_density, x10 = geodata[i,]$diameter, x11 = geodata[i,]$avg_pgrank, x12 = geodata[i,]$num_intl_countries, x13 = geodata[i,]$num_edges, x14 = geodata[i,]$num_nodes, x15 = geodata[i,]$num_large_providers, x16 = geodata[i,]$avg_degree, x17 = geodata[i,]$avg_bcen, x18 = geodata[i,]$largest_cust_cone, x19 = geodata[i,]$num_announced_ip, x20 = geodata[i,]$num_intl_nodes)

        p <- predict(fit.lm, idx_pred, interval="prediction", level=0.95)
        cat (p[1], geodata[i,]$fhi, (p[1] - geodata[i,]$fhi)^2, '\n')
        spe[i] <- (p[1] - geodata[i,]$fhi)^2
                   
        #fit.lm <- lm(loo_data$fhi ~ loo_data$n_foreign_asns + loo_data$n_asns_out + loo_data$avg_sp + loo_data$radius + loo_data$density + loo_data$avg_path_len + loo_data$modularity + loo_data$comm_no + loo_data$ip_density + loo_data$diameter + loo_data$avg_pgrank + loo_data$num_intl_countries + loo_data$num_edges + loo_data$num_nodes + loo_data$num_large_providers + loo_data$avg_degree + loo_data$avg_bcen + loo_data$largest_cust_cone + loo_data$num_announced_ip + loo_data$num_intl_nodes)
        #cvlm <- CVlm(data=loo_data, form.lm = formula(fhi ~ n_foreign_asns + n_asns_out + avg_sp + radius + density + avg_path_len + modularity + comm_no + ip_density + diameter + avg_pgrank + num_intl_countries + num_edges + num_nodes + num_large_providers + avg_degree + avg_bcen + largest_cust_cone + num_announced_ip + num_intl_nodes), m=129, dots= FALSE, seed=29, plotit=FALSE, printit=TRUE)
        #spe[i] <- sum((cvlm$fhi - cvlm$Predicted) ^ 2)
        
    }
    return(spe)
}
  
DATAFILE <- "geodata2.csv"

# Read the data from a file
geodata <- read.table(DATAFILE, sep=",", header=TRUE)
target <- geodata[,-1:-2]

# Define row/col names
rownames(geodata) <- geodata$cn
feat_names <- colnames(geodata)[-1:-2]

cat ("SUMMARY of geodata DATA\n")
summary(geodata[,-1:-2])

#geo_idxes <- subset(geodata, select=c(2,3,4,15,16,17))
#geo_feats <- geodata[5:14]


###############################
##  Features for Regression  ##
###############################

op <- par(no.readonly = TRUE)
par(mfrow=c(2,2))

# Boxplot to see the distribution of features at a glance (Scaled 0-1)
# A. Structural Features in Graph (1)
boxplot(zero_one_norm(geodata$fhi), zero_one_norm(geodata$num_nodes), zero_one_norm(geodata$num_edges), 
        zero_one_norm(geodata$avg_bcen), zero_one_norm(geodata$avg_pgrank), zero_one_norm(geodata$avg_degree),
        names=c("FHI", "Nodes", "Edges", "Betness Centrality", "Page Rank", "Degree"), 
        notch=TRUE, col=(c("red", "green", "blue", "red", "green", "blue")), 
        pars = list(boxwex = 0.9, staplewex = 0.5, outwex = 0.5), cex.axis=0.8, tck=-.01,
        xlab="Indexes", ylab="0-1 scaled value", main="Distribution of Structural Features (1)")
        
# A. Structural Features in Graph (2)
boxplot(zero_one_norm(geodata$avg_sp), zero_one_norm(geodata$radius), zero_one_norm(geodata$density), 
        zero_one_norm(geodata$modularity), zero_one_norm(geodata$comm_no), zero_one_norm(geodata$diameter),
        names=c("Shortest Path", "Radius", "Density", "Modularity", "Comm No", "Diameter"), 
        notch=TRUE, col=(c("red", "green", "blue", "red", "green", "blue")), 
        pars = list(boxwex = 0.9, staplewex = 0.5, outwex = 0.5), cex.axis=0.8, tck=-.01,
        xlab="Indexes", ylab="0-1 scaled value", main="Distribution of Structural Features (2)")

# B. International Connectivity Features
boxplot(zero_one_norm(geodata$num_intl_nodes), zero_one_norm(geodata$n_foreign_asns),
        zero_one_norm(geodata$n_asns_out), zero_one_norm(geodata$num_intl_countries), 
        zero_one_norm(geodata$avg_path_len),
        pars = list(boxwex = 0.9, staplewex = 0.5, outwex = 0.5),
        cex.axis=0.7, tck=-.01,
        names=(c("Int'l Nodes", "Int'l ASNs", "# of domestic ASNs \n connected to outside",
                "Int'l Countries", "Path Length")), 
        ylab="0-1 scaled value",
        notch=TRUE, main="Distribution of International \nConnectivity Features")
        
# C. IP Demographic/Routing/BGP Features
boxplot(zero_one_norm(geodata$ip_density), zero_one_norm(geodata$num_announced_ip),
        zero_one_norm(geodata$num_large_providers), zero_one_norm(geodata$largest_cust_cone),
        pars = list(boxwex = 0.9, staplewex = 0.5, outwex = 0.5), x.axis=0.7, tck=-.01,
        names=(c("IP Density", "Announced \nIP Prefixes", "Large Providers", 
                "Size of largest \ncustomer cone")), ylab="0-1 scaled value",
        notch=TRUE, main="Distribution of IP Demographic \n Routing/BGP Features")
        

readkey()


###############################
##     Linear Regression     ##
###############################

# Draw the Distribution of Corelationship Coefficients per Feature
y <- geodata$fhi        # y = FHI (index)
x <- geodata[,-1:-3]    # all_features
cor_coeff <- cor(x, y)
dotchart(cor_coeff, labels=row.names(cor_coeff), cex=.7, main="Distribution of Corelationship Coefficients per Feature", xlab="FHI")

readkey()

# Get the Scatterplot Matrices
D <- geodata[,-1:-2]
pairs(~D$fhi + D$n_foreign_asns + D$n_asns_out + D$avg_sp + D$radius + D$density + D$avg_path_len + D$modularity + D$comm_no + D$ip_density + D$diameter + D$avg_pgrank + D$num_intl_countries + D$num_edges + D$num_nodes + D$num_large_providers + D$avg_degree + D$avg_bcen + D$largest_cust_cone + D$num_announced_ip + D$num_intl_nodes, data=D, main="Scatterplot Matrix")

readkey()

# Leave One Out Cross Validation without Regularization
# spe vector contains sum of prediction square errors per country
spe <- loocv1(geodata)
spe <- data.matrix(spe)
rownames(spe) <- geodata$cn
colnames(spe) <- c('spe')

par(mfrow=c(1,2))
dotchart(data.matrix(spe[1:65]), labels=geodata$cc[1:65], cex=.7, main="Prediction Square Errors per Country", xlab="PSE")
dotchart(data.matrix(spe[66:130]), labels=geodata$cc[66:130], cex=.7, main="Prediction Square Errors per Country", xlab="PSE")

readkey()

par(mfrow=c(1,2))
hist(spe, main="Prediction Square Error Histogram", breaks=50, xlab="Prediction Square Errors")
lines(density(spe)$x, density(spe)$y, col="blue", lwd=2)
plot(ecdf(spe), main="CDF of PSE", xlab="Prediction Square Errors", ylab="CDF")


