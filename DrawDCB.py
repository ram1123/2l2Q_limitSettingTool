import ROOT
from ROOT import RooRealVar, RooDoubleCB, RooDataSet, RooFit

# Define the variables and the RooDoubleCB function
x = RooRealVar("x", "x", 900, 1100)
mean = RooRealVar("mean", "mean", 1004.97267557)
sigma = RooRealVar("sigma", "sigma", 37.1402875669)
alpha1 = RooRealVar("alpha1", "alpha1", 0.987967886364)
n1 = RooRealVar("n1", "n1", 5.93837598581)
alpha2 = RooRealVar("alpha2", "alpha2", 1.79020242615)
n2 = RooRealVar("n2", "n2", 0.5)

doubleCB = RooDoubleCB("doubleCB", "doubleCB", x, mean, sigma, alpha1, n1, alpha2, n2)

# Draw the plot
canvas = ROOT.TCanvas()
frame = x.frame()
doubleCB.plotOn(frame)
frame.Draw()
canvas.Draw()

canvas.SaveAs('testDCB.png')