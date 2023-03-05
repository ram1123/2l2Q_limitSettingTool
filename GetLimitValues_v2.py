import os
import glob
import ROOT
from prettytable import PrettyTable

# define function to get limit values from root file
def get_limit_values(root_file):
    # open root file and get tree
    file = ROOT.TFile(root_file)
    tree = file.Get("limit")

    # Define a list to store the values
    limit_values = []
    for i in range(tree.GetEntries()):
        tree.GetEntry(i)
        # get limit values
        value = getattr(tree, "limit")
        # Append the value to the list
        limit_values.append(value)
    return limit_values

def GetLimitValues_ForCombinedCards(table):
    # loop over root files in directory
    for root_file in glob.glob("datacards_HIG_23_001/cards_2016/HCG/*/higgsCombinemH*_2016_AsympLimitblind_.AsymptoticLimits.mH*.root"):
        # print(root_file)
        # extract signal mass from file name
        signal_mass = int(os.path.splitext(root_file)[0].split("mH")[-1])
        # print(signal_mass)
        # if signal_mass > 700:    continue
        # get limit values from root file
        limit_values = get_limit_values(root_file)
        # add row to table
        table.add_row([signal_mass, round(limit_values[2], 6), round(limit_values[1], 6), round(limit_values[3], 6), round(limit_values[0], 6), round(limit_values[4], 6)])
    return table

def GetLimitValues_OneMass_EachCategory(table):
    MassPoint = "500"
    # loop over root files in directory
    for root_file in glob.glob("datacards_HIG_23_001/cards_2016/HCG/"+MassPoint+"/higgsCombinemH"+MassPoint+"_2016_AsympLimit*.root"):
        # print(root_file)
        # extract signal mass from file name
        signal_mass = (os.path.splitext(root_file)[0].split("higgsCombinemH"+MassPoint+"_2016_AsympLimitblind_")[-1].split(".AsymptoticLimits.mH"+MassPoint)[0])
        # split signal_mass into three parts: "eeqq_Resolved_b-tagged" => ["eeqq", "Resolved", "b-tagged"], then format it nicely
        signal_mass = signal_mass.split("_")
        if len(signal_mass) == 1:
            if signal_mass[0] == "":    signal_mass = "{:6} {:8} {:6}".format("All Combined", " ", " ")
            else: signal_mass = "{:6} {:8} {:6}".format(signal_mass[0], " ", " ")
        elif len(signal_mass) == 2:
            signal_mass = "{:6} {:8} {:6}".format(signal_mass[0], signal_mass[1], " ")
        else:
            signal_mass = "{:6} {:8} {:6}".format(signal_mass[0], signal_mass[1], signal_mass[2])
        # print(signal_mass)

        # get limit values from root file
        limit_values = get_limit_values(root_file)
        # # add row to table
        table.add_row([signal_mass, round(limit_values[2], 4), round(limit_values[1], 4), round(limit_values[3], 4), round(limit_values[0], 4), round(limit_values[4], 4)])
    return table

def CompareLimit_MergedResolved(table2):

    MassPoint = "*"
    MergedRootFile = "datacards_HIG_23_001/cards_2016/HCG/"+MassPoint+"/higgsCombinemH"+MassPoint+"_2016_AsympLimitblind_Merged.AsymptoticLimits.mH"+MassPoint+".root"
    # loop over root files in directory
    for root_file in glob.glob(MergedRootFile):
        # print(root_file)
        # extract signal mass from file name
        signal_mass = int(os.path.splitext(root_file)[0].split("mH")[-1])
        # print("Merged",signal_mass)
        # if signal_mass > 700:    continue
        # get limit values from root file
        limit_values_Merged = get_limit_values(root_file)
        limit_values_Resolved = get_limit_values(root_file.replace("Merged", "Resolved"))
        limit_values_combined = get_limit_values(root_file.replace("Merged", ""))
        # add row to table
        table2.add_row([signal_mass, round(limit_values_Resolved[2], 6), round(limit_values_Merged[2], 6), round(limit_values_combined[2], 6)])
    return table2

if __name__ == '__main__':
    # set up table headers
    table = PrettyTable()
    # table.field_names = ["Signal Mass (GeV)", "Expected Limit", "Expected -1 Sigma", "Expected +1 Sigma", "Expected -2 Sigma", "Expected +2 Sigma", "Observed Limit"]


    # table.field_names = ["Signal Mass (GeV)", "Expected Limit", "Expected -1 Sigma", "Expected +1 Sigma", "Expected -2 Sigma", "Expected +2 Sigma"]
    # table = GetLimitValues_ForCombinedCards(table)
    # table = GetLimitValues_OneMass_EachCategory(table)

    table.field_names = ["Signal Mass (GeV)",  "Resolved Limit",  "Merged Limit", "combined Limit"]
    table = CompareLimit_MergedResolved(table)

    # # sort table by signal mass
    table.sortby = "Signal Mass (GeV)"
    # table.sortby = "Expected Limit"

    # # left-align first column
    # # table.align["Signal Mass (GeV)"] = "l"

    # # print table
    print(table)
