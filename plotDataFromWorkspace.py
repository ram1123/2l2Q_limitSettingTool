import ROOT
ROOT.gROOT.SetBatch(True)  # run in batch mode

# Load the workspace from a ROOT file
input_file = ROOT.TFile.Open("datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_13TeV_xs.root")
workspace = input_file.Get("w")

# Get the RooDataSet from the workspace
data_obs = workspace.data("data_obs")

# Define the frame for zz2l2q_mass
frame1 = workspace.var("zz2l2q_mass").frame(ROOT.RooFit.Title("ZZ to 2l2q Mass"))
# Plot data on the frame
data_obs.plotOn(frame1)

# Draw the frame
canvas1 = ROOT.TCanvas("canvas1", "canvas1")
frame1.Draw()
canvas1.SaveAs("zz2l2q_mass_plot.png")

# Define the frame for zz2l2q_mass
frame1 = workspace.var("zz2lJ_mass").frame(ROOT.RooFit.Title("ZZ to 2lJ Mass"))
# Plot data on the frame
data_obs.plotOn(frame1)

# Draw the frame
canvas12 = ROOT.TCanvas("canvas12", "canvas12")
frame1.Draw()
canvas12.SaveAs("zz2lJ_mass_plot.png")

# Similarly you can define frames for other variables and plot them
frame2 = workspace.var("Dspin0").frame(ROOT.RooFit.Title("Spin Discriminant"))
data_obs.plotOn(frame2)

canvas2 = ROOT.TCanvas("canvas2", "canvas2")
frame2.Draw()
canvas2.SaveAs("Dspin0_plot.png")

# Define the frame for zz2l2q_mass
frame1 = workspace.var("CMS_channel").frame(ROOT.RooFit.Title("ZZ to 2lJ Mass"))
# Plot data on the frame
data_obs.plotOn(frame1)

# Draw the frame
canvas3 = ROOT.TCanvas("canvas3", "canvas3")
frame1.Draw()
canvas3.SaveAs("CMS_channel_plot.png")

# Don't forget to close the ROOT file
input_file.Close()
