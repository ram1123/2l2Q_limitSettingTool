import os
import glob
import ROOT
from prettytable import PrettyTable

# set up table headers
table = PrettyTable(["Signal Mass (GeV)", "Expected Limit", "Expected -1 Sigma", "Expected +1 Sigma", "Expected -2 Sigma", "Expected +2 Sigma"])

# loop over root files in directory
for root_file in glob.glob("datacards_HIG_23_001/cards_2016/HCG/*/higgsCombinemH*_2016_AsympLimitblind_.AsymptoticLimits.mH*.root"):
    # extract signal mass from file name
    signal_mass = int(os.path.splitext(root_file)[0].split("mH")[-1])

    # if signal_mass != 500:    continue

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

    # add row to table
    table.add_row([signal_mass, round(limit_values[2], 4), round(limit_values[1], 4), round(limit_values[3], 4), round(limit_values[0], 4), round(limit_values[4], 4)])

# sort table by "Signal Mass (GeV)" column
table.sortby = "Signal Mass (GeV)"

# print table
print(table)
