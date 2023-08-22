import ROOT as ROOT
import sys
ROOT.gROOT.SetBatch(ROOT.kTRUE)

def get_standard_deviation(histogram):
    # Compute the standard deviation of a histogram
    mean = histogram.GetMean()
    variance = histogram.GetStdDev() ** 2
    return variance ** 0.5

def main():
    # Open the ROOT file
    file_name = "/eos/user/g/guoj/Sample/2L2Q/UL_Legacy/2018/sig_all.root"
    file = ROOT.TFile(file_name)

    # Get the tree from the file
    tree_name = "passedEvents"
    tree = file.Get(tree_name)

    # Set the GEN mass window parameters
    gen_mass = float(sys.argv[1]) if len(sys.argv) > 1 else 500  # Default: 500 GeV
    window_percentage = 0.02

    # Create histograms
    gen_histogram = ROOT.TH1F("gen_histogram", "GEN Higgs Mass", 300, 0, 1000)
    reco_histogram = ROOT.TH1F("reco_histogram", "RECO Higgs Mass", 200, 0, 1000)
    diff_histogram = ROOT.TH1F("diff_histogram", "GEN - RECO", 100, -100, 100)

    # Loop over the events in the tree
    count_Events = 0
    for event in tree:
        if count_Events % 50000 == 0: print(f"Event {count_Events}")
        if count_Events > 1000000: break

        # Apply the additional cut for resolved case
        # if (
        #     event.foundZ1LCandidate
        #     and event.isEE
        #     and ((event.mass2jet > 70) and (event.mass2jet < 105))
        #     and event.foundZ1LCandidate
        #     and event.foundZ2JCandidate
        # ):

        # Apply the additional cut for merged case
        if (
            event.foundZ1LCandidate
            and event.foundZ2MergedCandidata
            and event.isEE
            and event.massmerged > 70
            and event.massmerged < 105
            and event.particleNetZvsQCD > 0.9
        ):
            # Get GEN and RECO mass values
            gen_mass_value = event.GEN_H1_mass
            # reco_mass_value = event.mass2l2jet      # resolved
            reco_mass_value = event.mass2lj    # merged

            # Fill the histograms within the given GEN mass window
            if abs(gen_mass_value - gen_mass) <= window_percentage * gen_mass:
                gen_histogram.Fill(gen_mass_value)
                reco_histogram.Fill(reco_mass_value)
                diff_histogram.Fill(gen_mass_value - reco_mass_value)

        count_Events +=1

    # Print the standard deviation for both histograms
    gen_std_dev = get_standard_deviation(gen_histogram)
    reco_std_dev = get_standard_deviation(reco_histogram)

    # Get what is the percentage of the GEN standard deviation compared to the mass value
    gen_std_dev_percentage = (gen_std_dev / gen_mass)*100
    reco_std_dev_percentage = (reco_std_dev / gen_mass)*100

    print(f"Standard Deviation of GEN Higgs Mass: {gen_std_dev} ({gen_std_dev_percentage}%)")
    print(f"Standard Deviation of RECO Higgs Mass: {reco_std_dev} ({reco_std_dev_percentage}%)")

    # Draw the histograms on a canvas
    canvas = ROOT.TCanvas("canvas", "Higgs Mass Comparison", 800, 600)
    gen_histogram.Draw()
    gen_histogram.SetLineColor(ROOT.kRed)
    gen_histogram.SetLineWidth(2)
    reco_histogram.Draw("same")
    reco_histogram.SetLineColor(ROOT.kBlue)
    reco_histogram.SetLineWidth(2)

    # add legend
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend.AddEntry(gen_histogram, "GEN Higgs Mass", "l")
    legend.AddEntry(reco_histogram, "RECO Higgs Mass", "l")
    legend.Draw()

    # print the standard deviation on the canvas
    text = ROOT.TLatex()
    text.SetNDC()
    # round off to 2 decimal places
    gen_std_dev = round(gen_std_dev, 2)
    reco_std_dev = round(reco_std_dev, 2)
    text.DrawLatex(0.1, 0.8, f"GEN Std Dev: {gen_std_dev}")
    text.DrawLatex(0.1, 0.7, f"RECO Std Dev: {reco_std_dev}")

    canvas.Update()
    canvas.SaveAs("higgs_mass_comparison.png")

    diff_canvas = ROOT.TCanvas("diff_canvas", "GEN - RECO", 800, 600)
    diff_histogram.Draw()
    diff_histogram.SetLineColor(ROOT.kBlack)
    diff_histogram.SetLineWidth(2)

    # print the standard deviation on the canvas
    text = ROOT.TLatex()
    text.SetNDC()
    # round off to 2 decimal places
    diff_std_dev = round(get_standard_deviation(diff_histogram), 2)
    text.DrawLatex(0.1, 0.8, f"Std Dev: {diff_std_dev}")

    diff_canvas.Update()
    diff_canvas.SaveAs("higgs_mass_diff.png")

    # Clean up resources
    file.Close()

if __name__ == "__main__":
    main()
