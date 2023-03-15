import ROOT

# Open the first ROOT file and retrieve the RooWorkspace object
file1 = ROOT.TFile("/afs/cern.ch/work/r/rasharma/LearnCombine/CMSSW_11_3_4/src/2l2Q_limitSettingTool/datacards_HIG_23_001/cards_2018/HCG/600_SigParsUncorrelated/hzz2l2q_13TeV_xs.root")
ws1 = file1.Get("w")

# Open the second ROOT file and retrieve the RooWorkspace object
file2 = ROOT.TFile("/afs/cern.ch/work/r/rasharma/LearnCombine/CMSSW_11_3_4/src/2l2Q_limitSettingTool/datacards_HIG_23_001/cards_2018/HCG/600_AllCorrelated/hzz2l2q_13TeV_xs.root")
ws2 = file2.Get("w")

# # Compare the variables in the workspaces
# vars1 = ws1.allVars()
# vars2 = ws2.allVars()

# print("vars1: ", len(vars1))
# print("vars1: ", (vars1))
# print("*"*100)
# print("vars2: ", len(vars2))
# print("vars2: ", (vars2))
# if len(vars1) != len(vars2):
#     print("Number of variables is different!")
# else:
#     CountDiffVar = 0
#     for i in range(len(vars1)):
#         if (vars1[i].GetName() != vars2[i].GetName()) or (vars1[i].getVal() != vars2[i].getVal()):
#             CountDiffVar += 1
#             print("Count: {}".format(CountDiffVar))
#             print("{:4}: Variable names are different! {} {}".format(i, vars1[i].GetName(), vars2[i].GetName()))
#             print("{:4}: Variable values are different! {} {}\n\n".format(i, vars1[i].getVal(), vars2[i].getVal()))
#         # elif vars1[i].getVal() != vars2[i].getVal():
#             # print("{:4}: Variable values are different! {} {}".format(i, vars1[i].getVal(), vars2[i].getVal()))

# # Compare the PDFs in the workspaces
# pdfs1 = ws1.allPdfs()
# pdfs2 = ws2.allPdfs()
# if len(pdfs1) != len(pdfs2):
#     print("Number of PDFs is different!")
# else:
#     CountDiffPDFs = 0
#     for i in range(len(pdfs1)):
#         if (pdfs1[i].GetName() != pdfs2[i].GetName()) or (pdfs1[i].getAttribute("Formula") != pdfs2[i].getAttribute("Formula")):
#             CountDiffPDFs += 1
#             print("Count: {}".format(CountDiffPDFs))
#             print("{:4} PDF names are different! {} {}".format(i, pdfs1[i].GetName(), pdfs2[i].GetName()))
#             print("{:4} PDF formulas are different! {} {}\n\n".format(i, pdfs1[i].getAttribute("Formula"), pdfs2[i].getAttribute("Formula")))
#         # elif pdfs1[i].getAttribute("Formula") != pdfs2[i].getAttribute("Formula"):
#             # print("PDF formulas are different!")

# # # Compare the datasets in the workspaces
# # data1 = ws1.allData()
# # data2 = ws2.allData()
# # if len(data1) != len(data2):
# #     print("Number of datasets is different!")
# # else:
# #     for i in range(len(data1)):
# #         if data1[i].GetName() != data2[i].GetName():
# #             print("Dataset names are different!")
# #         elif data1[i].numEntries() != data2[i].numEntries():
# #             print("Number of entries in dataset", data1[i].GetName(), "is different!")
# #         else:
# #             for j in range(data1[i].numEntries()):
# #                 for var in data1[i].get():
# #                     if var.getVal() != data2[i].get(var.GetName()).getVal():
# #                         print("Difference in value for variable", var.GetName(), "in dataset", data1[i].GetName())

# Compare the datasets in the workspaces
print("data1:")
data1 = ws1.allData()
print(type(data1))
print(len(data1))
for i in data1:
    i.Print()
    print("type: {}".format(type(i)))
print("data2:")
data2 = ws2.allData()
print(data2)
print("*"*100)
print(ws1.data("data_obs"))
print("*"*100)
print("ws1 entries: {}".format(int(ws1.data("data_obs").sumEntries())))
print("ws2 entries: {}".format(int(ws2.data("data_obs").sumEntries())))

# Print summary of RooDataSet
print(ws1.data("data_obs").Print("V"))
print(ws2.data("data_obs").Print("V"))

entries = int(ws1.data("data_obs").sumEntries())

print("#"*100)
print("{:3} {:5} {:5} {:5} {:5}".format("i", "channel", "zz2l2q", "Dspin0", "zz2lJ"))
for i in range(entries):
    if i > 10: break
    # print("===: Entry: ",i)
    # print(ws1.data("data_obs").get(i).Print("V"))
    # print(ws2.data("data_obs").get(i).Print("V"))
    print("{:3} {:3} {:3} {:3} {:3}".format(i, ws1.data("data_obs").get(i).getRealValue("CMS_channel"), ws1.data("data_obs").get(i).getRealValue("zz2l2q_mass"), ws1.data("data_obs").get(i).getRealValue("Dspin0"), ws1.data("data_obs").get(i).getRealValue("zz2lJ_mass")))


print("#"*100)

# Print the number of events in the dataset
print("Number of events: ", ws1.data("data_obs").sumEntries())

data_obs = ws1.data("data_obs")
# Print the value of each variable for the first event
data_obs.get(0)
CMS_channel = data_obs.get(0).getRealValue("CMS_channel")
zz2l2q_mass = data_obs.get(0).getRealValue("zz2l2q_mass")
Dspin0 = data_obs.get(0).getRealValue("Dspin0")
zz2lJ_mass = data_obs.get(0).getRealValue("zz2lJ_mass")
print("CMS_channel = ", CMS_channel)
print("zz2l2q_mass = ", zz2l2q_mass)
print("Dspin0 = ", Dspin0)
print("zz2lJ_mass = ", zz2lJ_mass)

print("#"*100)
# # Print the names of the observables
# Get the RooArgSet containing all the observables
observables = data_obs.get()

# Print the names of the observables
print("Observables: ", [obs.GetName() for obs in observables])

for obs in observables:
    print("obs name: {:15}, obs type: {}".format(obs.GetName(), type(obs)))
# print(data1)
# if len(data1) != len(data2):
#     print("Number of datasets is different!")
# else:
#     print("data1: ", data1)
#     for i in data1:
#         i.Print()
#         print(data1[i])
    # for i in range(len(data1)):
    #     if data1[i].GetName() != data2[i].GetName():
    #         print("Dataset names are different!")
    #     elif data1[i].numEntries() != data2[i].numEntries():
    #         print("Number of entries in dataset", data1[i].GetName(), "is different!")
    #     else:
    #         for j in range(data1[i].numEntries()):
    #             for var in data1[i].get():
    #                 if var.getVal() != data2[i].get().find(var.GetName()).getVal():
    #                     print("Difference in value for variable", var.GetName(), "in dataset", data1[i].GetName())
