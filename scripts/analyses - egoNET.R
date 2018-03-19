# Title     : TODO
# Objective : TODO
# Created by: Kyle Gerst
# Created on: 3/9/2018

rm(list = ls())
cat('\014')

for (package in c('tidyverse',
                  'psych',
                  'lme4',
                  'MASS',
                  'cowplot')) {
  if (!require(package, character.only=TRUE, quietly=TRUE)) {
    install.packages(package)
    library(package, character.only=TRUE)
  }
}

path <- getwd()
df <- read.csv(file = '../data/processed/data - net-ss3 merged - 2018-03-13.csv', header = TRUE, sep = ",")
df_long <- read.csv(file = '../data/processed/data - net-ss3 alter merged - 2018-03-13.csv', header = TRUE, sep = ",")

df['Group_Alt'] <- df$Group
df$Group_Alt[df['Group_Alt'] == 3] <- 2
df['Group_Alt'] <- recode_factor(df$Group_Alt, `1` = 'Control', `2` = 'AUD')
df['ASP_LT'] <- df['AS_PC'] + df['CD_PC']

# Bi-split of Alcohol and ASP Problem Counts
df['Alc_Grp'] <- factor(ntile(df$AL_PC, n = 2), levels = c(1,2),labels = c('Low', 'High'))
df['ASP_Grp'] <- factor(ntile(df$ASP_LT, n = 2), levels = c(1,2),labels = c('Low', 'High'))

# # Tert-split of Alcohol and ASP Problem Counts
# df['Alc_Grp'] <- factor(ntile(df$AL_PC, n = 3), levels = c(1,2,3),labels = c('Low', 'Mod', 'High'))
# df['ASP_Grp'] <- factor(ntile(df$ASP_LT, n = 3), levels = c(1,2,3),labels = c('Low', 'Mod', 'High'))

df['Alc_Density'] <- df$NumOfDrinkers / df$Size
df['MJ_Density'] <- df$NumOfMJUsers / df$Size
df['Drg_Density'] <- df$NumOfDrgUsers / df$Size

table(df[c('Alc_Grp', 'ASP_Grp')])

#### Visualizations ####
# Density Plots
p1 <- ggplot(data = df, mapping = aes(x = AL_PC, y = Alc_Density, color = Alc_Grp)) + 
      geom_point()


# Frequency Plots
p1 <- ggplot(data = df, mapping = aes(x = AlcFrequency_AVG, y = MJFrequency_AVG, color = AL_PC)) +
      geom_point() + 
      scale_fill_gradient(low = 'blue', high = 'black') +
      # scale_color_grey(start = 0.8, end = 0.2) + 
      theme_bw()

p2 <- ggplot(data = df, mapping = aes(x = AlcFrequency_AVG, y = DrgFrequency_AVG, color = AL_PC)) +
      geom_point() + 
      # scale_fill_gradient(low = 'blue', high = 'black') +
      # scale_color_grey(start = 0.8, end = 0.2) + 
      theme_bw()

cowplot::plot_grid(p1, p2, nrow = 2)

# Quantity Plots
p1 <- ggplot(data = df_long, mapping = aes(x = AlcDrinkWithPerson, y = Closeness, color = AL_PC)) +
  geom_point() + 
  scale_fill_gradient(low = 'blue', high = 'black') +
  # scale_color_grey(start = 0.8, end = 0.2) + 
  theme_bw()

p2 <- ggplot(data = df_long, mapping = aes(x = AlcDrinkWithPerson, y = Betweenness, color = AL_PC)) +
  geom_point() + 
  # scale_fill_gradient(low = 'blue', high = 'black') +
  # scale_color_grey(start = 0.8, end = 0.2) + 
  theme_bw()

cowplot::plot_grid(p1, p2, nrow = 2)

#### Correlations ####
net_cols <- colnames(df)[31:44]
cor(df[c('AL_PC', 'ASP_LT', net_cols)])
cor(df_long[c('AlcFrequency', 'MJFrequency', 'DrgFrequency')])

#### Regressions ####
summary(lm <- lm(Alc_Density ~ Alc_Grp + ASP_LT, data = df))
hist(lm$residuals)

summary(lm(MJ_Density ~ Alc_Grp + ASP_LT, data = df))
summary(lm(Drg_Density ~ Alc_Grp + ASP_LT, data = df))

summary(lm(Contact_AVG ~ Alc_Grp + ASP_LT, data = df))
summary(lm(AlcFrequency_AVG ~ Alc_Grp + ASP_LT, data = df))
summary(lm(AlcQuantity_AVG ~ Alc_Grp + ASP_LT, data = df))

hist(df_long$MJFrequency)
hist(df_long$AlcFrequency)
summary(lme4::glmer(MJFrequency ~ AlcFrequency + (1|SubID), data = df_long, family = poisson))


#### Box-Cox Transformations ####
m.nb <- glmer.nb(MJFrequency ~ AlcFrequency + (1|SubID), data = df_long, verbose = TRUE)

y <- as.vector(df$Alc_Density)
x <- as.vector(df$AL_PC)
m <- lm(y ~ x)
bc <- boxcox(lm)
(lambda <- bc$x[which.max(bc$y)])

powerTransform <- function(y, lambda1, lambda2 = NULL, method = "boxcox") {
  
  boxcoxTrans <- function(x, lam1, lam2 = NULL) {
    
    # if we set lambda2 to zero, it becomes the one parameter transformation
    lam2 <- ifelse(is.null(lam2), 0, lam2)
    
    if (lam1 == 0L) {
      log(y + lam2)
    } else {
      (((y + lam2)^lam1) - 1) / lam1
    }
  }
  
  switch(method
         , boxcox = boxcoxTrans(y, lambda1, lambda2)
         , tukey = y^lambda1
  )
}


# re-run with transformation
mnew <- lm(powerTransform(y, lambda) ~ x)

# QQ-plot
op <- par(pty = "s", mfrow = c(1, 2))
qqnorm(m$residuals); qqline(m$residuals)
qqnorm(mnew$residuals); qqline(mnew$residuals)
par(op)
