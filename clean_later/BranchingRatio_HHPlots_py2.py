import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as colors

# Create an array of the BR data
data = np.array([[33.8724, 24.9096, 7.2983, 3.3640, 3.0497, 0.2642],
                [24.9096, 4.5796, 2.6836, 1.2369, 1.1214, 0.0972],
                [7.2983, 2.6836, 0.3931, 0.3624, 0.3285, 0.0285],
                [3.3640, 1.2369, 0.3624, 0.0835, 0.1514, 0.0131],
                [3.0497, 1.1214, 0.3285, 0.1514, 0.0686, 0.0119],
                [0.2642, 0.0972, 0.0285, 0.0131, 0.0119, 0.0005]])

# Only keep the lower triangle of the data array
data = np.tril(data)

# Define the row and column labels
# labels = ['Hbb', 'HWW', 'HTauTau', 'Hcc', 'HZZ', 'HGammaGamma']
labels = ['Hbb', 'HWW', 'H'+u'\u03C4'+u'\u03C4', 'Hcc', 'HZZ', 'H'+u'\u03B3'+u'\u03B3']

# Create a heatmap of the BR data
fig, ax = plt.subplots()

# Define the normalization and colormap for the heatmap
norm = colors.LogNorm(vmin=1e-3, vmax=1)
cmap = plt.cm.get_cmap('hsv')

# Create the heatmap with the defined normalization and colormap
im = ax.imshow(data, cmap=cmap, norm=norm)

# Add the row and column labels
ax.set_xticks(np.arange(len(labels)))
ax.set_yticks(np.arange(len(labels)))
ax.set_xticklabels(labels)
ax.set_yticklabels(labels)

# Rotate the x-axis labels
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

# Add the BR values to the heatmap
for i in range(len(labels)):
    for j in range(len(labels)):
        if data[i, j] != 0:
            text = ax.text(j, i, "{:.2f}%".format(data[i, j]),
                           ha="center", va="center", color="black", fontsize=12)

# Add a colorbar to the heatmap with the defined normalization
cbar = ax.figure.colorbar(im, ax=ax, norm=norm)
cbar.ax.set_ylabel("BR (%)", rotation=-90, va="bottom")

# Set the title of the heatmap
ax.set_title("Higgs Boson BR")

# Save the heatmap as a PDF file
plt.savefig("dihiggs_boson_br2.pdf")

# Show the heatmap
plt.show()
