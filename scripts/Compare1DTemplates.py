import ROOT

def compare_histograms(file1_path, file2_path, hist_name):
    # Open the first ROOT file
    file1 = ROOT.TFile.Open(file1_path)
    if not file1 or file1.IsZombie():
        print(f"Error: Cannot open {file1_path}")
        return

    # Open the second ROOT file
    file2 = ROOT.TFile.Open(file2_path)
    if not file2 or file2.IsZombie():
        print(f"Error: Cannot open {file2_path}")
        return

    # Get the histogram from the first file
    hist1 = file1.Get(hist_name)
    if not hist1:
        print(f"Error: Histogram {hist_name} not found in {file1_path}")
        return

    # Get the histogram from the second file
    hist2 = file2.Get(hist_name)
    if not hist2:
        print(f"Error: Histogram {hist_name} not found in {file2_path}")
        return

    # Create a canvas to draw both histograms
    canvas = ROOT.TCanvas("canvas", "Comparison of Histograms", 800, 600)

    # Customize histograms
    hist1.SetLineColor(ROOT.kRed)  # Set color for the first histogram
    hist1.SetLineWidth(2)          # Set line width for the first histogram
    hist1.SetTitle(f"Comparison of {hist_name}")  # Set title
    hist1.GetXaxis().SetTitle("Mass (GeV)")       # X-axis title
    hist1.GetYaxis().SetTitle("Events")           # Y-axis title

    hist2.SetLineColor(ROOT.kBlue)  # Set color for the second histogram
    hist2.SetLineWidth(2)           # Set line width for the second histogram

    # Draw histograms
    hist1.Draw("HIST")              # Draw the first histogram
    hist2.Draw("HIST SAME")         # Draw the second histogram on the same canvas

    # Add a legend to differentiate the histograms
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend.AddEntry(hist1, "File 1", "l")
    legend.AddEntry(hist2, "File 2", "l")
    legend.Draw()

    # Write integral on the histograms
    integral1 = hist1.Integral()
    integral2 = hist2.Integral()
    text1 = ROOT.TText(0.4, 0.6, f"Integral (File 1): {integral1:.2f}")
    text1.SetNDC()
    text1.Draw()
    text2 = ROOT.TText(0.4, 0.55, f"Integral (File 2): {integral2:.2f}")
    text2.SetNDC()
    text2.Draw()

    # Save the canvas as a PNG file
    canvas.SaveAs("histogram_comparison.png")

    # save log scale
    canvas.SetLogy()
    canvas.SaveAs("histogram_comparison_log.png")

    # Close the files
    file1.Close()
    file2.Close()

# Example usage
file1_path = "templates1D/Template1D_spin0_2mu_2018.root"
file2_path = "/tmp/rasharma/templates1D/Template1D_spin0_2mu_2018.root"
# hist_name = "hmass_mergedSR_VZ_perInvFb_Bin50GeV"
hist_name = "hmass_resolvedSR_VZ_perInvFb_Bin50GeV"

compare_histograms(file1_path, file2_path, hist_name)
