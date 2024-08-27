#!/usr/bin/env python
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kInfo
import sys
from decimal import *
from subprocess import *
from array import array
import numpy as np

from inputReader import *
from systematicsClass import *
from utils import *
from utils_hist import plot_and_save, save_histograms
from utils_hist import smooth_histogram, smooth_histogram_with_tkde
from utils_hist import save_histograms_3
from utils_hist import visualize_workspace

ROOT.gROOT.ProcessLine("struct zz2lJ_massStruct {" "   Double_t zz2lJ_mass;" "};")

from ROOT import zz2lJ_massStruct


class DatacardClass:

    def __init__(self, year, DEBUG=False):
        logger.debug("Creating a new instance of DatacardClass")
        self.year = year
        self.DEBUG = DEBUG
        self.loadIncludes()
        self.setup_parameters()
        self.initialize_roofit_objects()
        self.workspace = ROOT.RooWorkspace("w", "workspace")
        self.sigFraction = 1.0  # Fraction of signal to be used
        self.channelName2D = ["ggH_hzz", "qqH_hzz", "bkg_vz", "bkg_ttbar", "bkg_zjets"]
        self.background_list = ["vz", "ttbar", "zjets"]
        self.background_map_2DTemplates = {
            "vz": "Diboson",
            "ttbar": "TTbar",
            "zjets": "DY",
        }
        self.hist_suffixes = {
            "vz": "VZ_perInvFb_Bin50GeV",
            "ttbar": "TTplusWW_perInvFb_Bin50GeV",
            "zjets": "Zjet_perInvFb_Bin50GeV",
        }
        self.datacard_lines = []

    def loadIncludes(self):
        """Load necessary ROOT libraries and include paths."""
        ROOT.gSystem.AddIncludePath("-I$ROOFITSYS/include/")
        ROOT.gSystem.AddIncludePath("-Iinclude/")
        ROOT.gROOT.ProcessLine(".L include/tdrstyle.cc")
        ROOT.gSystem.Load("libRooFit")
        ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so")

    def initialize_roofit_objects(self):
        # Extend the lifecycle of all RooFit objects by storing them as attributes of self
        self.rooVars = {}
        self.rooDataSet = {}
        self.rooDataHist = {}
        self.signalCBs = {}  # Dictionary to store signalCB objects
        self.rooProdPdf = {}  # Dictionary to store rooProdPdf objects
        self.rooFormulaVars = {}  # Dictionary to store RooFormulaVar objects
        self.rooArgSets = {}  # Dictionary to store RooArgSet objects
        self.background_hists_From1DTemplate = {}
        self.background_hists_From2DTemplate = {}
        self.background_hists = {}
        self.background_hists_smooth = {}

    def clearRooArgSets(self):
        """Clear RooArgSets before using them again as the datacard is initialized one time and used multiple times."""
        self.initialize_roofit_objects()
        self.workspace = ROOT.RooWorkspace("w", "workspace")
        self.sigFraction = 1.0  # Fraction of signal to be used
        self.datacard_lines = []

    def printAllRooArgSets(self):
        """Print all RooArgSets and related RooFit objects."""
        logger.error("==============        RooVars        ==============")
        for key, value in self.rooVars.items():
            print("key: {:35}, value: {}".format(key, value))

        logger.error("==============        RooDataSet        ==============")
        for key, value in self.rooDataSet.items():
            print("key: {:35}, value: {}".format(key, value))

        logger.error("==============        RooDataHist        ==============")
        for key, value in self.rooDataHist.items():
            print("key: {:35}, value: {}".format(key, value))

        logger.error("==============        SignalCBs        ==============")
        for key, value in self.signalCBs.items():
            print("key: {:35}, value: {}".format(key, value))

        logger.error("==============        RooProdPdf        ==============")
        for key, value in self.rooProdPdf.items():
            print("key: {:35}, value: {}".format(key, value))

        logger.error("==============        RooFormulaVars        ==============")
        for key, value in self.rooFormulaVars.items():
            print("key: {:35}, value: {}".format(key, value))

        logger.error("==============        RooArgSets        ==============")
        for key, value in self.rooArgSets.items():
            print("=========        key: {:35}        =========".format(key))
            for i in range(value.getSize()):
                print("{:4}: {}".format(i, value.at(i)))

        logger.error("==============        Background Hists        ==============")
        for key, value in self.background_hists.items():
            print("key: {:35}, value: {}".format(key, value))

        logger.error("==============        Background Hists Smooth        ==============")
        for key, value in self.background_hists_smooth.items():
            print("key: {:35}, value: {}".format(key, value))

    def setup_parameters(self):
        """Setup initial parameters."""
        self.low_M = 150
        self.high_M = 3500
        uniform_bins = np.linspace(self.low_M, self.high_M, int((self.high_M - self.low_M)/10), dtype=int)

        # Resolved bin edges
        temp_bin1_resolved = np.linspace(self.low_M, 1200, 22)
        temp_bin2_resolved = np.array([1300, 1400, 1500, 1600, self.high_M])
        # FIXME: Uniform bins or not?
        # self.binning_resolved = np.concatenate((temp_bin1_resolved, temp_bin2_resolved))
        self.binning_resolved = uniform_bins
        self.rooBinning_resolved = ROOT.RooBinning(len(self.binning_resolved) - 1, array('d', self.binning_resolved))

        # Merged bin edges
        temp_bin1_merged = np.linspace(self.low_M, 900, 16)
        temp_bin2_merged = np.array([1000, 1200, 1600, self.high_M])
        # FIXME: Uniform bins or not?
        # self.binning_merged = np.concatenate((temp_bin1_merged, temp_bin2_merged))
        self.binning_merged = uniform_bins
        self.rooBinning_merged = ROOT.RooBinning(len(self.binning_merged) - 1, array('d', self.binning_merged))

        self.ID_2muResolved = "mumuqq_Resolved"
        self.ID_2eResolved = "eeqq_Resolved"
        self.ID_2muMerged = "mumuqq_Merged"
        self.ID_2eMerged = "eeqq_Merged"

    def open_root_file(self, file_path):
        """Open a ROOT file and return the file object."""
        file = ROOT.TFile.Open(file_path, "READ")
        if not file or file.IsZombie():
            logger.error("Failed to open file: {}".format(file_path))
            raise FileNotFoundError("Could not open file: {}".format(file_path))
        logger.debug("Successfully opened file: {}".format(file_path))
        return file

    def setup_workspace(self):
        """Setup the RooWorkspace."""
        self.workspace.importClassCode(ROOT.RooDoubleCB.Class(), True)
        self.workspace.importClassCode(ROOT.RooFormulaVar.Class(), True)

    def set_jet_type(self):
        """Set the jet type based on the channel."""
        self.jetType = "resolved"
        if "merged" in (self.channel).lower():
            self.jetType = "merged"

    def setup_observables(self):
        """Setup the observables for the analysis."""
        logger.info("Setting up observables")
        self.mzz_name = "zz2l2q_mass"
        self.zz2l2q_mass = ROOT.RooRealVar(
            self.mzz_name, self.mzz_name, self.variableBinning[0], self.variableBinning[-1]
        )
        # self.zz2l2q_mass.setBins(self.bins)
        self.zz2l2q_mass.setBinning(self.rooBinning_resolved, "resolved")

        if self.jetType == "merged":
            self.zz2l2q_mass.SetName("zz2lJ_mass")
            self.zz2l2q_mass.SetTitle("zz2lJ_mass")
            self.zz2l2q_mass.setBinning(self.rooBinning_merged, "merged")

        self.zz2l2q_mass.setRange("fullrange", self.variableBinning[0], self.variableBinning[-1])
        self.zz2l2q_mass.setRange("fullsignalrange", self.mH - 0.25 * self.mH, self.mH + 0.25 * self.mH)
        self.rooVars["zz2l2q_mass"] = self.zz2l2q_mass

        self.rooVars["LUMI"] = ROOT.RooRealVar(
            "LUMI_{0:.0f}_{1}".format(self.sqrts, self.year),
            "Integrated Luminosity",
            self.lumi,
        )
        self.rooVars["LUMI"].setConstant(True)

        self.rooVars["MH"] = ROOT.RooRealVar("MH", "MH", self.mH)
        self.rooVars["MH"].setConstant(True)

        logger.info("Observables are set up successfully")

    def set_append_name(self):
        """Set the append name for the channel and category."""
        self.fs = "2e"
        if self.channel == self.ID_2muResolved:
            self.fs = "2mu"
        if self.channel == self.ID_2muMerged:
            self.fs = "2mu"
        postfix = self.channel + "_" + self.cat
        self.appendName = postfix
        logger.debug("appendName is channel + cat: {}".format(postfix))

    def set_category_tree(self):
        """Set the category tree based on the category."""
        self.cat_tree = "untagged"
        if self.cat == "b_tagged":
            self.cat_tree = "btagged"
        if self.cat == "vbf_tagged":
            self.cat_tree = "vbftagged"

    def set_channels(self, inputs):
        """Set the channels based on the input dictionary."""
        self.all_chan = inputs["all"]
        self.ggH_chan = inputs["ggH"]
        self.qqH_chan = inputs["qqH"]
        self.vz_chan = inputs["vz"]
        self.zjets_chan = inputs["zjets"]
        self.ttbar_chan = inputs["ttbar"]

    def setup_nuisances(self, systematics):
        """Set up the JES and BTAG nuisances and prepare RooArgList with all nuisances."""
        all_nuisances = []
        jetString = "J" if self.jetType == "merged" else "j"

        # JES nuisances for each split source
        for source in systematics.SplitSource:
            nuisance = ROOT.RooRealVar(
                "CMS_scale_{}_{}".format(jetString, source),
                "CMS_scale_{}_{}".format(jetString, source),
                0,
                -2,
                2,
            )
            all_nuisances.append(nuisance)
            self.rooVars["CMS_scale_{}_{}".format(jetString, source)] = nuisance

        # JES nuisances for each split source considering the year
        for source in systematics.SplitSourceYears:
            nuisance = ROOT.RooRealVar(
                "CMS_scale_{}_{}_{}".format(jetString, source, self.year),
                "CMS_scale_{}_{}_{}".format(jetString, source, self.year),
                0,
                -2,
                2,
            )
            all_nuisances.append(nuisance)
            self.rooVars["CMS_scale_{}_{}_{}".format(jetString, source, self.year)] = nuisance

        # Create a RooArgList from all JES nuisances
        arglist_all_JES = ROOT.RooArgList()
        for nuisance in all_nuisances:
            arglist_all_JES.add(nuisance)

        # Creating BTAG nuisance
        BTAG = ROOT.RooRealVar("BTAG_" + self.jetType, "BTAG_" + self.jetType, 0, -2, 2)
        self.rooVars["BTAG_" + self.jetType] = BTAG

        # Combining BTAG with JES nuisances for cumulative effect
        arglist_all_JES_BTAG = ROOT.RooArgList()
        # arglist_all_JES_BTAG.add(BTAG)
        for nuisance in all_nuisances:
            arglist_all_JES_BTAG.add(nuisance)
        # arglist_all_JES_BTAG = arglist_all_JES

        # Generating the formula string for cumulative effects
        cumulative_jes_effect = "+".join(
            "@{}".format(i) for i in range(len(arglist_all_JES))
        )
        cumulative_jes_effect_with_btag = "+".join(
            # "@{}".format(i + 1) for i in range(len(arglist_all_JES)) # +1 to skip the first BTAG nuisance, so len should be used with without_btag
            "@{}".format(i) for i in range(len(arglist_all_JES)) # +1 to skip the first BTAG nuisance, so len should be used with without_btag
        )

        self.rooVars["arglist_all_JES"] = arglist_all_JES
        self.rooVars["arglist_all_JES_BTAG"] = arglist_all_JES_BTAG
        self.rooVars["cumulative_jes_effect"] = cumulative_jes_effect
        self.rooVars["cumulative_jes_effect_with_btag"] = cumulative_jes_effect

        for i in range(arglist_all_JES.getSize()):
            logger.debug("{:4}. JES nuisances: {}".format(i, arglist_all_JES[i]))

        for i in range(arglist_all_JES_BTAG.getSize()):
            logger.debug("{:4}. JES nuisances with BTAG: {}".format(i, arglist_all_JES_BTAG[i]))

        logger.debug("cumulative_jes_effect: {}".format(cumulative_jes_effect))
        logger.debug("cumulative_jes_effect_with_btag: {}".format(cumulative_jes_effect_with_btag))

    def initialize_settings(self, theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, BinStatUnc, SanityCheckPlot):
        """Initialize settings for the datacard."""
        self.mH = theMH
        self.lumi = theInputs["lumi"]
        self.sqrts = theInputs["sqrts"]
        self.channel = theInputs["decayChannel"]
        self.is2D = theis2D
        self.outputDir = theOutputDir
        self.sigMorph = True
        self.bkgMorph = True
        self.cat = theCat
        self.FracVBF = theFracVBF
        self.BinStatUnc = BinStatUnc
        self.SanityCheckPlot = SanityCheckPlot

        logger.debug("Settings initialized for channel: {}".format(self.channel))

    def initialize_workspace_and_observables(self, theMH, theInputs):
        """Initialize workspace and observables."""
        self.setup_workspace()  # Setup the RooWorkspace
        self.set_append_name()  # Set the finalState (fs) and postfix variable
        self.set_category_tree()  # Set the category tree: cat_tree and cat
        self.set_channels(theInputs)  # Set the channels: ggH, qqH, vz, zjets, ttbar
        self.set_jet_type()  # Set the jet type: resolved or merged
        self.theInputs = theInputs  # Set the inputs coming from txt file
        self.variableBinning = self.binning_resolved if self.jetType == "resolved" else self.binning_merged

        logger.error("channel: {}, cat: {}, jetType: {}".format(self.channel, self.cat, self.jetType))

        ## ------------------------- OBSERVABLES ----------------------------- ##
        self.setup_observables()

        ## ---------------- SET PLOTTING STYLE ---------------- ##
        ROOT.setTDRStyle(True)
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetPadLeftMargin(0.16)

    def getRateFromSmoothedHist(self, process):
        """Get the rate for the given process from the smoothed histograms."""
        hist_key = "{}_{}_smooth".format(process, self.cat_tree)
        rate = self.background_hists_smooth.get(hist_key, None)
        if rate is not None:
            return rate.Integral()
        else:
            logger.error("Histogram key not found: {}".format(hist_key))
            return 0.0

    def get_tree_name(self):
        """Return the tree name based on the channel and category."""
        tree_mapping = {
            ("eeqq_Resolved", "vbf_tagged"): "TreeSR0",
            ("eeqq_Resolved", "b_tagged"): "TreeSR1",
            ("eeqq_Resolved", "untagged"): "TreeSR2",
            ("eeqq_Merged", "vbf_tagged"): "TreeSR3",
            ("eeqq_Merged", "b_tagged"): "TreeSR4",
            ("eeqq_Merged", "untagged"): "TreeSR5",
            ("mumuqq_Resolved", "vbf_tagged"): "TreeSR6",
            ("mumuqq_Resolved", "b_tagged"): "TreeSR7",
            ("mumuqq_Resolved", "untagged"): "TreeSR8",
            ("mumuqq_Merged", "vbf_tagged"): "TreeSR9",
            ("mumuqq_Merged", "b_tagged"): "TreeSR10",
            ("mumuqq_Merged", "untagged"): "TreeSR11",
        }
        return tree_mapping.get((self.channel, self.cat), "")

    def getData(self):
        """Retrieve data from the ROOT file and return the RooDataSet."""
        dataFileName = "CMSdata/Data_SR.root" # FIXME: Hardcoded
        logger.debug("dataFileName: {}".format(dataFileName))

        data_obs_file = self.open_root_file(dataFileName)

        treeName = self.get_tree_name()
        logger.debug("treeName: {}".format(treeName))
        tree = data_obs_file.Get(treeName)
        if not tree:
            logger.error('File "{}", or tree "{}", not found'.format(dataFileName, treeName))
            logger.error("Exiting...")
            sys.exit(1)
        else:
            logger.debug('File "{}", tree "{}" found'.format(dataFileName, treeName))

        tmpFile = ROOT.TFile("tmpFile.root", "RECREATE")  # FIXME: This is a temporary fix. We don't need tempFile.root. But if its not there then it gives error
        data_obs_tree = tree.CloneTree(0)
        logger.debug("data_obs_tree: {}".format(data_obs_tree))

        zz2lJ_mass_struct = zz2lJ_massStruct()
        data_obs_tree.Branch("zz2lJ_mass", zz2lJ_mass_struct, "zz2lJ_mass/D")
        logger.debug("zz2lJ_mass_struct: {}".format(zz2lJ_mass_struct))

        for i in range(tree.GetEntries()):
            tree.GetEntry(i)
            zz2lJ_mass_struct.zz2lJ_mass = data_obs_file.Get(treeName).zz2l2q_mass
            data_obs_tree.Fill()

        logger.info("Data entries: {}".format(tree.GetEntries()))

        datasetName = "data_obs"
        self.rooDataSet["data_obs"] = ROOT.RooDataSet(datasetName, datasetName, data_obs_tree, ROOT.RooArgSet(self.zz2l2q_mass, self.rooVars["D"]))
        # logger.debug("data_obs: {}".format(self.rooDataSet["data_obs"]))
        # self.rooDataSet["data_obs"].Print("v")
        # exit()
        # FIXME: Check if the data_obs is filled correctly??? Not sure if the way "D" is added fine? As I think D is empty
        #               1. Possible check is to print the data_obs_tree and see if it has the correct values
        #               2. Check if the "D" has some values in it or not
        #               3. Also, compare these values from the legacy code

        logger.debug("data_obs: {}".format(self.rooDataSet["data_obs"]))
        return self.rooDataSet["data_obs"]

    def getRooProdPDFofMorphedSignal(self, TString_sig, templateSigName):
        """Get the RooProdPDF of the morphed signal."""
        logger.debug("Inside getRooProdPDFofMorphedSignal")

        self.rooVars["funcList_ggH"] = ROOT.RooArgList()
        self.rooVars["funcList_VBF"] = ROOT.RooArgList()

        sigTempFile = self.open_root_file(templateSigName)
        #  Get the rooDataHist for signal templates
        for tag in ["", "_up", "_dn"]:
            sigTemplate = sigTempFile.Get(TString_sig + tag)
            if not sigTemplate:
                logger.error("Failed to get signal template: {}".format(TString_sig + tag))
                continue

            sigTempDataHist_tag = "_Up" if tag == "_up" else "_Down" if tag == "_dn" else ""
            TemplateName = "sigTempDataHist_" + TString_sig + sigTempDataHist_tag + "_" + str(self.year)
            self.rooDataHist[TemplateName] = ROOT.RooDataHist(
                        TemplateName, TemplateName, ROOT.RooArgList(self.zz2l2q_mass, self.rooVars["D"]), sigTemplate
                    )
            logger.debug("Created rooDataHist: {}".format(TemplateName))

        # Get the rooHistPdf for signal templates separately for ggH and VBF
        for sample in ["ggH", "VBF"]:
            for tag in ["", "_up", "_dn"]:
                # continue for up and dn if sigMorph is False
                if not self.sigMorph and tag != "":
                    continue
                sigTempDataHist_tag = "_Up" if tag == "_up" else "_Down" if tag == "_dn" else ""
                pdfName = "sigTemplatePdf_{}_{}{}_{}".format(sample, TString_sig, sigTempDataHist_tag, self.year)
                TemplateName = "sigTempDataHist_" + TString_sig + sigTempDataHist_tag + "_" + str(self.year)
                logger.debug("pdfName: {}".format(pdfName))
                logger.debug("TemplateName: {}".format(TemplateName))
                self.rooVars[pdfName] = ROOT.RooHistPdf(
                    pdfName,
                    pdfName,
                    ROOT.RooArgSet(self.zz2l2q_mass, self.rooVars["D"]),
                    self.rooDataHist[TemplateName],
                )

                self.rooVars[pdfName].graphVizTree("{}/figs/dotFiles/{}.dot".format(self.outputDir, pdfName))

                if sample == "ggH":
                    self.rooVars["funcList_ggH"].add(self.rooVars[pdfName])
                elif sample == "VBF":
                    self.rooVars["funcList_VBF"].add(self.rooVars[pdfName])

        # morphing
        morphSigVarName = "CMS_zz2l2q_sigMELA_" + self.jetType
        self.rooVars[morphSigVarName] = ROOT.RooRealVar(morphSigVarName, morphSigVarName, 0, -2, 2)
        if self.sigMorph:
            self.rooVars[morphSigVarName].setConstant(False)
        else:
            self.rooVars[morphSigVarName].setConstant(True)

        self.rooVars["morphVarListSig_" + self.jetType] = ROOT.RooArgList()
        if self.sigMorph:
            self.rooVars["morphVarListSig_" + self.jetType].add(self.rooVars[morphSigVarName]) ## INFO: just one morphing for all signal processes

        sample_list = ["ggH", "VBF"]
        for sample in sample_list:
            logger.debug("sample: {}".format(sample))
            TemplateName = "sigTemplateMorphPdf_" + sample + "_" + TString_sig + "_" + str(self.year)
            self.rooVars[TemplateName] = ROOT.FastVerticalInterpHistPdf2D(
                TemplateName,
                TemplateName,
                self.zz2l2q_mass,
                self.rooVars["D"],
                True,
                self.rooVars["funcList_" + sample],
                self.rooVars["morphVarListSig_" + self.jetType],
                1.0,
                1,
            )

        # 2D -> mzz + Djet
        for sample in sample_list:
            if sample == "ggH":
                tag_temp = "ggH"
            elif sample == "VBF":
                tag_temp = "qqH"

            pdfName = "sigTemplatePdf_{}_{}{}_{}".format(sample, TString_sig, "", self.year)
            TemplateName = "sigTemplateMorphPdf_" + sample + "_" + TString_sig + "_" + str(self.year)
            name = "sigCB2d_{}_{}".format(tag_temp, self.year)
            logger.debug("======  parameters entered in rooProdPdf  ======")

            self.rooProdPdf[name] = ROOT.RooProdPdf(
                name,
                name,
                ROOT.RooArgSet(self.signalCBs["signalCB_{}_{}".format(sample, self.channel)]),
                ROOT.RooFit.Conditional(
                    # ROOT.RooArgSet(self.rooVars[TemplateName]), # Uncomment to use FastVerticalInterpHistPdf2D
                    ROOT.RooArgSet(self.rooVars[pdfName]), # Uncomment to just use RooHistPdf not FastVerticalInterpHistPdf2D
                    ROOT.RooArgSet(self.rooVars["D"]),
                ),
            )

        for sample in sample_list:
            if sample == "ggH":
                tag_temp = "ggH"
            elif sample == "VBF":
                tag_temp = "qqH"

            name = "sigCB2d_{}_{}".format(tag_temp, self.year)
            if sample == "ggH":
                self.rooProdPdf[name].SetNameTitle("ggH_hzz", "ggH_hzz")
            elif sample == "VBF":
                self.rooProdPdf[name].SetNameTitle("qqH_hzz", "qqH_hzz")

            getattr(self.workspace, "import")(self.rooProdPdf[name], ROOT.RooFit.RecycleConflictNodes())
            logger.debug("added to workspace: {}".format(name))

    def get_Backgrounds_funcList(self):
        """Get the function list for Zjets."""
        templatezjetsBkgName = "templates2D/2l2q_spin0_template_{}.root".format(self.year)
        bkg2DTemplateFile = self.open_root_file(templatezjetsBkgName)

        for bkg_process in self.background_list:
            # Initialize funcList_zjets as RooArgList
            if "funcList_{}".format(bkg_process) not in self.rooArgSets:
                self.rooArgSets["funcList_{}".format(bkg_process)] = ROOT.RooArgList()

            TString_bkg = "{}_resolved".format(self.background_map_2DTemplates[bkg_process])
            if self.channel in ["mumuqq_Merged", "eeqq_Merged"]:
                TString_bkg = "{}_merged".format(self.background_map_2DTemplates[bkg_process])

            variations = ["", "_Up", "_Down"]
            for variation in variations:
                logger.debug("variation: {}".format(variation))
                if not self.bkgMorph and variation != "":
                    logger.error("Skipping variation: {}".format(variation))
                    continue

                variations_tag_for_hist = "_up" if variation == "_Up" else "_dn" if variation == "_Down" else ""
                logger.debug("variations: {}, variations_tag_for_hist: {}".format(variation, variations_tag_for_hist))
                logger.debug("Looking for hist: {}".format(TString_bkg + variations_tag_for_hist))

                bkgsTemplate = bkg2DTemplateFile.Get(TString_bkg + variations_tag_for_hist)
                if not bkgsTemplate:
                    logger.debug("Failed to get {} template: {}".format(bkg_process, TString_bkg + variations_tag_for_hist))
                    continue

                logger.debug("bkgsTemplate: Name: {} Title: {} NbinsX: {}".format(bkgsTemplate.GetName(), bkgsTemplate.GetTitle(), bkgsTemplate.GetNbinsX()))

                TemplateName = "{}TempDataHist_{}{}_{}".format(bkg_process, TString_bkg, variation, self.year)
                self.rooDataHist[TemplateName] = ROOT.RooDataHist(
                    TemplateName,
                    TemplateName,
                    ROOT.RooArgList(self.zz2l2q_mass, self.rooVars["D"]),
                    bkgsTemplate,
                )

                PdfName = "{}TemplatePdf_{}{}_{}".format(bkg_process, TString_bkg, variation, self.year)
                self.rooDataHist[PdfName] = ROOT.RooHistPdf(
                    PdfName,
                    PdfName,
                    ROOT.RooArgSet(self.zz2l2q_mass, self.rooVars["D"]),
                    self.rooDataHist[TemplateName],
                )
                self.rooDataHist[PdfName].graphVizTree("{}/figs/dotFiles/{}.dot".format(self.outputDir, PdfName))

                self.rooArgSets["funcList_{}".format(bkg_process)].add(self.rooDataHist[PdfName])

            for i in range(self.rooArgSets["funcList_{}".format(bkg_process)].getSize()):
                logger.debug("{:2}: funcList_{}: {}".format(i, bkg_process, self.rooArgSets["funcList_{}".format(bkg_process)].at(i).GetName()))

    def getRooProdPDFofMorphedBackgrounds(self):
        """Get the RooProdPDF of morphed backgrounds."""
        for process in self.background_list:
            vzTemplateName = "{}_{}_{}".format(process, self.appendName, self.year)
            vzTemplateMVV = self.background_hists_From1DTemplate["{}_template".format(process)]
            # category = self.cat_tree
            # vzTemplateMVV = self.background_hists["{}_{}_template".format(process, category)]
            logger.debug("vzTemplateName: {}, \n\tvzTemplateMVV: {}".format(vzTemplateName, vzTemplateMVV))
            logger.debug("TYPE: {}".format(type(vzTemplateMVV)))

            TString_bkg = "{}_resolved".format(self.background_map_2DTemplates[process])
            if self.channel in ["mumuqq_Merged", "eeqq_Merged"]:
                TString_bkg = "{}_merged".format(self.background_map_2DTemplates[process])

            self.rooDataHist[vzTemplateName] = ROOT.RooDataHist(
                vzTemplateName,
                vzTemplateName,
                ROOT.RooArgList(self.zz2l2q_mass),
                vzTemplateMVV,  # INFO: Whether we should use vzTemplateMVV or vzTemplateMVV_smooth
            )

            vzTemplatePdfName = "{}Pdf".format(vzTemplateName)
            self.rooDataHist[vzTemplatePdfName] = ROOT.RooHistPdf(
                vzTemplatePdfName,
                vzTemplatePdfName,
                ROOT.RooArgSet(self.zz2l2q_mass),
                self.rooDataHist[vzTemplateName],
            )
            self.rooDataHist[vzTemplatePdfName].graphVizTree("{}/figs/dotFiles/{}.dot".format(self.outputDir, vzTemplatePdfName))

            for i in range(self.rooArgSets["funcList_{}".format(process)].getSize()):
                logger.debug("{:2}: funcList_{}: {}".format(i, process, self.rooArgSets["funcList_{}".format(process)].at(i).GetName()))

            # morphing
            for i in range(self.rooArgSets["morphVarListBkg"].getSize()):
                logger.debug("{:2}: morphVarListBkg: {}".format(i, self.rooArgSets["morphVarListBkg"].at(i).GetName()))

            TemplateName = "bkgTemplateMorphPdf_{}_{}_{}".format(process, self.jetType, self.year)
            self.rooVars[TemplateName] = ROOT.FastVerticalInterpHistPdf2D(
                TemplateName,
                TemplateName,
                self.zz2l2q_mass,
                self.rooVars["D"],
                True, # If conditional = true, the pdf is separately normalized integrating on (y) for each specific (x) bin
                self.rooArgSets["funcList_{}".format(process)], # INFO: identical to all background processes
                # self.rooArgSets["funcList_{}".format("zjets")], # INFO: identical to all background processes
                self.rooArgSets["morphVarListBkg"], # INFO: identical to all background processes
                1.0,
                1,
            )

            name = "bkg2d_{}_{}".format(process, self.year)
            self.rooProdPdf[name] = ROOT.RooProdPdf(
                name,
                name,
                ROOT.RooArgSet(self.rooDataHist[vzTemplatePdfName]),
                ROOT.RooFit.Conditional(
                    # ROOT.RooArgSet(self.rooVars["bkgTemplateMorphPdf_{}_{}_{}".format(process, self.jetType, self.year)]), # Uncomment to use FastVerticalInterpHistPdf2D
                    ROOT.RooArgSet(self.rooDataHist["{}TemplatePdf_{}{}_{}".format(process, TString_bkg, "", self.year)]), # Uncomment to use HistPdf not the FastVerticalInterpHistPdf2D
                    ROOT.RooArgSet(self.rooVars["D"]),
                ),
            )

            self.rooProdPdf[name].SetNameTitle("bkg_{}".format(process), "bkg_{}".format(process))

            getattr(self.workspace, "import")(self.rooProdPdf[name], ROOT.RooFit.RecycleConflictNodes())

        if self.BinStatUnc:
            for hist in self.background_hists:
                logger.debug("hist: {}, {}".format(hist, type(self.background_hists[hist])))
                # logger.error("\tName: {}".format(self.background_hists[hist].GetName()))

            # # from the list self.background_hists get new list that contains only the histograms with the name "*_Bin*_up"
            # # up_hists = [hist for hist in self.background_hists if "Bin" in hist and "up" in hist]
            # up_hists = []
            # for hist in self.background_hists:
            #     if "Bin" in hist and "up" in hist:
            #         up_hists.append(self.background_hists[hist])
            # logger.debug("=====================================")
            # for hist in up_hists:
            #     logger.debug("hist: {}, {}".format(hist, type(up_hists[hist])))
            # # exit()
            # categories = {"untagged", "btagged", "vbftagged"}
            categories = {self.cat_tree}
            for process in self.background_list:
                TString_bkg = "{}_resolved".format(self.background_map_2DTemplates[process])
                if self.channel in ["mumuqq_Merged", "eeqq_Merged"]:
                    TString_bkg = "{}_merged".format(self.background_map_2DTemplates[process])
                for category in categories:
                #     # Plot nominal, up and down histograms on one canvas for each category
                #     # temp_nom = self.background_hists_From1DTemplate["{}_template".format(process)]
                #     temp_nom = self.background_hists["{}_{}_template".format(process, category)]
                #     temp_up = self.background_hists["{}_{}_template_{}".format(process, category, "up")]
                #     temp_down = self.background_hists["{}_{}_template_{}".format(process, category, "down")]

                #     # Create a canvas
                #     c = ROOT.TCanvas("c", "c", 800, 800)
                #     c.cd()
                #     # Draw the histograms
                #     temp_nom.SetLineColor(ROOT.kBlack)
                #     temp_nom.SetMarkerColor(ROOT.kBlack)
                #     temp_nom.SetMarkerStyle(1)
                #     temp_nom.SetMarkerSize(1.5)
                #     temp_nom.Draw("hist")
                #     temp_up.SetLineColor(ROOT.kRed)
                #     temp_up.SetMarkerColor(ROOT.kRed)
                #     temp_up.SetMarkerStyle(1)
                #     temp_up.SetMarkerSize(0.5)
                #     temp_up.Draw("hist same")
                #     temp_down.SetLineColor(ROOT.kBlue)
                #     temp_down.SetMarkerColor(ROOT.kBlue)
                #     temp_down.SetMarkerStyle(2)
                #     temp_down.SetMarkerSize(0.5)
                #     temp_down.Draw("hist same")
                #     # Draw the legend
                #     leg = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
                #     leg.AddEntry(temp_nom, "Nominal", "l")
                #     leg.AddEntry(temp_up, "Up", "l")
                #     leg.AddEntry(temp_down, "Down", "l")
                #     leg.Draw()
                #     # Save the canvas
                #     c.SaveAs("{}/figs/{}_{}_{}_{}.pdf".format(self.outputDir, process, category, self.channel, self.year))
                #     # exit()


                    for syst in ["Up", "Down"]:
                        vzTemplateName = "{}_{}_{}_{}_{}".format(process, self.appendName, self.year, category, syst)

                        logger.debug("HIST name: {}".format("{}_{}_template_{}".format(process, category, syst.lower())))

                        vzTemplateMVV = self.background_hists["{}_{}_template_{}".format(process, category, syst.lower())]
                        logger.debug("vzTemplateName: {}, \n\tvzTemplateMVV: {}".format(vzTemplateName, vzTemplateMVV))
                        logger.debug("TYPE: {}".format(type(vzTemplateMVV)))

                        self.rooDataHist[vzTemplateName] = ROOT.RooDataHist(
                            vzTemplateName,
                            vzTemplateName,
                            ROOT.RooArgList(self.zz2l2q_mass),
                            vzTemplateMVV,  # INFO: Whether we should use vzTemplateMVV or vzTemplateMVV_smooth
                        )

                        vzTemplatePdfName = "{}Pdf{}".format(vzTemplateName, syst)
                        self.rooDataHist[vzTemplatePdfName] = ROOT.RooHistPdf(
                            vzTemplatePdfName,
                            vzTemplatePdfName,
                            ROOT.RooArgSet(self.zz2l2q_mass),
                            self.rooDataHist[vzTemplateName],
                        )
                        self.rooDataHist[vzTemplatePdfName].graphVizTree("{}/figs/dotFiles/{}.dot".format(self.outputDir, vzTemplatePdfName))

                        for i in range(self.rooArgSets["funcList_{}".format(process)].getSize()):
                            logger.debug("{:2}: funcList_{} {}".format(i,  process, self.rooArgSets["funcList_{}".format(process)].at(i).GetName()))

                        # morphing
                        for i in range(self.rooArgSets["morphVarListBkg"].getSize()):
                            logger.debug("{:2}: morphVarListBkg: {}".format(i, self.rooArgSets["morphVarListBkg"].at(i).GetName()))

                        TemplateName = "bkgTemplateMorphPdf_{}_{}_{}{}".format(process, self.jetType, self.year, syst)
                        self.rooVars[TemplateName] = ROOT.FastVerticalInterpHistPdf2D(
                            TemplateName,
                            TemplateName,
                            self.zz2l2q_mass,
                            self.rooVars["D"],
                            True, # If conditional = true, the pdf is separately normalized integrating on (y) for each specific (x) bin
                            self.rooArgSets["funcList_{}".format(process)], # INFO: identical to all background processes
                            # self.rooArgSets["funcList_{}".format("zjets")], # INFO: identical to all background processes
                            self.rooArgSets["morphVarListBkg"], # INFO: identical to all background processes
                            1.0,
                            1,
                        )

                        for hist in self.rooDataHist:
                            logger.debug("hist: {}".format(hist))

                        name = "bkg2d_{}_{}{}".format(process, self.year, syst)
                        self.rooProdPdf[name] = ROOT.RooProdPdf(
                            name,
                            name,
                            ROOT.RooArgSet(self.rooDataHist[vzTemplatePdfName]),
                            ROOT.RooFit.Conditional(
                                # ROOT.RooArgSet(self.rooVars["bkgTemplateMorphPdf_{}_{}_{}".format(process, self.jetType, self.year)]), # Uncomment to use FastVerticalInterpHistPdf2D
                                ROOT.RooArgSet(self.rooDataHist["{}TemplatePdf_{}{}_{}".format(process, TString_bkg, "_"+syst, self.year)]), # Uncomment to use HistPdf not the FastVerticalInterpHistPdf2D
                                ROOT.RooArgSet(self.rooVars["D"]),
                            ),
                        )

                        self.rooProdPdf[name].SetNameTitle(
                            "bkg_{}_{}_{}{}".format(
                                process, process, category, syst
                            ),
                            "bkg_{}_{}_{}{}".format(
                                process, process, category, syst
                            ),
                        )

                        getattr(self.workspace, "import")(self.rooProdPdf[name], ROOT.RooFit.RecycleConflictNodes())

    def get_signal_shape_mean_error(self, SignalShape):
        """Define systematic variables for both electron and muon channels."""
        systematic_vars = [
            ("mean_e_sig", "CMS_zz2l2q_mean_e_sig", 0.0, -10.0, 10.0),
            ("sigma_e_sig", "CMS_zz2l2q_sigma_e_sig", 0.0, -10.0, 10.0),
            ("mean_m_sig", "CMS_zz2l2q_mean_m_sig", 0.0, -10.0, 10.0),
            ("sigma_m_sig", "CMS_zz2l2q_sigma_m_sig", 0.0, -10.0, 10.0),
            ("mean_j_sig", "CMS_zz2l2q_mean_j_sig", 0.0, -10.0, 10.0),
            ("sigma_j_sig", "CMS_zz2l2q_sigma_j_sig", 0.0, -10.0, 10.0),
            ("mean_J_sig", "CMS_zz2lJ_mean_J_sig", 0.0, -10.0, 10.0),
            ("sigma_J_sig", "CMS_zz2lJ_sigma_J_sig", 0.0, -10.0, 10.0),
        ]
        # Initialize RooRealVar objects for each variable
        for varName, title, init_val, min_val, max_val in systematic_vars:
            self.rooVars[varName] = ROOT.RooRealVar(title, varName, init_val, min_val, max_val)
            self.rooVars[varName].setVal(init_val)

        # Initialize uncertainty variables from inputs
        uncertainty_vars = [
            ("mean_m_err", "CMS_zz2l2q_mean_m_err"),
            ("mean_e_err", "CMS_zz2l2q_mean_e_err"),
            ("mean_j_err", "CMS_zz2l2q_mean_j_err"),
            ("mean_J_err", "CMS_zz2lJ_mean_J_err"),
            ("sigma_m_err", "CMS_zz2l2q_sigma_m_err"),
            ("sigma_e_err", "CMS_zz2l2q_sigma_e_err"),
            ("sigma_j_err", "CMS_zz2l2q_sigma_j_err"),
            ("sigma_J_err", "CMS_zz2lJ_sigma_J_err"),
        ]
        for var_name, input_key in uncertainty_vars:
            self.rooVars[var_name] = ROOT.RooRealVar(var_name, var_name, float(self.theInputs[input_key]))

        # Electon or muon channel distinction
        lep_type = "e" if "ee" in self.channel else "m"

        # Define error and scale factor formulas for each channel
        jet_suffix = "J" if "merged" in self.channel.lower() else "j"
        mean_formula = "(@0*@1*@3 + @0*@2*@4)/2"
        sigma_formula = "TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))"

        self.rooVars["mean_err_" + self.channel] = ROOT.RooFormulaVar(
            "mean_err_" + self.channel,
            mean_formula,
            ROOT.RooArgList(
                self.rooVars["MH"],
                self.rooVars["mean_{}_sig".format(lep_type)],
                self.rooVars["mean_{}_sig".format(jet_suffix)],
                self.rooVars["mean_{}_err".format(lep_type)],
                self.rooVars["mean_{}_err".format(jet_suffix)],
            ),
        )

        self.rooFormulaVars["sigma_SF_" + self.channel] = ROOT.RooFormulaVar(
            "sigma_SF_" + self.channel,
            sigma_formula,
            ROOT.RooArgList(
                self.rooVars["sigma_{}_sig".format(lep_type)],
                self.rooVars["sigma_{}_sig".format(jet_suffix)],
                self.rooVars["sigma_{}_err".format(lep_type)],
                self.rooVars["sigma_{}_err".format(jet_suffix)],
            ),
        )

        signal_type_list = ["ggH", "VBF"]
        for signal_type in signal_type_list:
            sigma_value = (SignalShape.Get("sigma")).GetListOfFunctions().First().Eval(self.mH)
            self.rooVars["sigma_{}_{}".format(signal_type, self.channel)] = ROOT.RooRealVar(
                "sigma_{}_{}".format(signal_type, self.channel),
                "sigma_{}_{}".format(signal_type, self.channel),
                sigma_value,
            )

            self.rooVars["rfv_sigma_{}_{}".format(signal_type, self.channel)] = ROOT.RooFormulaVar(
                "rfv_sigma_{}_{}".format(signal_type, self.channel),
                "@0*@1",
                ROOT.RooArgList(
                    self.rooVars["sigma_{}_{}".format(signal_type, self.channel)],
                    self.rooFormulaVars["sigma_SF_" + self.channel],
                ),
            )

    def setup_signal_shape(self, SignalShape, systematics, signal_type, channel):
        """Setup the signal shape parameters."""
        name = "bias_{}_{}".format(signal_type, channel)
        self.rooVars["bias_{}_{}".format(signal_type, channel)] = ROOT.RooRealVar(
            name,
            name,
            SignalShape.Get("mean").GetListOfFunctions().First().Eval(self.mH)
            - self.mH,
        )
        name = "mean_{}_{}".format(signal_type, channel)
        self.rooVars["mean_{}_{}".format(signal_type, channel)] = ROOT.RooFormulaVar(
            name,
            "@0+@1",
            ROOT.RooArgList(
                self.rooVars["MH"], self.rooVars["bias_{}_{}".format(signal_type, channel)],
            )
        )

        name = "rfv_mean_{}_{}".format(signal_type, channel)
        self.rooVars["rfv_mean_{}_{}".format(signal_type, channel)] = (
            ROOT.RooFormulaVar(
                name,
                "@0+@1",
                ROOT.RooArgList(
                    self.rooVars["mean_{}_{}".format(signal_type, channel)],
                    self.rooVars["mean_err_" + self.channel],
                ),
            )
        )

        self.rooVars["a1_{}_{}_{}".format(signal_type, channel, self.year)] = (
            ROOT.RooRealVar(
                "a1_{}_{}_{}".format(signal_type, channel, self.year),
                "Low tail",
                SignalShape.Get("a1").GetListOfFunctions().First().Eval(self.mH),
            )
        )
        self.rooVars["n1_{}_{}_{}".format(signal_type, channel, self.year)] = (
            ROOT.RooRealVar(
                "n1_{}_{}_{}".format(signal_type, channel, self.year),
                "Low tail parameter",
                SignalShape.Get("n1").GetListOfFunctions().First().Eval(self.mH),
            )
        )
        self.rooVars["a2_{}_{}_{}".format(signal_type, channel, self.year)] = (
            ROOT.RooRealVar(
                "a2_{}_{}_{}".format(signal_type, channel, self.year),
                "High tail",
                SignalShape.Get("a2").GetListOfFunctions().First().Eval(self.mH),
            )
        )
        self.rooVars["n2_{}_{}_{}".format(signal_type, channel, self.year)] = (
            ROOT.RooRealVar(
                "n2_{}_{}_{}".format(signal_type, channel, self.year),
                "High tail parameter",
                SignalShape.Get("n2").GetListOfFunctions().First().Eval(self.mH),
            )
        )
        self.signalCBs["signalCB_{}_{}".format(signal_type, channel)] = ROOT.RooDoubleCB(
            "signalCB_{}_{}".format(signal_type, channel),
            "Double Crystal Ball Model for {} in {}".format(signal_type, channel),
            self.rooVars["zz2l2q_mass"],
            self.rooVars["rfv_mean_{}_{}".format(signal_type, channel)],
            self.rooVars["rfv_sigma_{}_{}".format(signal_type, self.channel)],
            self.rooVars["a1_{}_{}_{}".format(signal_type, channel, self.year)],
            self.rooVars["n1_{}_{}_{}".format(signal_type, channel, self.year)],
            self.rooVars["a2_{}_{}_{}".format(signal_type, channel, self.year)],
            self.rooVars["n2_{}_{}_{}".format(signal_type, channel, self.year)]
        )

        fullRangeSigRate = (
            self.signalCBs["signalCB_{}_{}".format(signal_type, self.channel)]
            .createIntegral(
                ROOT.RooArgSet(self.zz2l2q_mass), ROOT.RooFit.Range("fullsignalrange")
            )
            .getVal()
        )
        fullRangeRate = (
            self.signalCBs["signalCB_{}_{}".format(signal_type, self.channel)]
            .createIntegral(
                ROOT.RooArgSet(self.zz2l2q_mass), ROOT.RooFit.Range("fullrange")
            )
            .getVal()
        )
        logger.debug("{} rate: {}".format(self.signalCBs["signalCB_{}_{}".format(signal_type, channel)].GetName(), fullRangeSigRate))

    def getSignalRates(self, signal_type):
        """Calculate and return the signal rates for ggH and VBF."""
        logger.debug("Calculating signal rates for {}".format(signal_type))

        file_path = "SigEff/2l2q_Efficiency_spin0_{}_{}.root".format(signal_type, self.year)
        accxeff_file = ROOT.TFile(file_path)
        logger.debug("Opened file: {}".format(file_path))

        categories = ["vbf-tagged", "b-tagged", "untagged"]
        accxeff = {
            "{}_accxeff_{}".format(signal_type, cat): accxeff_file.Get(
                "spin0_{}_{}_{}".format(signal_type, self.channel, cat)
            )
            .GetListOfFunctions()
            .First()
            .Eval(self.mH)
            for cat in categories
        }
        logger.debug("Acc x Eff for {}: {}".format(signal_type, accxeff))

        vbf_ratio = accxeff[signal_type + "_accxeff_vbf-tagged"] / (
            accxeff[signal_type + "_accxeff_untagged"]
            + accxeff[signal_type + "_accxeff_b-tagged"]
        )
        btag_ratio = (
            accxeff[signal_type + "_accxeff_b-tagged"]
            / accxeff[signal_type + "_accxeff_untagged"]
            if accxeff[signal_type + "_accxeff_untagged"] != 0
            else 0
        )
        logger.debug("VBF ratio: {}, B-tag ratio: {}".format(vbf_ratio, btag_ratio))

        formatted_name = self.appendName.replace("b_tagged", "b-tagged").replace(
            "vbf_tagged", "vbf-tagged"
        )
        sig_rate_shape = (
            accxeff_file.Get("spin0_{}_{}".format(signal_type, formatted_name))
            .GetListOfFunctions()
            .First()
            .Eval(self.mH)
        )

        sig_rate_shape *= self.sigFraction
        sig_rate_shape = max(sig_rate_shape, 0.0)
        logger.debug("{} Signal rate: {}".format(signal_type, sig_rate_shape))

        accxeff_file.Close()
        return sig_rate_shape, vbf_ratio, btag_ratio

    def calculate_background_rates(self, process):
        """Calculate and return background rates for various processes based on the histograms provided in self.background_hists."""
        bkgRate_Shape = {
            "untagged": self.background_hists[process + "_untagged_template"].Integral(),
            "btagged": self.background_hists[process + "_btagged_template"].Integral(),
            "vbftagged": self.background_hists[process + "_vbftagged_template"].Integral(),
        }

        if self.cat == "untagged":
            return bkgRate_Shape["untagged"]
        elif self.cat == "b_tagged":
            return bkgRate_Shape["btagged"]
        elif self.cat == "vbf_tagged":
            return bkgRate_Shape["vbftagged"]

    def calculate_background_rates_vz(self):
        """Calculate and return background rates for vz process based on the histograms provided in self.background_hists."""
        bkgRate_vz_Shape = {
            "untagged": self.background_hists_From1DTemplate["vz_untagged_template"].Integral(),
            "btagged": self.background_hists_From1DTemplate["vz_btagged_template"].Integral(),
            "vbftagged": self.background_hists_From1DTemplate["vz_vbftagged_template"].Integral(),
        }

        btagRatio = (
            bkgRate_vz_Shape["btagged"] / bkgRate_vz_Shape["untagged"]
            if bkgRate_vz_Shape["untagged"]
            else 0
        )
        vbfRatio = (
            bkgRate_vz_Shape["vbftagged"]
            / (bkgRate_vz_Shape["untagged"] + bkgRate_vz_Shape["btagged"])
            if (bkgRate_vz_Shape["untagged"] + bkgRate_vz_Shape["btagged"])
            else 0
        )

        cat_suffix = (
            self.cat_tree
            if self.cat_tree in ["untagged", "btagged", "vbftagged"]
            else "untagged"
        )
        jet_prefix = "resolved" if "resolved" in self.jetType else "merged"
        formula = {
            "resolved_untagged": "(1-0.05*@0*{btagRatio})*(1-0.1*({cumulative_jes_effect_with_btag})*{vbfRatio})",
            "resolved_btagged": "(1+0.05*@0)*(1-0.1*({cumulative_jes_effect_with_btag})*{vbfRatio})",
            "resolved_vbftagged": "(1+0.1*({cumulative_jes_effect}))",
            "merged_untagged": "(1-0.2*@0*{btagRatio})*(1-0.1*({cumulative_jes_effect_with_btag})*{vbfRatio})",
            "merged_btagged": "(1+0.2*@0)*(1-0.1*({cumulative_jes_effect_with_btag})*{vbfRatio})",
            "merged_vbftagged": "(1+0.1*({cumulative_jes_effect}))",
        }.get("{}_{}".format(jet_prefix, cat_suffix))

        logger.debug("(cat, jet): ({}, {})".format(cat_suffix, jet_prefix))
        logger.debug(formula.format(
                btagRatio=btagRatio,
                cumulative_jes_effect=self.rooVars["cumulative_jes_effect"],
                cumulative_jes_effect_with_btag=self.rooVars["cumulative_jes_effect_with_btag"],
                vbfRatio=vbfRatio,
            )
        )
        logger.debug(formula)

        if self.DEBUG:
            logger.warning("================== Not BTAG =====================")
            logger.warning(self.rooVars["arglist_all_JES"].Print("v"))
            logger.warning("==================  BTAG =====================")
            logger.warning(self.rooVars["arglist_all_JES_BTAG"].Print("v"))
            logger.warning("==================================================")

        rfvSigRate_vz = ROOT.RooFormulaVar(
            "bkg_vz_norm",
            formula.format(
                btagRatio=btagRatio,
                cumulative_jes_effect=self.rooVars["cumulative_jes_effect"],
                cumulative_jes_effect_with_btag=self.rooVars[
                    "cumulative_jes_effect_with_btag"
                ],
                vbfRatio=vbfRatio,
            ),
            (
                self.rooVars["arglist_all_JES"]
                if "vbftagged" in cat_suffix
                else self.rooVars["arglist_all_JES_BTAG"]
            ),
        )
        getattr(self.workspace, "import")(rfvSigRate_vz, ROOT.RooFit.RecycleConflictNodes())
        if self.DEBUG:
            logger.debug("bkg_vz_norm: {}".format(rfvSigRate_vz.Print("v")))
            logger.debug("bkg_vz_norm: {}".format(rfvSigRate_vz.getVal()))

    def setup_background_shapes_ReproduceRate_fs(self):
        """Set the histogram templates for the background shapes for the given final state."""
        template_file_path = "templates1D/Template1D_spin0_{}_{}.root".format(self.fs, self.year)
        temp_file_fs = ROOT.TFile(template_file_path, "READ")

        if not temp_file_fs or temp_file_fs.IsZombie():
            raise IOError("Could not open the template file: {}".format(template_file_path))

        prefix = "hmass_{}SR".format(self.jetType)

        categories = {
            "untagged": "",
            "btagged": "btag",
            "vbftagged": "vbf",
        }

        for key, suffix in self.hist_suffixes.items():
            for category, cat_string in categories.items():
                hist_name = "{}{}_{}".format(prefix, cat_string, suffix)
                hist = temp_file_fs.Get(hist_name)

                if not hist:
                    raise ValueError("Histogram {} not found in file: {}".format(hist_name, template_file_path))

                hist.SetDirectory(ROOT.gROOT)
                logger.debug("Range of histogram {}: {} to {}".format(hist_name, hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax()))

                hist_key = "{}_{}_template".format(key, category)
                self.background_hists_From1DTemplate[hist_key] = hist
                logger.debug("Stored histogram {} in background_hists_From1DTemplate".format(hist_key))

        for key, hist in self.background_hists_From1DTemplate.items():
            logger.debug("Background histogram - key: {}, hist: {}".format(key, hist))

        temp_file_fs.Close()

    def setup_background_shapes_ReproduceRate_2l(self):
        """Set the histogram templates for the background shapes for the inclusive 2l final state and inclusive jet category."""
        template_file_path = "templates1D/Template1D_spin0_2l_{}.root".format(self.year)
        temp_file_fs = ROOT.TFile(template_file_path, "READ")

        if not temp_file_fs or temp_file_fs.IsZombie():
            raise IOError("Could not open the template file: {}".format(template_file_path))

        prefix = "hmass_{}SR".format(self.jetType)

        for key, suffix in self.hist_suffixes.items():
            hist_name = "{}_{}".format(prefix, suffix)
            hist = temp_file_fs.Get(hist_name)

            if not hist:
                raise ValueError("Histogram {} not found in file: {}".format(hist_name))

            # Detach histogram from file ref: https://root-forum.cern.ch/t/nonetype-feturned-from-function-that-returns-th1f/18287/2?u=ramkrishna
            hist.SetDirectory(ROOT.gROOT)
            logger.debug("Range of histogram {}: {} to {}".format(hist_name, hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax()))

            hist_key = "{}_template".format(key)
            self.background_hists_From1DTemplate[hist_key] = hist
            logger.debug("Stored histogram {} in background_hists_From1DTemplate".format(hist_key))

        for key, hist in self.background_hists_From1DTemplate.items():
            logger.debug("Background histogram - key: {}, hist: {}".format(key, hist))

        temp_file_fs.Close()

    def setup_background_shapes_ReproduceRate(self, process):
        """Obtain the rate of the background process.

        It takes histogram from the 1D templates and rebin them to match the range and bins specified.

        """
        categories = ["_untagged", "_btagged", "_vbftagged", ""]

        vzTemplateMVV = self.background_hists_From1DTemplate["{}{}_template".format(process, "")]

        hist_smooth_name = "{}_smooth".format(process)
        self.background_hists_smooth["{}{}_smooth".format(process, "")] = ROOT.TH1F(hist_smooth_name, hist_smooth_name, len(self.variableBinning) -1, array('d', self.variableBinning))
        self.background_hists_smooth["{}{}_smooth".format(process, "_untagged")] = ROOT.TH1F(hist_smooth_name + "_untagged", hist_smooth_name + "_untagged", len(self.variableBinning) -1, array('d', self.variableBinning))
        self.background_hists_smooth["{}{}_smooth".format(process, "_btagged")] = ROOT.TH1F(hist_smooth_name + "_btagged", hist_smooth_name + "_btagged", len(self.variableBinning) -1, array('d', self.variableBinning))
        self.background_hists_smooth["{}{}_smooth".format(process, "_vbftagged")] = ROOT.TH1F(hist_smooth_name + "_vbftagged", hist_smooth_name + "_vbftagged", len(self.variableBinning) -1, array('d', self.variableBinning))

        # Rebin the histograms. Why?
        for i in range(0, len(self.variableBinning)):
            mVV_tmp = self.background_hists_smooth["{}{}_smooth".format(process, "")].GetBinCenter(i + 1)
            bin_width = self.background_hists_smooth["{}{}_smooth".format(process, "")].GetBinWidth(i + 1)

            for j in range(0, vzTemplateMVV.GetXaxis().GetNbins()):
                mVV_tmp_low = vzTemplateMVV.GetXaxis().GetBinLowEdge(j + 1)
                mVV_tmp_up = vzTemplateMVV.GetXaxis().GetBinUpEdge(j + 1)
                bin_width_tmp = vzTemplateMVV.GetXaxis().GetBinWidth(j + 1)

                if mVV_tmp >= mVV_tmp_low and mVV_tmp < mVV_tmp_up:
                    # Below the histogram is scaled by the ratio of the bin widths to factor out the different binning
                    self.background_hists_smooth["{}{}_smooth".format(process, "")].SetBinContent(i + 1, self.background_hists_From1DTemplate["{}{}_template".format(process, "")].GetBinContent(j + 1) * bin_width / bin_width_tmp)
                    self.background_hists_smooth["{}{}_smooth".format(process, "")].SetBinError(i + 1, self.background_hists_From1DTemplate["{}{}_template".format(process, "")].GetBinError(j + 1) * bin_width / bin_width_tmp)

                    self.background_hists_smooth["{}{}_smooth".format(process, "_untagged")].SetBinContent(i + 1, self.background_hists_From1DTemplate["{}{}_template".format(process, "_untagged")].GetBinContent(j + 1) * bin_width / bin_width_tmp)
                    self.background_hists_smooth["{}{}_smooth".format(process, "_untagged")].SetBinError(i + 1, self.background_hists_From1DTemplate["{}{}_template".format(process, "_untagged")].GetBinError(j + 1) * bin_width / bin_width_tmp)

                    self.background_hists_smooth["{}{}_smooth".format(process, "_btagged")].SetBinContent(i + 1, self.background_hists_From1DTemplate["{}{}_template".format(process, "_btagged")].GetBinContent(j + 1) * bin_width / bin_width_tmp)
                    self.background_hists_smooth["{}{}_smooth".format(process, "_btagged")].SetBinError(i + 1, self.background_hists_From1DTemplate["{}{}_template".format(process, "_btagged")].GetBinError(j + 1) * bin_width / bin_width_tmp)

                    self.background_hists_smooth["{}{}_smooth".format(process, "_vbftagged")].SetBinContent(i + 1, self.background_hists_From1DTemplate["{}{}_template".format(process, "_vbftagged")].GetBinContent(j + 1) * bin_width / bin_width_tmp)
                    self.background_hists_smooth["{}{}_smooth".format(process, "_vbftagged")].SetBinError(i + 1, self.background_hists_From1DTemplate["{}{}_template".format(process, "_vbftagged")].GetBinError(j + 1) * bin_width / bin_width_tmp)

                    break
                    #
                    # The break statement exits the inner loop once the corresponding bin in vzTemplateMVV is found
                    # and its values are copied to vz_smooth.
                    # This prevents further iterations of the inner loop, which is correct in this context
                    # as each bin of vz_smooth should correspond to only one bin in vzTemplateMVV.
                    #

        for key, hist in self.background_hists_smooth.items():
            logger.debug("Smoothed {} integral: {}".format(key, hist.Integral()))

    def setup_background_shapes(self):
        """Setup the background shapes from the templates."""
        TempFile_fs = ROOT.TFile("templates1D/Template1D_spin0_{}_{}.root".format(self.fs, self.year), "READ")
        if not TempFile_fs or TempFile_fs.IsZombie():
            raise FileNotFoundError("Could not open the template file for final state {}".format(self.fs))

        prefix = "hmass_{}SR".format(self.jetType)
        categories = {"untagged": "", "btagged": "btag", "vbftagged": "vbf"}

        for key, suffix in self.hist_suffixes.items():
            for category, cat_string in categories.items():
                hist_name = "{}{}_{}".format(prefix, cat_string, suffix)
                hist = TempFile_fs.Get(hist_name)
                hist.SetDirectory(ROOT.gROOT) # Detach histogram from file ref: https://root-forum.cern.ch/t/nonetype-feturned-from-function-that-returns-th1f/18287/2?u=ramkrishna

                logger.debug("Range of histogram {}: {} to {}".format(hist_name, hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax()))
                if not hist:
                    raise ValueError("Histogram {} not found in file".format(hist_name))
                self.background_hists_From1DTemplate[key + "_" + category + "_template"] = hist
                logger.debug("{} integral: {}".format(hist_name, hist.Integral()))

                # Add shape uncertainties
                if category == self.cat_tree and self.BinStatUnc:
                    # self.add_shape_uncertainties_to_workspace(key + "_" + category, hist, self.rooDataHist[hist_name])
                    self.add_shape_uncertainties_to_workspace(key + "_" + category, hist)

        self.rooHistPdfs = {}
        for key, hist in self.background_hists_From1DTemplate.items():
            hist_smooth = hist.Clone()
            # hist_smooth.Smooth(1000, "R")
            # hist_smooth.SmoothMarkov(1000)
            hist_smooth = smooth_histogram(hist)
            # hist_smooth_KDE = smooth_histogram_with_tkde(hist)

            logger.debug("Smoothed {} integral: {}".format(key, hist.Integral()))
            if self.SanityCheckPlot:
                save_histograms(hist, hist_smooth, "{}/figs/smooth/{}_{}_smoothed.png".format(self.outputDir, self.channel, key), "hist", "Smooth")
                # save_histograms_3(hist, hist_smooth, hist_smooth_KDE, "{}/figs/smooth/{}_{}_smoothed.png".format(self.outputDir, self.channel, key), "hist", "Smooth", "Smooth_KDE")

            self.rooVars["data_hist"] = ROOT.RooDataHist(
                "dh_{}".format(key),
                "DataHist for {}".format(key),
                ROOT.RooArgList(self.zz2l2q_mass),
                hist, # INFO: Use without smooth histogram here
                # hist_smooth, # INFO: Use smooth histogram here
            )

            self.rooHistPdfs["pdf_{}".format(key)] = ROOT.RooHistPdf(
                "pdf_{}".format(key),
                "PDF for {}".format(key),
                ROOT.RooArgSet(self.zz2l2q_mass),
                self.rooVars["data_hist"],
            )
            self.rooHistPdfs["pdf_{}".format(key)].graphVizTree("{}/figs/dotFiles/{}.dot".format(self.outputDir, "pdf_{}".format(key)))

            if self.SanityCheckPlot:
                logger.debug("Integral of hist: {:21}: {}".format(key, hist.Integral()))
                fullRangeBkgRate = (self.rooHistPdfs["pdf_{}".format(key)].createIntegral(
                        ROOT.RooArgSet(self.zz2l2q_mass),
                        ROOT.RooFit.Range("fullsignalrange"),
                    ).getVal())

                logger.debug(
                    "Integral of pdf : {:21}: {}".format(
                        self.rooHistPdfs["pdf_{}".format(key)].GetName(),
                        fullRangeBkgRate,
                    ))

        logger.debug(self.background_hists_From1DTemplate)

    def setup_signal_fractions(self, vbfRatioVBF):
        """Set the VBF fraction based on condition."""
        if self.FracVBF == -1:
            logger.info("FracVBF is set to be floating within [0, 1]")
            self.rooVars["frac_VBF"] = ROOT.RooRealVar("frac_VBF", "Fraction of VBF", vbfRatioVBF, 0.0, 1.0)
            self.rooVars["frac_ggH"] = ROOT.RooFormulaVar("frac_ggH", "(1-@0)", ROOT.RooArgList(self.rooVars["frac_VBF"]))
        else:
            logger.info("Using fixed FracVBF = {}".format(self.FracVBF))
            # Define fraction of events coming from ggH process
            self.rooVars["frac_VBF"] = ROOT.RooRealVar("frac_VBF", "Fraction of VBF", self.FracVBF, 0.0, 1.0)
            self.rooVars["frac_VBF"].setConstant(True)
            # Define fraction of events coming from ggH process
            self.rooVars["frac_ggH"] = ROOT.RooFormulaVar("frac_ggH", "(1-@0)", ROOT.RooArgList(self.rooVars["frac_VBF"]))
            self.rooVars["frac_ggH"].setConstant(True)

    def calculate_signal_rates_next(
        self, frac_VBF, frac_ggH, ggH_vbf_ratio, vbfRatioVBF, ggH_btag_ratio, VBF_btag_ratio
    ):
        # Define branching ratio for ZZ->2l2q (l=e,mu) process without tau decays in signal MC
        # This value is calculated as the product of:
        # - 2: number of either Z-boson can decay to leptons or quarks and its indistinguishable partner
        # - 0.69911: branching ratio of each Z boson to decay into 2 quarks (q)
        # - 0.033662: branching ratio of Z boson to decay into 2 electrons
        # - 0.033662: branching ratio of Z boson to decay into 2 muons
        # - 2: as the Z boson can decay to either electrons or muons
        # - 1000: scaling factor used to convert the cross-section in femtobarns (fb) to the appropriate units for the analysis
        self.rooVars["BR"] = ROOT.RooRealVar("BR", "Branching Ratio", 2 * 0.69911 * 2 * 0.033662 * 1000)

        # Prepare arguments lists for ggH and VBF signal rates
        self.rooVars["arglist_ggH"] = ROOT.RooArgList(self.rooVars["arglist_all_JES"])
        self.rooVars["arglist_ggH"].add(self.rooVars["LUMI"])
        self.rooVars["arglist_ggH"].add(self.rooVars["frac_ggH"])
        self.rooVars["arglist_ggH"].add(self.rooVars["BR"])

        self.rooVars["arglist_VBF"] = ROOT.RooArgList(self.rooVars["arglist_all_JES"])
        self.rooVars["arglist_VBF"].add(self.rooVars["LUMI"])
        self.rooVars["arglist_VBF"].add(self.rooVars["frac_VBF"])
        self.rooVars["arglist_VBF"].add(self.rooVars["BR"])

        self.rooVars["arglist_ggH_with_BTAG"] = ROOT.RooArgList(self.rooVars["arglist_all_JES_BTAG"])
        self.rooVars["arglist_ggH_with_BTAG"].add(self.rooVars["LUMI"])
        self.rooVars["arglist_ggH_with_BTAG"].add(self.rooVars["frac_ggH"])
        self.rooVars["arglist_ggH_with_BTAG"].add(self.rooVars["BR"])

        self.rooVars["arglist_VBF_with_BTAG"] = ROOT.RooArgList(self.rooVars["arglist_all_JES_BTAG"])
        self.rooVars["arglist_VBF_with_BTAG"].add(self.rooVars["LUMI"])
        self.rooVars["arglist_VBF_with_BTAG"].add(self.rooVars["frac_VBF"])
        self.rooVars["arglist_VBF_with_BTAG"].add(self.rooVars["BR"])

        logger.debug("channel: {}, cat: {}, jetType: {}".format(self.channel, self.cat, self.jetType))
        formula_ggH, formula_VBF = self.get_formulas(ggH_vbf_ratio, vbfRatioVBF, ggH_btag_ratio, VBF_btag_ratio)
        logger.debug("Formula ggH: {}".format(formula_ggH))
        logger.debug("Formula VBF: {}".format(formula_VBF))

        if self.cat == "b_tagged" or self.cat == "untagged":
            rfvSigRate_ggH = ROOT.RooFormulaVar("ggH_hzz_norm", formula_ggH, self.rooVars["arglist_ggH_with_BTAG"])
            rfvSigRate_VBF = ROOT.RooFormulaVar("qqH_hzz_norm", formula_VBF, self.rooVars["arglist_VBF_with_BTAG"])
        else:

            rfvSigRate_ggH = ROOT.RooFormulaVar("ggH_hzz_norm", formula_ggH, self.rooVars["arglist_ggH"])
            rfvSigRate_VBF = ROOT.RooFormulaVar("qqH_hzz_norm", formula_VBF, self.rooVars["arglist_VBF"])

        logger.debug("Signal Rate ggH: {}".format(rfvSigRate_ggH.getVal()))
        logger.debug("Signal Rate VBF: {}".format(rfvSigRate_VBF.getVal()))

        getattr(self.workspace, "import")(rfvSigRate_ggH, ROOT.RooFit.RecycleConflictNodes())
        getattr(self.workspace, "import")(rfvSigRate_VBF, ROOT.RooFit.RecycleConflictNodes())

    def get_formulas(self, vbfRatioGGH, vbfRatioVBF, btagRatioGGH, btagRatioVBF):
        """Get the formula strings based on category and jet type."""
        num_jes_sources = len(self.rooVars["arglist_all_JES"])
        cumulative_jes_effect = self.rooVars["cumulative_jes_effect"]
        cumulative_jes_effect_with_btag = self.rooVars["cumulative_jes_effect_with_btag"]
        logger.debug("Number of JES sources: {}".format(num_jes_sources))

        if self.cat == "vbf_tagged":
            formula_ggH = "(1+0.16*({}))*@{}*@{}*@{}".format(
                self.rooVars["cumulative_jes_effect"],
                num_jes_sources,
                num_jes_sources + 1,
                num_jes_sources + 2,
            )
            formula_VBF = "(1+0.12*({}))*@{}*@{}*@{}".format(
                self.rooVars["cumulative_jes_effect"],
                num_jes_sources,
                num_jes_sources + 1,
                num_jes_sources + 2,
            )
        elif self.jetType == "resolved" and self.cat == "b_tagged":
            formula_ggH = "(1+0.04*@0)*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioGGH),
                num_jes_sources,
                num_jes_sources + 1,
                num_jes_sources + 2,
            )
            formula_VBF = "(1+0.13*@0)*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioVBF),
                num_jes_sources,
                num_jes_sources + 1,
                num_jes_sources + 2,
            )
        elif self.jetType == "resolved" and self.cat == "untagged":
            formula_ggH = "(1-0.03*@0*{})*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioGGH),
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioGGH),
                num_jes_sources,
                num_jes_sources + 1,
                num_jes_sources + 2,
            )
            formula_VBF = "(1-0.11*@0*{})*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioVBF),
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioVBF),
                num_jes_sources,
                num_jes_sources + 1,
                num_jes_sources + 2,
            )
        elif self.jetType == "merged" and self.cat == "b_tagged":
            formula_ggH = "(1+0.08*@0)*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioGGH),
                num_jes_sources,
                num_jes_sources + 1,
                num_jes_sources + 2,
            )
            formula_VBF = "(1+0.07*@0)*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioVBF),
                num_jes_sources,
                num_jes_sources + 1,
                num_jes_sources + 2,
            )
        elif self.jetType == "merged" and self.cat == "untagged":
            formula_ggH = "(1-0.16*@0*{})*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioGGH),
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioGGH),
                num_jes_sources,
                num_jes_sources + 1,
                num_jes_sources + 2,
            )
            formula_VBF = "(1-0.2*@0*{})*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioVBF),
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioVBF),
                num_jes_sources,
                num_jes_sources + 1,
                num_jes_sources + 2,
            )
        else:
            raise ValueError("Category {} not recognized. So, can't get_formulas()".format(self.cat))

        return formula_ggH, formula_VBF

    def WriteDatacard(self, file, theInputs, nameWS, theRates, obsEvents, is2D):
        """Write the datacard with the given parameters."""
        numberSig = self.numberOfSigChan(theInputs)
        numberBg = self.numberOfBgChan(theInputs)

        file.write("imax 1\n")
        file.write("jmax {0}\n".format(numberSig + numberBg - 1))
        file.write("kmax *\n")

        file.write("------------\n")
        file.write("shapes * * {0} w:$PROCESS w:$PROCESS_$SYSTEMATIC \n".format(nameWS))
        file.write("------------\n")

        file.write("bin {0} \n".format(self.appendName))
        file.write("observation {0} \n".format(obsEvents))

        file.write("------------\n")
        file.write("## mass window [{0},{1}] \n".format(self.variableBinning[0], self.variableBinning[1]))
        file.write("bin ")

        channelList = ["ggH", "qqH", "vz", "ttbar", "zjets"]
        channelName1D = self.channelName2D
        channelName2D = self.channelName2D

        for chan in channelList:
            if theInputs[chan]:
                file.write("{0} ".format(self.appendName))
            else:
                if chan.startswith("ggH") and theInputs["all"]:
                    file.write("{0} ".format(self.appendName))
        file.write("\n")

        file.write("process ")

        i = 0
        if not (self.is2D == 1):
            for chan in channelList:
                if theInputs[chan]:
                    file.write("{0} ".format(channelName1D[i]))
                i += 1
        else:
            for chan in channelList:
                if theInputs[chan]:
                    file.write("{0} ".format(channelName2D[i]))
                    i += 1
                else:
                    if chan.startswith("ggH") and theInputs["all"]:
                        file.write("{0} ".format(channelName2D[i]))
                        i += 1

        file.write("\n")

        processLine = "process "

        for x in range(-numberSig + 1, 1):
            processLine += "{0} ".format(x)

        for y in range(1, numberBg + 1):
            processLine += "{0} ".format(y)

        file.write(processLine)
        file.write("\n")

        file.write("rate ")
        for chan in channelList:
            if theInputs[chan] or (chan.startswith("ggH") and theInputs["all"]):
                file.write("{0:.4f} ".format(theRates[chan]))
        file.write("\n")
        file.write("------------\n")

    def numberOfSigChan(self, inputs):
        """Count the number of signal channels."""
        counter = 0
        if inputs["ggH"]: counter += 1
        if inputs["qqH"]: counter += 1

        return counter

    def numberOfBgChan(self, inputs):
        """Count the number of background channels."""
        counter = 0
        if inputs["vz"]: counter += 1
        if inputs["zjets"]: counter += 1
        if inputs["ttbar"]: counter += 1

        return counter

    def compareOldNewBinnedHistogram(self):
        """Compare the smoothed histograms with the original histograms."""
        process = self.background_list
        categories = {"_untagged", "_btagged", "_vbftagged", ""}

        for proc in process:
            for cat in categories:
                hist = self.background_hists_From1DTemplate["{}{}_template".format(proc, cat)]
                hist_smooth = self.background_hists_smooth["{}{}_smooth".format(proc, cat)]
                save_histograms(hist, hist_smooth, "{}/figs/rebin/{}_{}{}_RebinComp.png".format(self.outputDir, self.channel, proc, cat), "hist", "hist_rebin")

    def create_shape_uncertainties(self, hist, process, threshold=5):
        """Create shape uncertainties for bins with entries below the threshold."""
        hist_up = hist.Clone(hist.GetName() + "_up")
        hist_down = hist.Clone(hist.GetName() + "_down")

        # # detatch from root file
        hist_up.SetDirectory(ROOT.gROOT)
        hist_down.SetDirectory(ROOT.gROOT)

        self.background_hists[process + "_template"] = hist
        for bin in range(4, hist.GetNbinsX() + 1): #FIXME: Remove hardcoded value
            # hist_up = hist.Clone(hist.GetName() + "_up")
            # hist_down = hist.Clone(hist.GetName() + "_down")

            # # # detatch from root file
            # hist_up.SetDirectory(ROOT.gROOT)
            # hist_down.SetDirectory(ROOT.gROOT)

            content = hist.GetBinContent(bin)
            error = hist.GetBinError(bin)

            if content < threshold:
                if content == 0 or content < 0:
                    hist.SetBinContent(bin, 0.000001)
                    hist_up.SetBinContent(bin, 0.000001 + ROOT.TMath.Sqrt(0.000001))
                    hist_down.SetBinContent(bin, 0.0)
                else:
                    hist_up.SetBinContent(bin, content + error)
                    hist_down.SetBinContent(bin, max(content - error, 0.0))
                break;
                # self.background_hists[process + "_template_Bin" + str(bin) + "_up"] = hist_up
                # self.background_hists[process + "_template_Bin" + str(bin) + "_down"] = hist_down
                # if self.SanityCheckPlot:
                #     save_histograms_3(hist, hist_up, hist_down, "{}/figs/shape_uncertainties/{}_{}_shape_uncertainties.png".format(self.outputDir, process, self.channel), "hist", "hist_up", "hist_dn")

        self.background_hists[process + "_template_up"] = hist_up
        self.background_hists[process + "_template_down"] = hist_down

        # compare 3 histograms
        if self.SanityCheckPlot:
            save_histograms_3(hist, hist_up, hist_down, "{}/figs/shape_uncertainties/{}_{}_shape_uncertainties.png".format(self.outputDir, process, self.channel), "hist", "hist_up", "hist_dn")

        return hist_up, hist_down

    def add_shape_uncertainties_to_workspace(self, process, hist):
        """Add shape uncertainties to the workspace."""
        hist_up, hist_down = self.create_shape_uncertainties(hist, process, threshold=5)

        # save hist_up and hist_down it in the simple new ROOT file
        # hist_up.SaveAs("hist_up_{}.root".format(process))
        # hist_down.SaveAs("hist_down_{}.root".format(process))

        TemplateName_up = "{process}_template_up".format(process=process)
        TemplateName_down = "{process}_template_down".format(process=process)

        # self.background_hists[process + "_template_up"] = hist_up
        # self.background_hists[process + "_template_down"] = hist_down

        # # print the min, max and number of bins in hist
        # print("hist min: ", hist.GetMinimum())
        # print("hist max: ", hist.GetMaximum())
        # print("hist bins: ", hist.GetNbinsX())
        # print("hist dimension: ", hist.GetDimension())

        rooDataHist_up = ROOT.RooDataHist(TemplateName_up, TemplateName_up, ROOT.RooArgList(self.zz2l2q_mass), hist_up)
        rooDataHist_down = ROOT.RooDataHist(TemplateName_down, TemplateName_down, ROOT.RooArgList(self.zz2l2q_mass), hist_down)

        # RooHistPdf::vz_untagged_PdfDown[ pdfObs=(zz2lJ_mass) ] = 0.000188115
        # RooHistPdf::bkg_vz_vz_untagged_PdfDown[ pdfObs=(zz2lJ_mass) ] = 0.000188115
        # self.channelName2D = self.channelName2D

        tmptag = process.split("_")[0]
        # wptag = "bkg_"+tmptag
        # pdfName_up = "{wptag}_{process}_PdfUp".format(wptag=wptag, process=process)
        # pdfName_down = "{wptag}_{process}_PdfDown".format(wptag=wptag, process=process)

        pdfName_up = "{process}Up".format( process=process)
        pdfName_down = "{process}Down".format( process=process)

        self.rooVars[pdfName_up] = ROOT.RooHistPdf(pdfName_up, pdfName_up, ROOT.RooArgSet(self.zz2l2q_mass), rooDataHist_up)
        self.rooVars[pdfName_down] = ROOT.RooHistPdf(pdfName_down, pdfName_down, ROOT.RooArgSet(self.zz2l2q_mass), rooDataHist_down)

        # getattr(self.workspace, "import")(self.rooVars[pdfName_up], ROOT.RooFit.RecycleConflictNodes())
        # getattr(self.workspace, "import")(self.rooVars[pdfName_down], ROOT.RooFit.RecycleConflictNodes())

        # Add these uncertainties to the datacard as shape uncertainties
        self.add_shape_uncertainties_to_datacard(process, pdfName_up, pdfName_down)

    def add_shape_uncertainties_to_datacard(self, process, pdfName_up, pdfName_down):
        """Add shape uncertainties to the datacard."""
        # Determine the position of the process in the channelName2D list
        shape_line_up = "{process} shape".format(process=pdfName_up.replace("Up",""))
        shape_line_down = "{process} shape".format(process=pdfName_down.replace("Down",""))

        # logger.error(("shape_line_up: ", shape_line_up))
        # logger.error(("shape_line_down: ", shape_line_down))

        for channel in self.channelName2D:
            if channel.endswith(process.split("_")[0]):
                shape_line_up += " 1"
                shape_line_down += " 1"
            else:
                shape_line_up += " -"
                shape_line_down += " -"

        shape_line_up += "\n"
        shape_line_down += "\n"

        self.datacard_lines.append(shape_line_up)
        # self.datacard_lines.append(shape_line_down)

    def makeCardsWorkspaces(self, theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, BinStatUnc = True, SanityCheckPlot=True):
        """Main function to create the datacards and workspaces."""
        self.clearRooArgSets()
        self.initialize_settings(theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, BinStatUnc, SanityCheckPlot)
        self.initialize_workspace_and_observables(theMH, theInputs)
        TString_sig = "sig_resolved"
        if self.channel in ["mumuqq_Merged", "eeqq_Merged"]:
            TString_sig = "sig_merged"

        ## ------------------------- SYSTEMATICS CLASSES ----------------------------- ##
        systematics = systematicsClass(self.mH, True, theInputs, self.year, self.DEBUG)

        ## ------------------------- RATES: Signal ----------------------------- ##
        sigRate_ggH_Shape, vbf_ratioGGH, btag_ratioGGH = self.getSignalRates("ggH")
        sigRate_VBF_Shape, vbf_ratioVBF, btag_ratioVBF = self.getSignalRates("VBF")

        # ================== SIGNAL SHAPE ================== #
        SignalShapeFile = "Resolution/2l2q_resolution_{0}_{1}.root".format(self.jetType, self.year) # INFO: Hardcoded path and filename
        SignalShape = self.open_root_file(SignalShapeFile)

        self.get_signal_shape_mean_error(SignalShape)
        self.setup_signal_shape(SignalShape, systematics, "VBF", self.channel)
        self.setup_signal_shape(SignalShape, systematics, "ggH", self.channel)

        # Opening template ROOT files
        templateSigName = "templates2D/2l2q_spin0_template_{}.root".format(self.year) # FIXME: hardcoded path
        logger.debug("Using templateSigName: {}".format(templateSigName))
        sigTempFile = self.open_root_file(templateSigName)

        # Setup discriminant variable
        sigTemplate = sigTempFile.Get(TString_sig)
        dBins = sigTemplate.GetYaxis().GetNbins()
        dLow = sigTemplate.GetYaxis().GetXmin()
        dHigh = sigTemplate.GetYaxis().GetXmax()
        self.rooVars["D"] = ROOT.RooRealVar("Dspin0", "Discriminant Variable (Dspin0)", dLow, dHigh)
        self.rooVars["D"].setBins(dBins)
        logger.debug("Discriminant variable setup with bins: {}, range: [{}, {}]".format(dBins, dLow, dHigh))
        sigTempFile.Close()

        ## ------------------------- RATES: Background ----------------------------- ##
        self.setup_background_shapes_ReproduceRate_fs()
        self.setup_background_shapes_ReproduceRate_2l()
        self.setup_background_shapes_ReproduceRate("vz")
        self.setup_background_shapes_ReproduceRate("ttbar")
        self.setup_background_shapes_ReproduceRate("zjets")

        if self.SanityCheckPlot:
            self.compareOldNewBinnedHistogram()

        self.setup_background_shapes()

        # FIXME: This rate is not used in the legacy code. But, we should switch to this for rate calculation
        # bkgRate_vz_Shape = self.calculate_background_rates("vz")
        # bkgRate_ttbar_Shape = self.calculate_background_rates("ttbar")
        # bkgRate_zjets_Shape = self.calculate_background_rates("zjets")

        # obtain rate using the new histogram based on the number of bins and range used in self.bins and self.low_M, self.high_M
        # this is obtained from the 1D histograms present in the templates1D directory
        bkgRate_vz_Shape = self.getRateFromSmoothedHist("vz")
        bkgRate_ttbar_Shape = self.getRateFromSmoothedHist("ttbar")
        bkgRate_zjets_Shape = self.getRateFromSmoothedHist("zjets")

        logger.debug("Signal rates: ggH: {:.4f}, qqH: {:.4f}".format(sigRate_ggH_Shape, sigRate_VBF_Shape))
        logger.debug("Background rates: VZ: {:.4f}, TTbar: {:.4f}, Zjets: {:.4f}\n\n".format(bkgRate_vz_Shape, bkgRate_ttbar_Shape, bkgRate_zjets_Shape))

        ## --------------------------- DATACARDS -------------------------- ##
        rates = {}
        rates["ggH"] = sigRate_ggH_Shape
        rates["qqH"] = sigRate_VBF_Shape

        rates["vz"] = bkgRate_vz_Shape
        rates["ttbar"] = bkgRate_ttbar_Shape
        rates["zjets"] = bkgRate_zjets_Shape

        ## ------------------------- MELA 2D ----------------------------- ##
        self.getRooProdPDFofMorphedSignal(TString_sig, templateSigName)
        self.setup_nuisances(systematics) # needed for  module "calculate_signal_rates_next"
        self.setup_signal_fractions(vbf_ratioVBF)
        self.calculate_signal_rates_next(
            self.rooVars["frac_VBF"],
            self.rooVars["frac_ggH"],
            vbf_ratioGGH,
            vbf_ratioVBF,
            btag_ratioGGH,
            btag_ratioVBF,
        )
        logger.debug("jetType: {}, cat: {}".format(self.jetType, self.cat))

        ## ------------------------- Backgrounds 2D: Write to workspace ----------------------------- ##
        morphBkgVarName = "CMS_zz2l2q_bkgMELA_{}".format(self.jetType)
        self.rooVars[morphBkgVarName] = ROOT.RooRealVar(morphBkgVarName, morphBkgVarName, 0, -2, 2)
        self.rooVars[morphBkgVarName].setConstant(False)
        self.rooArgSets["morphVarListBkg"] = ROOT.RooArgList(self.rooVars[morphBkgVarName])

        self.get_Backgrounds_funcList()
        self.getRooProdPDFofMorphedBackgrounds()
        self.calculate_background_rates_vz()

        ## ------------------------- DATA ----------------------------- ##
        self.rooDataSet["data_obs"] = self.getData()
        getattr(self.workspace, "import")(self.rooDataSet["data_obs"], ROOT.RooFit.Rename("data_obs"))

        ## ------------------------- Name of datacard and workspace files ----------------------------- ##
        name_ShapeWS = ""
        name_ShapeWS2 = ""
        name_ShapeWS = "{0}/HCG/{1:.0f}/hzz2l2q_{2}_{3:.0f}TeV.input.root".format(self.outputDir, self.mH, self.appendName, self.sqrts)
        name_ShapeWS2 = "hzz2l2q_{0}_{1:.0f}TeV.input.root".format(self.appendName, self.sqrts)
        self.workspace.writeToFile(name_ShapeWS)

        ## Write Datacards
        systematics.setSystematics(rates)
        name_Shape = "{0}/HCG/{1:.0f}/hzz2l2q_{2}_{3:.0f}TeV.txt".format(self.outputDir, self.mH, self.appendName, self.sqrts)
        fo = open(name_Shape, "w")
        self.WriteDatacard(fo, theInputs, name_ShapeWS2, rates, self.rooDataSet["data_obs"].numEntries(), self.is2D)
        systematics.WriteSystematics(fo, theInputs, rates, 0.0) # INFO: Why is the last argument 0.0?
        systematics.WriteShapeSystematics(fo, theInputs)

        for line in self.datacard_lines:
            fo.write(line)

        fo.close()
        logger.debug("appendName is channel + cat: {}".format(self.appendName))

        # ## ------------------------- Save the model using graphVizTree ----------------------------- ##
        # model_file_path = "{0}/HCG/{1:.0f}/model_{2}_{3:.0f}TeV.dot".format(self.outputDir, self.mH, self.appendName, self.sqrts)
        # visualize_workspace(self.workspace, model_file_path)

        ## ------------------------- Print ajjjll RooArgSets ----------------------------- ##
        # self.printAllRooArgSets()
        if self.DEBUG:
            self.workspace.Print("v")
            logger.error("Exiting the program for DEBUG mode")
            # exit()
        # exit()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create datacards and workspaces.")
    parser.add_argument("--year", type=int, required=True, help="Year of the data")
    parser.add_argument("--channel", type=str, required=True, help="Channel ID")
    parser.add_argument("--cat", type=str, required=True, help="Category ID")
    parser.add_argument(
        "--jetType", type=str, required=True, help="Jet type (resolved or merged)"
    )
    parser.add_argument(
        "--mH", type=float, required=True, help="Mass of the Higgs boson"
    )
    parser.add_argument("--is2D", type=int, default=1, help="Is it a 2D analysis?")
    parser.add_argument(
        "--outputDir", type=str, required=True, help="Output directory for the files"
    )
    parser.add_argument("--fracVBF", type=float, default=-1, help="Fraction of VBF")
    parser.add_argument(
        "--sanityCheck", type=bool, default=True, help="Enable sanity check plots"
    )
    parser.add_argument("--debug", type=bool, default=False, help="Enable debug mode")

    parser.add_argument("--BinStatUnc", type=bool, default=False, help="Enable statistical uncertainty")

    args = parser.parse_args()

    inputs = {
        "all": True,
        "ggH": True,
        "qqH": True,
        "vz": True,
        "zjets": True,
        "ttbar": True,
        "decayChannel": args.channel,
        "lumi": 1.0,
        "sqrts": 13,
        "alphaS": 0.118,
        "cat": args.cat,
        "model": "SM",
        "lumiUnc": 0.027,
        "muonTrigUnc": 0.02,
        "muonFullUnc": 0.02,
        "elecTrigUnc": 0.02,
        "elecFullUnc": 0.02,
        "zjetsAlphaLow": 0.0,
        "zjetsAlphaHigh": 0.0,
        "gghJESLow": 0.0,
        "gghJESHigh": 0.0,
    }

    datacard = DatacardClass(args.year, args.debug)
    datacard.channel = args.channel
    datacard.cat = args.cat
    datacard.jetType = args.jetType
    datacard.makeCardsWorkspaces(
        args.mH,
        args.is2D,
        args.outputDir,
        inputs,
        args.cat,
        args.fracVBF,
        args.sanityCheck,
    )
