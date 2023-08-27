"""
The RooWorkspace object is retrieved from a ROOT file.
1. Open the ROOT file and retrieve the RooWorkspace object
2. Print the contents of the RooWorkspace object
3. Get all the variables and print them
4. Plot all the variables present in the RooWorkspace object
5. Get the data set from the workspace
6. Plot the data set
"""

import ROOT
ROOT.gROOT.SetBatch(True)  # run in batch mode

fileName = "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_13TeV_xs.root"

GetMassFromFileName = lambda fileName: int(fileName.split("/")[-2])

print("Mass: {}".format(GetMassFromFileName(fileName)))



# 1. Open the ROOT file and retrieve the RooWorkspace object
file = ROOT.TFile.Open(fileName)
w = file.Get("w")

# 2. Print the contents of the RooWorkspace object
# w.Print()

# 3. Get all the variables and print them
allVars = w.allVars()
# allVars.Print("v")

# 4. Plot all the variables present in the RooWorkspace object
for var in allVars:
    frame = var.frame(ROOT.RooFit.Title(var.GetName()))

# 5. Get the data set from the workspace
data_obs = w.data("data_obs")

# print data_obs contents for each events: channel, weight, mass, spin, ...
# loop over events
print("data_obs contents:")
print("Entries: ", data_obs.numEntries())
print("Data set: ", data_obs)
print("{}".format(data_obs.Print()))
print("{}".format(data_obs.Print("v")))

"""
DataStore data_obs (data_obs)
  Contains 18054 entries
  Observables:
    1)  CMS_channel = Resolved_mumuqq_Resolved_mumuqq_Resolved_vbf_tagged(idx = 2)
  "CMS_channel"
    2)  zz2l2q_mass = 633.604  L(0 - 3500) B(32)  "zz2l2q_mass"
    3)       Dspin0 = 0.0274993  L(0 - 1) B(50)  "Dspin0"
    4)   zz2lJ_mass = 368.301  L(0 - 3500) B(24)  "zz2lJ_mass"
"""

# 4. Plot all the variables present in the RooWorkspace object
obs_names = ['CMS_channel', 'zz2l2q_mass', 'Dspin0', 'zz2lJ_mass']
canvas = ROOT.TCanvas("c", "c", 800, 600)

for i, name in enumerate(obs_names):
    canvas.cd()
    myVar = w.var(name)
    if myVar:  # Check if the variable exists
        frame = myVar.frame()
        data = w.data("data_obs")  # Assuming data_obs is your dataset name
        if data:
            data.plotOn(frame)
        frame.Draw()
        canvas.SaveAs("{}_plot.png".format(name))

# 5. Get the dataset from the workspace
data = w.data("data_obs")

temp_channel = None  # Initialize to None

# Loop through each entry in the dataset
for i in range(data.numEntries()):
    event = data.get(i)

    current_channel_obs = event.find('CMS_channel')

    if current_channel_obs:
        current_channel = current_channel_obs.getLabel()

        # Check if the channel is new
        if current_channel != temp_channel:
            print("Event {}:".format(i + 1))

            # Update temp_channel
            temp_channel = current_channel
            print("temp_channel = {}".format(temp_channel))
            print("CMS_channel = {} (index: {})".format(current_channel, current_channel_obs.getIndex()))

            # Print the other variables
            for name in obs_names[1:]:  # Exclude 'CMS_channel' as we already printed it
                obs = event.find(name)
                if obs and isinstance(obs, ROOT.RooRealVar):
                    print("{} = {}".format(name, obs.getVal()))

#  #############
#

temp_channel = None  # Initialize to None

# Create a dictionary to hold histograms for each channel
histograms = {}

# Loop through each entry in the dataset
for i in range(data.numEntries()):
    event = data.get(i)

    current_channel_obs = event.find('CMS_channel')
    if current_channel_obs:
        current_channel = current_channel_obs.getLabel()

        # Initialize histograms if channel is new
        if current_channel != temp_channel:
            temp_channel = current_channel
            for name in obs_names[1:]:  # We skip 'CMS_channel'
                # CMS_channel format is like "Merged_eeqq_Merged_eeqq_Merged_b_tagged"
                # We want to extract
                #  - the jet type (Merged/Resolved)
                #  - the lepton type (ee/mumu)
                #  - the tag type (b/vbf/untagged)

                # Split the string by '_'
                split_channel = temp_channel.split("_")

                # Get the jet type
                jet_type = split_channel[0]

                # Get the lepton type
                lepton_type = split_channel[1]

                # Get the tag type
                tag_type = ""
                if split_channel[-1] == "tagged":
                    tag_type = split_channel[-2]  + "_tagged"
                else:
                    tag_type = split_channel[-1]

                histograms["{}_{}".format(temp_channel, name)] = ROOT.TH1F("{}_{}".format(temp_channel, name), "{}_{};{};{}".format(temp_channel, name,  name + "  (" + lepton_type + ", " + jet_type + ", " + tag_type + ", M" + str(GetMassFromFileName(fileName)) +  "GeV)", "Entries"), 100, 0, 3500 if 'mass' in name else 1)

        # Fill the histograms
        for name in obs_names[1:]:
            obs = event.find(name)
            if obs and isinstance(obs, ROOT.RooRealVar):
                histograms["{}_{}".format(temp_channel, name)].Fill(obs.getVal())

# create a directory named debugPlots, if not exists, and save the histograms there
import os
if not os.path.exists("debugPlots"):
    os.makedirs("debugPlots")

# Plotting
for key, hist in histograms.items():
    c = ROOT.TCanvas(key, key, 800, 600)
    hist.Draw()
    # c.SaveAs("debugPlots/{}.png".format(key))
    c.SaveAs("debugPlots/{}_{:.2f}.png".format(key, GetMassFromFileName(fileName)))

# Don't forget to close the ROOT file
file.Close()
