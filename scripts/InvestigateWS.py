import ROOT
# ROOT.gROOT.SetBatch(True)  # run in batch mode

file = ROOT.TFile("datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_13TeV_xs.root")
workspace = file.Get("w")

pdf_mumu = workspace.pdf("Merged_mumuqq_Merged_mumuqq_Merged_b_tagged")
pdf_eeqq = workspace.pdf("Merged_eeqq_Merged_eeqq_Merged_b_tagged")
# pdf_mumu.Print()


dataset = workspace.data("data_obs")
dataset.Print()
# for i in range(dataset.numEntries()):
#     entry = dataset.get(i)
#     print(i, entry.contentsString())

#     # if entry.getRealValue("bin_variable_name") == 800:  # replace bin_variable_name with the name of your bin variable
#         # print(entry.contentsString())


# # Inspect the dataset for specific bin number (e.g., 800)
# for i in range(dataset.numEntries()):
#     entry = dataset.get(i)
#     if i == 800:  # Assuming 800 is the index of the entry and not a value of a variable
#         print("Bin {}: {}".format(i, entry.contentsString()))

#     # Inspect the dataset for specific value of zz2l2q_mass (e.g., 800)
#     if entry.getRealValue("zz2l2q_mass") == 800:  # Replace zz2l2q_mass with the appropriate variable name
#         print("Entry with zz2l2q_mass = 800: {}".format(entry.contentsString()))


#     if entry:  # Check if the entry exists
#         print("Variable values for bin 800:")
#         for var in entry:
#             print("{}: {}".format(var.GetName(), var.getVal()))
#     else:
#         print("No entry found at index 800.")


# Assuming '800' refers to the index of the entry in the dataset
entry = dataset.get(800)  # Retrieve the 800th entry
if entry:  # Check if the entry exists
    print("Variable values for bin 800:")
    for var in entry:
        if isinstance(var, ROOT.RooRealVar):
            print("{}: {}".format(var.GetName(), var.getVal()))
        elif isinstance(var, ROOT.RooCategory):
            print("{}: {}".format(var.GetName(), var.getLabel()))
else:
    print("No entry found at index 800.")

# params_eeqq = pdf_eeqq.getParameters(dataset)
# params_eeqq.Print("v")

if pdf_mumu and dataset:
    argset = ROOT.RooArgSet(dataset)
    params_mumu = pdf_mumu.getParameters(argset)

    # params_mumu = pdf_mumu.getParameters(dataset)
    params_mumu.Print("v")
else:
    print("Either pdf_mumu or dataset is not valid.")

frame = bin_variable.frame()  # replace bin_variable with the actual variable you are binning over
dataset.plotOn(frame)
pdf_mumu.plotOn(frame)
frame.Draw()
