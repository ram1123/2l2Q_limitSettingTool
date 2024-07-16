import ROOT

# no pop up plots
ROOT.gROOT.SetBatch(True)

datacardPath = "/afs/cern.ch/user/r/rasharma/work/h2l2Q/EL7_Container/Limit_Extraction_FW/CMSSW_11_3_4/src/2l2Q_limitSettingTool/datacards_HIG_23_001/cards_2018_test/HCG/1000"
WorkspaceName = "hzz2l2q_mumuqq_Merged_b_tagged_13TeV.input.root"

# Open the ROOT file and get the workspace
file = ROOT.TFile(f"{datacardPath}/{WorkspaceName}")
workspace = file.Get("w")
workspace.Print("v")

if not workspace:
    raise Exception("Workspace not found in the file.")

# Retrieve the variable to plot
mass = workspace.var("zz2lJ_mass")
if not mass:
    raise Exception("Variable 'zz2lJ_mass' not found in workspace.")

# Create a canvas and a frame
canvas = ROOT.TCanvas("canvas", "PDF Plot", 800, 600)
frame = mass.frame()

# Define colors for the plots
colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen]
lineStyle = [1, 1, 2]

# PDFs list to plot
# pdf_names = ["bkg_zjets", "bkg_zjets_zjets_btaggedDown", "bkg_zjets_zjets_btaggedUp"]
pdf_names = ["bkg_vz", "bkg_vz_vz_btaggedDown", "bkg_vz_vz_btaggedUp"]
# pdf_names = ["bkg_ttbar", "bkg_ttbar_ttbar_btaggedDown", "bkg_ttbar_ttbar_btaggedUp"]
# pdf_names = ["bkg_zjets", "bkg_vz", "bkg_ttbar"]

leg = ROOT.TLegend(0.5, 0.5, 0.9, 0.9)  # Create a legend

#    // Create binning object with range (-15,15)
#    RooBinning tbins(-15, 15);
#    // Add 60 bins with uniform spacing in range (-15,0)
#    tbins.addUniform(60, -15, 0);
#    // Add 15 bins with uniform spacing in range (0,15)
#    tbins.addUniform(15, 0, 15);

# # add 10 bins from 0 to 3500
# tbins = ROOT.RooBinning(0, 3500)
# tbins.addUniform(10, 0, 3500)

# Loop through the PDF names to plot them
for i, pdf_name in enumerate(pdf_names):
    pdf = workspace.pdf(pdf_name)
    if not pdf:
        print(f"PDF '{pdf_name}' not found in workspace.")
        continue
    cmdList = ROOT.RooLinkedList()
    cmdList.Add(ROOT.RooFit.LineColor(colors[i]))
    cmdList.Add(ROOT.RooFit.LineStyle(lineStyle[i]))
    cmdList.Add(ROOT.RooFit.Name(pdf_name))
    pdf.plotOn(frame, cmdList)
    leg.AddEntry(frame.findObject(pdf_name), pdf_name, "l")


# reset y-range to -0.1 to 0.7
frame.SetMinimum(0.0000001)
frame.SetMaximum(0.7)


# Draw the frame and the legend
frame.Draw()
# leg.Draw()

# set logY

canvas.SetLogy()

# Show the canvas
canvas.Draw()

# Save the canvas to a file
canvas.SaveAs(f"pdf_plot_comparison_{pdf_names[0]}.png")

# Close the ROOT file
file.Close()
