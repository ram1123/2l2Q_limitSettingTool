import ROOT
import os

ROOT.gROOT.SetBatch(True)  # run in batch mode

def GetMassFromFileName(fileName):
    return int(fileName.split("/")[-2])

def GetDataCardNameFromFileName(fileName):
    return fileName.split("/")[-1].replace(".root", "")

def process_workspace(fileName):
    mass = GetMassFromFileName(fileName)
    print("Processing file: {}, Mass: {}".format(fileName, mass))

    # Open ROOT file and retrieve the RooWorkspace
    file = ROOT.TFile.Open(fileName)
    w = file.Get("w")

    # Initialize
    obs_names = ['CMS_channel', 'zz2l2q_mass', 'Dspin0', 'zz2lJ_mass']
    canvas = ROOT.TCanvas("c", "c", 800, 600)

    # Dictionary to hold histograms
    histograms = {}

    # Get data
    data = w.data("data_obs")
    if not data:
        print("Data set 'data_obs' not found in workspace!")
        file.Close()
        return

    # Loop through each entry
    for i in range(data.numEntries()):
        event = data.get(i)
        current_channel_obs = event.find('CMS_channel')

        if current_channel_obs:
            current_channel = current_channel_obs.getLabel()

            for name in obs_names[1:]:
                obs = event.find(name)

                if obs and isinstance(obs, ROOT.RooRealVar):
                    key = "{}_{}".format(current_channel, name)

                    if key not in histograms:
                        histograms[key] = ROOT.TH1F(key, key, 100, 0, 3500 if 'mass' in name else 1)

                    histograms[key].Fill(obs.getVal())

    # Create directory if not exists
    if not os.path.exists("debugPlots/{}".format(GetDataCardNameFromFileName(fileName))):
        os.makedirs("debugPlots/{}".format(GetDataCardNameFromFileName(fileName))) # Create directory

    # Plotting
    for key, hist in histograms.items():
        c = ROOT.TCanvas(key, key, 800, 600)
        hist.Draw()
        c.SaveAs("debugPlots/{}/{}_{}.png".format(GetDataCardNameFromFileName(fileName), key,  mass))

    # Close ROOT file
    file.Close()

# List of workspace files
workspace_files = [
    "datacards_HIG_23_001/cards_2018/HCG/1500/AllCombined.root"
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_13TeV_xs.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_13TeV_xs_NoNuisance.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_Merged_13TeV_xs.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_Merged_vbf_tagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_Merged_b_tagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_Merged_untagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_Resolved_13TeV_xs.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_Resolved_vbf_tagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_Resolved_b_tagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_Resolved_untagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_eeqq_Merged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_eeqq_Merged_b_tagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_eeqq_Merged_untagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_eeqq_Merged_vbf_tagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_eeqq_Resolved_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_eeqq_Resolved_b_tagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_eeqq_Resolved_untagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_eeqq_Resolved_vbf_tagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_mumuqq_Merged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_mumuqq_Merged_b_tagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_mumuqq_Merged_untagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_mumuqq_Merged_vbf_tagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_mumuqq_Resolved_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_mumuqq_Resolved_b_tagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_mumuqq_Resolved_untagged_13TeV.root",
    # "datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_mumuqq_Resolved_vbf_tagged_13TeV.root"
]

# Process each workspace
for fileName in workspace_files:
    process_workspace(fileName)
