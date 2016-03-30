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
    sse <- 0
    library(DAAG)
    for(i in 1:nrow(geodata))
    {
        loo_data <- geodata[c(-i),]
        fit.lm <- lm(loo_data$fhi ~ loo_data$n_foreign_asns + loo_data$n_asns_out + loo_data$avg_sp + loo_data$radius + loo_data$density + loo_data$avg_path_len + loo_data$modularity + loo_data$comm_no + loo_data$ip_density + loo_data$diameter + loo_data$avg_pgrank + loo_data$num_intl_countries + loo_data$num_edges + loo_data$num_nodes + loo_data$num_large_providers + loo_data$avg_degree + loo_data$avg_bcen + loo_data$largest_cust_cone + loo_data$num_announced_ip + loo_data$num_intl_nodes)
        cvlm <- CVlm(data=loo_data, form.lm = formula(fhi ~ n_foreign_asns + n_asns_out + avg_sp + radius + density + avg_path_len + modularity + comm_no + ip_density + diameter + avg_pgrank + num_intl_countries + num_edges + num_nodes + num_large_providers + avg_degree + avg_bcen + largest_cust_cone + num_announced_ip + num_intl_nodes),         m=129, dots= FALSE, seed=29, plotit=FALSE, printit=TRUE)
        sse[i] <- sum((cvlm$fhi - cvlm$Predicted) ^ 2)
        # predict(fit.lm)
    }
    return(sse)
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
# SSE vector contains sum of prediction square errors per country
sse <- loocv1(geodata)
sse <- data.matrix(sse)
rownames(sse) <- geodata$cn
colnames(sse) <- c('SSE')

par(mfrow=c(1,2))
dotchart(data.matrix(sse[1:65]), labels=geodata$cc[1:65], cex=.7, main="Sum of Prediction Square Errors per Country", xlab="SPSE")
dotchart(data.matrix(sse[66:130]), labels=geodata$cc[66:130], cex=.7, main="Sum of Prediction Square Errors per Country", xlab="SPSE")

readkey()

par(mfrow=c(1,2))
hist(sse, main="SPSE Histogram", breaks=50, xlab="SPSE")
lines(density(sse)$x, density(sse)$y, col="blue", lwd=2)
plot(ecdf(sse), main="CDF of SPSE", xlab="Sum of Prediction Square Errors", ylab="CDF")

readkey()