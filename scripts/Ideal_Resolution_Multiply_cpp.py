import ROOT
import ROOT as R
R.RooRandom.randomGenerator().SetSeed(0)  # Set the random seed for reproducibility
ROOT.gROOT.SetBatch(ROOT.kTRUE)

# 1. Gaussian distribution
x = R.RooRealVar('x', 'Energy (GeV)', 560, 640)
mu = R.RooRealVar('mu', 'mean', 600, 560, 640)
sigma = R.RooRealVar('sigma', 'width', 18)
gaussian = R.RooGaussian('gaussian', 'Gaussian distribution', x, mu, sigma)

# Generate toy data from the Gaussian distribution
data_gaussian = gaussian.generate(R.RooArgSet(x), 10000)
data_gaussian.plotOn(R.RooPlot(x))
R.gPad.SaveAs('gaussian.png')

# 2. Double crystal ball distribution
x_dc = R.RooRealVar('x_dc', 'Energy (GeV)', -100, 100)
mu_dc = R.RooRealVar('mu_dc', 'mean', 6.37)
sigma_dc = R.RooRealVar('sigma_dc', 'width', 21.85)
a1 = R.RooRealVar('a1', 'alpha1', 1.009)
a2 = R.RooRealVar('a2', 'alpha2', 2.502)
n1 = R.RooRealVar('n1', 'n1', 24.999)
n2 = R.RooRealVar('n2', 'n2', 2.79)
double_crystal = R.RooDCBShape('double_crystal', 'Double Crystal Ball distribution', x_dc, mu_dc, sigma_dc, a1, a2, n1, n2)

# Generate toy data from the double crystal ball distribution
data_dc = double_crystal.generate(R.RooArgSet(x_dc), 10000)
data_dc.plotOn(R.RooPlot(x_dc))
R.gPad.SaveAs('double_crystal.png')

# 3. Convolute the Gaussian distribution with the double crystal ball distribution
res = 3
sigma_conv = R.RooRealVar('sigma_conv', 'convolution width', res)
gaussian_conv = R.RooGaussian('gaussian_conv', 'Gaussian resolution function', x, R.RooFit.RooConst(0), sigma_conv)
conv_gaussian = R.RooFFTConvPdf('conv_gaussian', 'Convolved Gaussian distribution', x, gaussian, gaussian_conv)
product = R.RooProdPdf('product', 'Product distribution', conv_gaussian, double_crystal)

# Generate toy data from the product distribution
data_product = product.generate(R.RooArgSet(x), 10000)
data_product.plotOn(R.RooPlot(x))
R.gPad.SaveAs('product.png')
