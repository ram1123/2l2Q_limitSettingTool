import ROOT

def main():
    inFile = "root://cms-xrd-global.cern.ch//store/mc/Run3Summer22NanoAODv12/GluGluHtoZZto4L_M-125_TuneCP5_13p6TeV_powheg2-JHUGenV752-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_v5-v2/30000/542e888a-24b0-4e51-a494-d2690f894c0d.root"
    inRootFile = ROOT.TFile.Open(inFile)
    inTree = inRootFile.Get("Events")

    c1 = ROOT.TCanvas("c1", "c1", 800, 600)
    # c1.SetLogy()
    # set canvas title
    c1.SetTitle("Jet p_{T} distribution")

    # no stat box
    ROOT.gStyle.SetOptStat(0)

    h1_leadingJetPt = ROOT.TH1F("h1_leadingJetPt", "Leading jet p_{T}", 100, 0, 200)
    h1_subleadingJetPt = ROOT.TH1F("h1_subleadingJetPt", "Subleading jet p_{T}", 100, 0, 200)
    h1_subsubleadingJetPt = ROOT.TH1F("h1_subsubleadingJetPt", "Subsubleading jet p_{T}", 100, 0, 200)

    inTree.Draw("Jet_pt[0]>>h1_leadingJetPt")
    inTree.Draw("Jet_pt[1]>>h1_subleadingJetPt")
    inTree.Draw("Jet_pt[2]>>h1_subsubleadingJetPt")

    h1_leadingJetPt.SetLineColor(ROOT.kRed)
    h1_subleadingJetPt.SetLineColor(ROOT.kBlue)
    h1_subsubleadingJetPt.SetLineColor(ROOT.kGreen)

    maxVal = max(h1_leadingJetPt.GetMaximum(), h1_subleadingJetPt.GetMaximum())
    maxVal = max(maxVal, h1_subsubleadingJetPt.GetMaximum())

    h1_leadingJetPt.SetMaximum(maxVal * 1.2)
    h1_leadingJetPt.SetTitle("Reco Jet p_{T} distribution")

    h1_leadingJetPt.Draw()
    h1_subleadingJetPt.Draw("same")
    h1_subsubleadingJetPt.Draw("same")

    legend = ROOT.TLegend(0.5, 0.7, 0.9, 0.9)
    legend.AddEntry(h1_leadingJetPt, "Leading jet", "l")
    legend.AddEntry(h1_subleadingJetPt, "Subleading jet", "l")
    legend.AddEntry(h1_subsubleadingJetPt, "Subsubleading jet", "l")
    legend.SetTextSize(0.05)
    legend.Draw()

    # Draw line when X axis is 30
    line = ROOT.TLine(30, 0, 30, maxVal * 1.2)
    line.SetLineColor(ROOT.kGreen)
    line.SetLineWidth(2)
    line.Draw()

    # Print fraction of events with pT < 30 GeV
    nEntries = inTree.GetEntries()
    Fraction_pT0_30 = int((inTree.GetEntries("Jet_pt[0] < 30")/nEntries)*100.)
    Fraction_pT1_30 = int((inTree.GetEntries("Jet_pt[1] < 30")/nEntries)*100.)
    Fraction_pT2_30 = int((inTree.GetEntries("Jet_pt[2] < 30")/nEntries)*100.)
    print("Fraction of events with leading jet pT < 30 GeV: {}%".format(Fraction_pT0_30))
    print("Fraction of events with subleading jet pT < 30 GeV: {}%".format(Fraction_pT1_30))
    print("Fraction of events with subsubleading jet pT < 30 GeV: {}%".format(Fraction_pT2_30))

    # Add text for fractions
    text = ROOT.TLatex()
    text.SetNDC()
    text.SetTextSize(0.05)
    text.SetTextColor(ROOT.kRed)
    text.DrawLatex(0.35, 0.60, f"Leading jets < 30 GeV: {Fraction_pT0_30}%")
    text.SetTextColor(ROOT.kBlue)
    text.DrawLatex(0.35, 0.55, f"Sub-leading jets < 30 GeV: {Fraction_pT1_30}%")
    text.SetTextColor(ROOT.kGreen)
    text.DrawLatex(0.35, 0.50, f"Subsub-leading jets < 30 GeV: {Fraction_pT2_30}%")



    c1.SaveAs("jetpT.png")

if __name__ == "__main__":
    main()
