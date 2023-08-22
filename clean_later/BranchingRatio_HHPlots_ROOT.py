import ROOT
import numpy as np
ROOT.gROOT.SetBatch(ROOT.kTRUE)
import array

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
labels = ['Hbb', 'HWW', 'H'+u'\u03C4'+u'\u03C4', 'Hcc', 'HZZ', 'H'+u'\u03B3'+u'\u03B3']

# Create a TCanvas
canvas = ROOT.TCanvas("canvas", "Dihiggs Boson BR", 800, 800)

# Create a TH2F histogram for the heatmap
hist = ROOT.TH2F("hist", "Dihiggs Boson BR", len(labels), 0, len(labels), len(labels), 0, len(labels))

# Fill the histogram with the BR data
for i in range(len(labels)):
    for j in range(len(labels)):
        hist.SetBinContent(i+1, j+1, data[i, j])

# Set the labels for the x-axis and y-axis
for i, label in enumerate(labels):
    hist.GetXaxis().SetBinLabel(i+1, label)
    hist.GetYaxis().SetBinLabel(i+1, label)

# Rotate the x-axis labels
hist.GetXaxis().LabelsOption("v")

# Set the color palette for the heatmap
palette = array.array('i', [ROOT.kWhite, ROOT.kYellow-9, ROOT.kOrange+7, ROOT.kRed+1])
ROOT.gStyle.SetPalette(len(palette), palette)


# Draw the heatmap
hist.Draw("colztext")

# Set the title for the heatmap
hist.SetTitle("Dihiggs Boson BR")

# Add a colorbar to the heatmap
palette_axis = hist.GetListOfFunctions().FindObject("palette")
# palette_axis.SetTitle("BR (%)")

# Save the heatmap as a PDF file
canvas.SaveAs("dihiggs_boson_br.png")
canvas.SaveAs("dihiggs_boson_br.pdf")
