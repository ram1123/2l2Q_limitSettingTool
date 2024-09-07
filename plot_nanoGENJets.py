import ROOT

# Enable multi-threading
ROOT.ROOT.EnableImplicitMT()

ROOT.gStyle.SetOptStat(0)

# Open the NanoAOD ROOT file
file_path = "root://cms-xrd-global.cern.ch//store/mc/Run3Summer22NanoAODv12/GluGluHtoZZto4L_M-125_TuneCP5_13p6TeV_powheg2-JHUGenV752-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_v5-v2/30000/542e888a-24b0-4e51-a494-d2690f894c0d.root"
file = ROOT.TFile.Open(file_path)

# Get the Events tree
tree = file.Get("Events")

# Create a TTreeReader to access the tree
reader = ROOT.TTreeReader(tree)

# Create TTreeReaderArrays for the branches you're interested in
gen_jet_pt = ROOT.TTreeReaderArray("Float_t")(reader, "GenJet_pt")
gen_jet_eta = ROOT.TTreeReaderArray("Float_t")(reader, "GenJet_eta")
gen_jet_phi = ROOT.TTreeReaderArray("Float_t")(reader, "GenJet_phi")
gen_jet_mass = ROOT.TTreeReaderArray("Float_t")(reader, "GenJet_mass")

# Create histograms for leading and sub-leading jets pT
hist_leading = ROOT.TH1F("Leading_jet_pT", "Leading Jet pT; pT (GeV); Counts", 100, 0, 200)
hist_subleading = ROOT.TH1F("Subleading_jet_pT", "Sub-leading Jet pT; pT (GeV); Counts", 100, 0, 200)

# Counters for jets below 30 GeV
count_leading_below_30 = 0
count_subleading_below_30 = 0
total_events = 0

# Loop over all events
while reader.Next():
    n_gen_jets = gen_jet_pt.GetSize()

    if n_gen_jets > 0:
        total_events += 1
        jets = []
        for i in range(n_gen_jets):
            jets.append((gen_jet_pt[i], gen_jet_eta[i], gen_jet_phi[i], gen_jet_mass[i]))

        # Sort jets by pT
        jets.sort(reverse=True, key=lambda x: x[0])

        # Fill histograms for leading and sub-leading jets
        if len(jets) > 0:
            leading_pt = jets[0][0]
            hist_leading.Fill(leading_pt)
            if leading_pt < 30:
                count_leading_below_30 += 1

        if len(jets) > 1:
            subleading_pt = jets[1][0]
            hist_subleading.Fill(subleading_pt)
            if subleading_pt < 30:
                count_subleading_below_30 += 1

# Compute fractions
fraction_leading_below_30 = (count_leading_below_30 / total_events) * 100
fraction_subleading_below_30 = (count_subleading_below_30 / total_events) * 100

# Round off the fractions
fraction_leading_below_30 = int(fraction_leading_below_30)
fraction_subleading_below_30 = int(fraction_subleading_below_30)

# Draw histograms
canvas = ROOT.TCanvas("canvas", "Leading and Sub-leading Jets pT", 800, 600)
hist_leading.SetLineColor(ROOT.kRed)
hist_subleading.SetLineColor(ROOT.kBlue)

hist_leading.SetMaximum(max(hist_leading.GetMaximum(), hist_subleading.GetMaximum()) * 1.2)
hist_leading.SetTitle("GEN Jet p_{T} distribution")

hist_leading.Draw()
hist_subleading.Draw("SAME")

# Add legend
legend = ROOT.TLegend(0.5, 0.7, 0.9, 0.9)
legend.AddEntry(hist_leading, "Leading Jet", "l")
legend.AddEntry(hist_subleading, "Sub-leading Jet", "l")
# legend text size
legend.SetTextSize(0.05)
legend.Draw()

# Add text for fractions
text = ROOT.TLatex()
text.SetNDC()
text.SetTextSize(0.05)
text.SetTextColor(ROOT.kRed)
text.DrawLatex(0.40, 0.60, f"Leading jets < 30 GeV: {fraction_leading_below_30}%")
text.SetTextColor(ROOT.kBlue)
text.DrawLatex(0.40, 0.55, f"Sub-leading jets < 30 GeV: {fraction_subleading_below_30}%")

# Save the canvas
canvas.SaveAs("leading_subleading_jets_pt.png")

# Close the file
file.Close()
