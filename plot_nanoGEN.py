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

# Create histograms for ISR and FSR quarks pT
hist_isr = ROOT.TH1F("ISR_quarks_pT", "ISR Quarks pT; pT (GeV); Counts", 100, 0, 200)
hist_fsr = ROOT.TH1F("FSR_quarks_pT", "FSR Quarks pT; pT (GeV); Counts", 100, 0, 200)
hist_anyother_quarks = ROOT.TH1F("AnyOther_quarks_pT", "AnyOther Quarks pT; pT (GeV); Counts", 100, 0, 200)

counter = 0
total_events = 0
count_leading_below_30 = 0

# Loop over all events
while reader.Next():
    n_gen_parts = gen_part_pdgid.GetSize()

    # if counter > 10:
    #     break

    for i in range(n_gen_parts):
        pdgid = gen_part_pdgid[i]
        status = gen_part_status[i]
        pt = gen_part_pt[i]
        mother_idx = gen_part_genpartidxmother[i]

        # Define criteria for ISR and FSR quarks
        # This is an example, you may need to adjust the criteria based on your specific needs
        if abs(pdgid) <= 5:  # Quarks have PDG IDs 1-5
            # Final state quarks
            # print("Quark: (PDG ID, status, pT) = ({:3}, {:3}, {})".format(pdgid, status, pt))
            if status == 23:
                total_events += 1
                hist_anyother_quarks.Fill(pt)
                if pt < 30:
                    count_leading_below_30 += 1
                # print("Quark with PDG ID {} and status {} has pT = {} GeV".format(pdgid, status, pt))

    counter += 1
# Draw histograms
canvas = ROOT.TCanvas("canvas", "ISR and FSR Quarks pT", 800, 600)
# hist_isr.SetLineColor(ROOT.kRed)
# hist_fsr.SetLineColor(ROOT.kBlue)
hist_anyother_quarks.SetLineColor(ROOT.kBlack)

# hist_isr.Draw()
# hist_fsr.Draw("SAME")
# hist_anyother_quarks.Draw("SAME")
hist_anyother_quarks.Draw()

# legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
# legend.AddEntry(hist_isr, "ISR Quarks", "l")
# legend.AddEntry(hist_fsr, "FSR Quarks", "l")
# legend.AddEntry(hist_anyother_quarks, "AnyOther Quarks", "l")
# legend.Draw()

# Add text for fractions
text = ROOT.TLatex()
text.SetNDC()
text.SetTextSize(0.05)
text.SetTextColor(ROOT.kBlack)
text.DrawLatex(0.35, 0.60, f"Quarks < 30 GeV: {count_leading_below_30} / {total_events} = {int((count_leading_below_30 / total_events) * 100)}%")

canvas.SaveAs("isr_fsr_quarks_pt.png")

# Close the file
file.Close()
