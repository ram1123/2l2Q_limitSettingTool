import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# 1. Gaussian distribution
mu = 600  # mean
sigma = 18  # standard deviation
x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
gaussian = norm.pdf(x, mu, sigma)
plt.plot(x, gaussian, color='blue', label='Gaussian')

# save the plot as a PNG file
plt.savefig('gaussian.png')

# 2. Double crystal ball distribution
mu_dc = 6.37
sigma_dc = 21.85
a1 = 1.009
a2 = 2.502
n1 = 24.999
n2 = 2.79
x_dc = np.linspace(mu_dc - 4*sigma_dc, mu_dc + 4*sigma_dc, 1000)

# Generate the double crystal ball distribution
def double_crystal_ball(x, mu, sigma, a1, a2, n1, n2):
    t = (x - mu) / sigma
    if t > -a1:
        return np.exp(-0.5 * t**2)
    elif -a1 <= t <= a2:
        return np.exp(-0.5 * a1**2) * ((a1 - a2*t) / (a1**n1 * sigma**n1))
    else:
        return np.exp(-0.5 * a1**2 - 0.5 * (a2**2 / n2**2) + (a2*t) / n2) / (a1**n1 * sigma**n1)

double_crystal = np.array([double_crystal_ball(xi, mu_dc, sigma_dc, a1, a2, n1, n2) for xi in x_dc])
plt.plot(x_dc, double_crystal, color='red', label='Double Crystal Ball')

# save the plot as a PNG file
plt.savefig('double_crystal.png')

# 3. Convolute the Gaussian distribution with the double crystal ball distribution
res = 3  # resolution of the detector in GeV
kernel = norm.pdf(x, 0, res)
conv_gaussian = np.convolve(gaussian, kernel, mode='same')
product = conv_gaussian * double_crystal

# Plot the distributions
plt.plot(x, kernel, color='orange', label='Detector Resolution Kernel')
plt.plot(x, conv_gaussian, color='green', label='Convolved Gaussian')
plt.plot(x, product, color='purple', label='Product')
plt.xlabel('Energy (GeV)')
plt.ylabel('Probability density')
plt.legend()
plt.savefig('product.png')

# # show the plot
# plt.show()
