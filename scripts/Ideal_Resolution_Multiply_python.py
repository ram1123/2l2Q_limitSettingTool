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

# Define the parameters for the double crystal ball distribution
mu_dc = 6.37
sigma_dc = 21.85
a1 = 1.009
a2 = 2.502
n1 = 24.999
n2 = 2.79
x_dc = np.linspace(mu_dc - 4*sigma_dc, mu_dc + 4*sigma_dc, 1000)

# 2. Double crystal ball distribution
def double_crystal_ball(x, mu, sigma, a1, a2, n1, n2):
    t = (x - mu) / sigma
    if t > -a1:
        return np.exp(-0.5 * t**2)
    elif -a1 <= t <= a2:
        return np.exp(-0.5 * a1**2) * ((a1 - a2*t) / (a1**n1 * sigma**n1))
    else:
        return np.exp(-0.5 * a1**2 - 0.5 * (a2**2 / n2**2) + (a2*t) / n2) / (a1**n1 * sigma**n1)

x = np.linspace(6 - 4*21, 6 + 4*21, 1000)  # using mean 6 and sigma 21
double_crystal = np.array([double_crystal_ball(xi, 6, 21, 1.009, 2.502, 24.999, 2.79) for xi in x])
plt.plot(x, double_crystal, color='red', label='Double Crystal Ball')

# save the plot as a PNG file
plt.savefig('double_crystal.png')

# 3. Multiply the distributions
product = gaussian * double_crystal
plt.plot(x, product, color='green', label='Product')

# save the plot as a PNG file
plt.savefig('product.png')
