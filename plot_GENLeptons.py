import ROOT

# Enable multi-threading
ROOT.ROOT.EnableImplicitMT()

# Open the NanoAOD ROOT file
file_path = "root://cms-xrd-global.cern.ch//store/mc/Run3Summer22NanoAODv12/GluGluHtoZZto4L_M-125_TuneCP5_13p6TeV_powheg2-JHUGenV752-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_v5-v2/30000/542e888a-24b0-4e51-a494-d2690f894c0d.root"
file = ROOT.TFile.Open(file_path)

# Get the Events tree
tree = file.Get("Events")

# Create a TTreeReader to access the tree
reader = ROOT.TTreeReader(tree)

# Create TTreeReaderArrays for the branches you're interested in
gen_part_pdgid = ROOT.TTreeReaderArray("Int_t")(reader, "GenPart_pdgId")
gen_part_status = ROOT.TTreeReaderArray("Int_t")(reader, "GenPart_status")
gen_part_pt = ROOT.TTreeReaderArray("Float_t")(reader, "GenPart_pt")
gen_part_eta = ROOT.TTreeReaderArray("Float_t")(reader, "GenPart_eta")
gen_part_phi = ROOT.TTreeReaderArray("Float_t")(reader, "GenPart_phi")
gen_part_mass = ROOT.TTreeReaderArray("Float_t")(reader, "GenPart_mass")
gen_part_genpartidxmother = ROOT.TTreeReaderArray("Int_t")(reader, "GenPart_genPartIdxMother")

# Create histograms for the pT of the four leptons
hist_lepton1 = ROOT.TH1F("Lepton1_pT", "Lepton 1 pT; pT (GeV); Counts", 100, 0, 200)
hist_lepton2 = ROOT.TH1F("Lepton2_pT", "Lepton 2 pT; pT (GeV); Counts", 100, 0, 200)
hist_lepton3 = ROOT.TH1F("Lepton3_pT", "Lepton 3 pT; pT (GeV); Counts", 100, 0, 200)
hist_lepton4 = ROOT.TH1F("Lepton4_pT", "Lepton 4 pT; pT (GeV); Counts", 100, 0, 200)

# Loop over all events
while reader.Next():
    n_gen_parts = gen_part_pdgid.GetSize()

    leptons = []
    for i in range(n_gen_parts):
        pdgid = gen_part_pdgid[i]
        status = gen_part_status[i]
        pt = gen_part_pt[i]

        # Check if the particle is a final-state lepton (status 1) and comes from a Z boson
        if abs(pdgid) in [11, 13] and status == 1:
            mother_idx = gen_part_genpartidxmother[i]
            if mother_idx >= 0:
                mother_pdgid = gen_part_pdgid[mother_idx]
                if abs(mother_pdgid) == 23:  # Check if mother is a Z boson
                    leptons.append(pt)

    # Fill histograms for the leptons if we have exactly 4 leptons
    if len(leptons) == 4:
        leptons.sort(reverse=True)  # Sort leptons by pT
        hist_lepton1.Fill(leptons[0])
        hist_lepton2.Fill(leptons[1])
        hist_lepton3.Fill(leptons[2])
        hist_lepton4.Fill(leptons[3])

# Draw histograms
canvas = ROOT.TCanvas("canvas", "Lepton pT from H->ZZ->4l", 800, 600)
hist_lepton1.SetLineColor(ROOT.kRed)
hist_lepton2.SetLineColor(ROOT.kBlue)
hist_lepton3.SetLineColor(ROOT.kGreen)
hist_lepton4.SetLineColor(ROOT.kMagenta)

hist_lepton1.Draw()
hist_lepton2.Draw("SAME")
hist_lepton3.Draw("SAME")
hist_lepton4.Draw("SAME")

# Add legend
legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
legend.AddEntry(hist_lepton1, "Lepton 1", "l")
legend.AddEntry(hist_lepton2, "Lepton 2", "l")
legend.AddEntry(hist_lepton3, "Lepton 3", "l")
legend.AddEntry(hist_lepton4, "Lepton 4", "l")
legend.Draw()

# Save the canvas
canvas.SaveAs("leptons_pt.png")

# Close the file
file.Close()
