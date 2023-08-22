import ROOT
import root_numpy as rnp
from ROOT import RooRealVar, RooGaussian, RooCBShape, RooAddPdf, RooDataSet, RooFit
ROOT.gROOT.SetBatch(ROOT.kTRUE)

# 1. Gaussian distribution
mu = RooRealVar("mu", "mean of Gaussian", 600, 500, 700)
sigma = RooRealVar("sigma", "width of Gaussian", 18, 0, 50)
x = RooRealVar("x", "x", mu.getVal() - 4*sigma.getVal(), mu.getVal() + 4*sigma.getVal())
gaussian = RooGaussian("gaussian", "Gaussian", x, mu, sigma)

# plot the distribution
canvas = ROOT.TCanvas()
plot = x.frame()
gaussian.plotOn(plot)
plot.Draw()

# save the plot as a PNG file
canvas.SaveAs("gaussian.png")

# # 2. Double crystal ball distribution
# mu = RooRealVar("mu", "mean of Double Crystal Ball", 6.37, -10, 10)
# sigma = RooRealVar("sigma", "width of Double Crystal Ball", 21.85, 0, 50)
# a1 = RooRealVar("a1", "parameter a1 of Double Crystal Ball", 1.009, 0, 10)
# a2 = RooRealVar("a2", "parameter a2 of Double Crystal Ball", 2.502, 0, 10)
# n1 = RooRealVar("n1", "parameter n1 of Double Crystal Ball", 24.999, 0, 50)
# n2 = RooRealVar("n2", "parameter n2 of Double Crystal Ball", 2.79, 0, 10)
# double_crystal = RooCBShape("double_crystal", "Double Crystal Ball", mu, sigma, a1, a2, n1, n2)

# 2. Double crystal ball distribution
mu = RooRealVar("mu", "mean of Double Crystal Ball", 6.37, -10, 10)
sigma = RooRealVar("sigma", "width of Double Crystal Ball", 21.85, 0, 50)
a1 = RooRealVar("a1", "parameter a1 of Double Crystal Ball", 1.009, 0, 10)
a2 = RooRealVar("a2", "parameter a2 of Double Crystal Ball", 2.502, 0, 10)
n1 = RooRealVar("n1", "parameter n1 of Double Crystal Ball", 24.999, 0, 50)
n2 = RooRealVar("n2", "parameter n2 of Double Crystal Ball", 2.79, 0, 10)
double_crystal = RooCBShape("double_crystal", "Double Crystal Ball", mu, sigma, a1, a2, n1)


# plot the distribution
canvas = ROOT.TCanvas()
plot = mu.frame()
double_crystal.plotOn(plot)
plot.Draw()

# save the plot as a PNG file
canvas.SaveAs("double_crystal.png")

# 3. Multiply the distributions
pdf = RooAddPdf("pdf", "pdf", gaussian, double_crystal)
data = pdf.generate(ROOT.RooArgSet(x), 10000)

# # # plot the product distribution
# # x_arr = rnp.hist2array(data.createHistogram("x"))
# # product = x_arr * double_crystal.createHistogram("x").getArray()
# # h_product = ROOT.TH1F("h_product", "Product of Gaussian and Double Crystal Ball", 1000, mu.getVal() - 4*sigma.getVal(), mu.getVal() + 4*sigma.getVal())
# # rnp.array2hist(product, h_product)
# # h_product.Draw()
# # canvas.Draw()

# # plot the combined data set
# canvas = ROOT.TCanvas()
# plot = x.frame()
# data.plotOn(plot)
# plot.Draw()

# # save the plot as a PNG file
# canvas.SaveAs("product.png")


# plot the combined data set
canvas = ROOT.TCanvas()
plot = x.frame()
data.plotOn(plot)
plot.Draw()
canvas.SaveAs("combined.png")

# clean up
del gaussian, double_crystal, pdf, data
