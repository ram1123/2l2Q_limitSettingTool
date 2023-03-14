from utils import *
import ROOT

# Set up logger
logger.setLevel( logging.INFO)

# Define functions to compare variables, PDFs, and datasets
def compare_variables(vars1, vars2):
    """Compare the variables in two RooWorkspace objects."""
    if len(vars1) != len(vars2):
        logger.warning("Number of variables is different!")
    else:
        count_diff_var = 0
        for i in range(len(vars1)):
            if vars1[i].GetName() != vars2[i].GetName() or vars1[i].getVal() != vars2[i].getVal():
                count_diff_var += 1
                logger.warning("Count: %d", count_diff_var)
                logger.warning("%4d: Variable names are different! %s %s", i, vars1[i].GetName(), vars2[i].GetName())
                logger.warning("%4d: Variable values are different! %s %s\n\n", i, vars1[i].getVal(), vars2[i].getVal())

def compare_pdfs(pdfs1, pdfs2):
    """Compare the PDFs in two RooWorkspace objects."""
    if len(pdfs1) != len(pdfs2):
        logger.warning("Number of PDFs is different!")
    else:
        count_diff_pdfs = 0
        for i in range(len(pdfs1)):
            if pdfs1[i].GetName() != pdfs2[i].GetName() or pdfs1[i].getAttribute("Formula") != pdfs2[i].getAttribute("Formula"):
                count_diff_pdfs += 1
                logger.warning("Count: %d", count_diff_pdfs)
                logger.warning("%4d: PDF names are different! %s %s", i, pdfs1[i].GetName(), pdfs2[i].GetName())
                logger.warning("%4d: PDF formulas are different! %s %s\n\n", i, pdfs1[i].getAttribute("Formula"), pdfs2[i].getAttribute("Formula"))

def compare_datasets(data_obs1, data_obs2):
    """Compare the datasets in two RooWorkspace objects."""
    # Get the RooArgSet containing all the observables
    observables = data_obs1.get()

    # Print the names of the observables
    obs_names = [obs.GetName() for obs in observables]
    logger.info("Observables: {}".format(obs_names))

    # Print the data as a table
    # Print the column headers
    col_headers = ["i"]
    for obs_name in obs_names:
        col_headers.append("{}_1".format(obs_name))
    for obs_name in obs_names:
        col_headers.append("{}_2".format(obs_name))
    logger.info("{:>3} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8}".format(*tuple(col_headers)))

    # Loop over the events in the dataset and print the data as a table
    entries = min(data_obs1.numEntries(), data_obs2.numEntries())
    for i in range(entries):
        # if i > 10:
            # break
        row = []
        row.append(i)
        for obs_name in obs_names:
            row.append("{:.2f}".format(data_obs1.get(i).getRealValue(obs_name)))
        for obs_name in obs_names:
            row.append("{:.2f}".format(data_obs2.get(i).getRealValue(obs_name)))
        logger.info("{:>3} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8}".format(*tuple(row)))

    logger.info("#" * 100)

def compare_datasets_PrintDiff(data_obs1, data_obs2):
    """Compare the datasets in two RooWorkspace objects."""
    logger.info("Comparing datasets: {} vs {}".format(data_obs1.GetName(), data_obs2.GetName()))
    # Get the RooArgSet containing all the observables
    observables = data_obs1.get()

    # Print the names of the observables
    obs_names = [obs.GetName() for obs in observables]

    for i in range(data_obs1.numEntries()):
        if i >= data_obs2.numEntries():
            logger.warning("Event {} only in data_obs1".format(i))
            break

        # Loop over the observables and compare their values
        for obs_name in obs_names:
            obs_val1 = data_obs1.get(i).getRealValue(obs_name)
            obs_val2 = data_obs2.get(i).getRealValue(obs_name)
            if abs(obs_val1 - obs_val2) > 1e-6:
                logger.warning("Event {} - {} values are different: {:.6f} vs {:.6f}".format(i, obs_name, obs_val1, obs_val2))

    logger.info("#" * 100)

# Open the first ROOT file and retrieve the RooWorkspace object
file1 = ROOT.TFile("/afs/cern.ch/work/r/rasharma/LearnCombine/CMSSW_11_3_4/src/2l2Q_limitSettingTool/datacards_HIG_23_001/cards_2018/HCG/600_SigParsUncorrelated/hzz2l2q_13TeV_xs.root")
ws1 = file1.Get("w")

# Open the second ROOT file and retrieve the RooWorkspace object
file2 = ROOT.TFile("/afs/cern.ch/work/r/rasharma/LearnCombine/CMSSW_11_3_4/src/2l2Q_limitSettingTool/datacards_HIG_23_001/cards_2018/HCG/600_AllCorrelated/hzz2l2q_13TeV_xs.root")
ws2 = file2.Get("w")

# Compare the variables in the workspaces
vars1 = ws1.allVars()
vars2 = ws2.allVars()
logger.info("Number of variables in ws1: %d", len(vars1))
logger.info("Number of variables in ws2: %d", len(vars2))
compare_variables(vars1, vars2)

# Compare the PDFs in the workspaces
pdfs1 = ws1.allPdfs()
pdfs2 = ws2.allPdfs()
logger.info("Number of PDFs in ws1: %d", len(pdfs1))
logger.info("Number of PDFs in ws2: %d", len(pdfs2))
compare_pdfs(pdfs1, pdfs2)

# Compare the datasets in the workspaces
data_obs1 = ws1.data("data_obs")
data_obs2 = ws2.data("data_obs")
logger.info("Number of entries in data_obs1: %d", data_obs1.numEntries())
logger.info("Number of entries in data_obs2: %d", data_obs2.numEntries())
compare_datasets(data_obs1, data_obs2)
compare_datasets_PrintDiff(data_obs1, data_obs2)
