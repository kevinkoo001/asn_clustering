# Scaled to [0-1]
zero_one_norm <- function(data) {
  scaled <- (data - min(data)) / (max(data) - min(data))
  return(scaled)
}

# Draw various feature plots per each feature
feature_plot <- function(y, data) {
  par(mfrow=c(2,2))
  for(i in names(data)) {
    t_scatter <- paste("Scatterplot of", i, sep=" ")
    t_density <- paste("Density of", i, sep=" ")
    t_hist <- paste("Histogram of", i, sep=" ")
    t_cdf <- paste("CDF of", i, sep=" ")
    t_boxplot <- paste("Boxplot of", i, "Scaled (0-1)", sep=" ")
    
    plot(data[[i]], y, main=t_scatter, xlab=i, ylab="FHI (2012)")
    abline(lm(y~data[[i]]), col="red")
    
    hist(data[[i]], main=t_hist, xlab=i, breaks=20, prob=TRUE)

    plot(density(data[[i]]), xlab=i, ylab="Density", main=t_density)
    #densityplot(data[[i]], data=data, xlab=i, ylab="Density", main=t_density)
    
    plot(ecdf(data[[i]]), main=t_cdf, xlab=i)
    #lines(ecdf(log(data[[i]])), col="blue")
    
    #boxplot(zero_one_norm(data[[i]]), notch=TRUE, 
    #        pars = list(boxwex = 0.9, staplewex = 0.5, outwex = 0.5), cex.axis=0.8, tck=-.01,
    #        xlab=i, ylab="0-1 scaled value", main=t_boxplot)
    
    #pairs(~data[[i]]+y, data=data, main="Scatterplot matrix")

  }
}

# Corelationship Coefficient Dotchart
coeff_features <- function(cor_coeff, cor_coeff_sort) {
  dotchart(cor_coeff_sort, cex=.7, main="Distribution of Corelationship Coefficients per Feature", xlab="FHI")
  abline(v=0.2, untf=FALSE, col="gray60")
  abline(v=-0.2, untf=FALSE, col="gray60")
}

# http://personality-project.org/r/r.graphics.html
panel.cor <- function(x, y, digits=2, prefix="", cex.cor)
{
  usr <- par("usr"); on.exit(par(usr))
  par(usr = c(0, 1, 0, 1))
  r = (cor(x, y))
  txt <- format(c(r, 0.123456789), digits=digits)[1]
  txt <- paste(prefix, txt, sep="")
  if(missing(cex.cor)) cex <- 0.8/strwidth(txt)
  #text(0.5, 0.5, txt, cex = cex * abs(r))
  text(0.5, 0.5, txt, cex=cex*0.8)
}

# Draw partition trees per feature
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


DATAFILE <- "geodata3.csv"

# Read the data from a file
geodata <- read.table(DATAFILE, sep=",", header=TRUE)

# Define row/col names
rownames(geodata) <- geodata$cn

fhi <- geodata[, 3:3]
features <- geodata[,-1:-3]
feature_plot(fhi, features)

# Draw the Distribution of Corelationship Coefficients per Feature
cor_coeff <- cor(features, fhi)
cor_coeff_sort <- cor_coeff[order(cor_coeff),]
coeff_features(cor_coeff, cor_coeff_sort)

# Get the Scatterplot Matrices
#pairs(~., data=geodata[,-1:-2], main="Scatterplot Matrix")
pairs(~., data=geodata[,-1:-2], lower.panel=panel.smooth, upper.panel=panel.cor)

# Regression Tree
# References
#   http://www.di.fc.ul.pt/~jpn/r/tree/tree.html
#   http://www.statmethods.net/advstats/cart.html
library(rpart)
library(rpart.plot)
library(partykit)

# "class": classification tree, "anova": regression tree
fit <- rpart(fhi_12 ~ ., method="anova", data=geodata[,-1:-2])
prp(fit, type=2, extra=100, tweak=.8, xcompact=TRUE, ycompact=TRUE)

rpart.tree <- as.party(fit)
plot(rpart.tree, which.plot=2, cex=0.8)

part.feature(geodata[,-1:-2])

par(mfrow=c(1,3))
plotcp(fit)
rsq.rpart(fit)
