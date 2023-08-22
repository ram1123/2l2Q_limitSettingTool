import matplotlib.pyplot as plt
import numpy as np

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
# im = ax.imshow(data, cmap='YlGn')
# im = ax.imshow(data, cmap='Blues')
# im = ax.imshow(data, cmap='YlOrRd')
# im = ax.imshow(data, cmap='OrRd')
# im = ax.imshow(data, cmap='autumn')
# im = ax.imshow(data, cmap='hsv')
im = ax.imshow(data, cmap='Pastel1')

# Add the row and column labels
ax.set_xticks(np.arange(len(labels)))
ax.set_yticks(np.arange(len(labels)))
ax.set_xticklabels(labels)
ax.set_yticklabels(labels)

# Rotate the x-axis labels
plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")

# Add the BR values to the heatmap
for i in range(len(labels)):
    for j in range(len(labels)):
        if data[i, j] != 0:
            text = ax.text(j, i, "{:.2f}%".format(data[i, j]),
                           ha="center", va="center", color="black", fontsize=12)

# Add a colorbar to the heatmap
cbar = ax.figure.colorbar(im, ax=ax)
cbar.ax.set_ylabel("BR (%)", rotation=-90, va="bottom")

# Set the title of the heatmap
ax.set_title("Higgs Boson BR")

# # Add the text box to the upper triangle
# for i in range(len(labels)):
#     for j in range(i+1, len(labels)):
#         text = ax.text(j, i, "BR HH -> XXYY",
#                        ha="center", va="center", color="Black")

# Save the heatmap as a PDF file
plt.savefig("dihiggs_boson_br3.pdf")

# Show the heatmap
plt.show()
