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
        self.rooArgSets["funcList_zjets"] = ROOT.RooArgList()

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
        self.binning_resolved = uniform_bins
        self.rooBinning_resolved = ROOT.RooBinning(len(self.binning_resolved) - 1, array('d', self.binning_resolved))

        # Merged bin edges
        temp_bin1_merged = np.linspace(self.low_M, 900, 16)
        temp_bin2_merged = np.array([1000, 1200, 1600, self.high_M])
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

        arglist_all_JES = ROOT.RooArgList()
        for nuisance in all_nuisances:
            arglist_all_JES.add(nuisance)

        BTAG = ROOT.RooRealVar("BTAG_" + self.jetType, "BTAG_" + self.jetType, 0, -2, 2)
        self.rooVars["BTAG_" + self.jetType] = BTAG

        arglist_all_JES_BTAG = ROOT.RooArgList()
        for nuisance in all_nuisances:
            arglist_all_JES_BTAG.add(nuisance)

        cumulative_jes_effect = "+".join(
            "@{}".format(i) for i in range(len(arglist_all_JES))
        )
        cumulative_jes_effect_with_btag = "+".join(
            "@{}".format(i) for i in range(len(arglist_all_JES))
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
        self.setup_workspace()
        self.set_append_name()
        self.set_category_tree()
        self.set_channels(theInputs)
        self.set_jet_type()
        self.theInputs = theInputs
        self.variableBinning = self.binning_resolved if self.jetType == "resolved" else self.binning_merged

        logger.error("channel: {}, cat: {}, jetType: {}".format(self.channel, self.cat, self.jetType))

        self.setup_observables()

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
        dataFileName = "CMSdata/Data_SR.root"  # FIXME: Hardcoded
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

        tmpFile = ROOT.TFile("tmpFile.root", "RECREATE")
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

        logger.debug("data_obs: {}".format(self.rooDataSet["data_obs"]))
        return self.rooDataSet["data_obs"]

    def getRooProdPDFofMorphedSignal(self, TString_sig, templateSigName):
        """Get the RooProdPDF of the morphed signal."""
        logger.debug("Inside getRooProdPDFofMorphedSignal")

        self.rooVars["funcList_ggH"] = ROOT.RooArgList()
        self.rooVars["funcList_VBF"] = ROOT.RooArgList()

        sigTempFile = self.open_root_file(templateSigName)
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

        for sample in ["ggH", "VBF"]:
            for tag in ["", "_up", "_dn"]:
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

        morphSigVarName = "CMS_zz2l2q_sigMELA_" + self.jetType
        self.rooVars[morphSigVarName] = ROOT.RooRealVar(morphSigVarName, morphSigVarName, 0, -2, 2)
        if self.sigMorph:
            self.rooVars[morphSigVarName].setConstant(False)
        else:
            self.rooVars[morphSigVarName].setConstant(True)

        self.rooVars["morphVarListSig_" + self.jetType] = ROOT.RooArgList()
        if self.sigMorph:
            self.rooVars["morphVarListSig_" + self.jetType].add(self.rooVars[morphSigVarName])

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
                    ROOT.RooArgSet(self.rooVars[pdfName]),
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
            logger.debug("vzTemplateName: {}, \n\tvzTemplateMVV: {}".format(vzTemplateName, vzTemplateMVV))
            logger.debug("TYPE: {}".format(type(vzTemplateMVV)))

            TString_bkg = "{}_resolved".format(self.background_map_2DTemplates[process])
            if self.channel in ["mumuqq_Merged", "eeqq_Merged"]:
                TString_bkg = "{}_merged".format(self.background_map_2DTemplates[process])

            funcList = self.rooArgSets["funcList_{}".format(process)]
            morphVarName = "CMS_zz2l2q_bkgMELA_" + self.jetType
            logger.debug("morphVarName: {}".format(morphVarName))

            self.rooVars[morphVarName] = ROOT.RooRealVar(morphVarName, morphVarName, 0, -2, 2)
            if self.bkgMorph:
                self.rooVars[morphVarName].setConstant(False)
            else:
                self.rooVars[morphVarName].setConstant(True)

            self.rooVars["morphVarListBkg_" + self.jetType] = ROOT.RooArgList()
            if self.bkgMorph:
                self.rooVars["morphVarListBkg_" + self.jetType].add(self.rooVars[morphVarName])

            morphVarNamePdf = "{}_MorphPdf".format(vzTemplateName)
            self.rooVars[morphVarNamePdf] = ROOT.FastVerticalInterpHistPdf2D(
                morphVarNamePdf,
                morphVarNamePdf,
                self.zz2l2q_mass,
                self.rooVars["D"],
                True,
                funcList,
                self.rooVars["morphVarListBkg_" + self.jetType],
                1.0,
                1,
            )

            self.rooVars[morphVarNamePdf].graphVizTree("{}/figs/dotFiles/{}.dot".format(self.outputDir, morphVarNamePdf))
            logger.debug("Finished setting morphVarNamePdf: {}".format(morphVarNamePdf))

            bkg_vz_morphPdfName = "bkg_vz_{}_{}".format(process, self.year)
            self.rooProdPdf[bkg_vz_morphPdfName] = ROOT.RooProdPdf(
                bkg_vz_morphPdfName,
                bkg_vz_morphPdfName,
                ROOT.RooArgSet(self.rooVars[morphVarNamePdf]),
                ROOT.RooFit.Conditional(
                    ROOT.RooArgSet(self.rooVars["pdf_" + process + "_" + str(self.year)]),
                    ROOT.RooArgSet(self.zz2l2q_mass, self.rooVars["D"]),
                ),
            )

            if process == "zjets":
                self.rooProdPdf[bkg_vz_morphPdfName].SetNameTitle("bkg_zjets", "bkg_zjets")
            elif process == "ttbar":
                self.rooProdPdf[bkg_vz_morphPdfName].SetNameTitle("bkg_ttbar", "bkg_ttbar")
            elif process == "vz":
                self.rooProdPdf[bkg_vz_morphPdfName].SetNameTitle("bkg_vz", "bkg_vz")

            getattr(self.workspace, "import")(self.rooProdPdf[bkg_vz_morphPdfName], ROOT.RooFit.RecycleConflictNodes())
            logger.debug("added to workspace: {}".format(bkg_vz_morphPdfName))

    def general_setup_background_shapes(self, process, TString_bkg):
        """General method for setting up background shapes."""
        logger.debug(f"Setting up background shapes for process: {process}")
        if f"funcList_{process}" not in self.rooArgSets:
            self.rooArgSets[f"funcList_{process}"] = ROOT.RooArgList()

        variations = ["", "_Up", "_Down"]
        for variation in variations:
            logger.debug(f"variation: {variation}")
            if not self.bkgMorph and variation != "":
                logger.error(f"Skipping variation: {variation}")
                continue

            variations_tag_for_hist = "_up" if variation == "_Up" else "_dn" if variation == "_Down" else ""
            logger.debug(f"variations: {variation}, variations_tag_for_hist: {variations_tag_for_hist}")
            logger.debug(f"Looking for hist: {TString_bkg + variations_tag_for_hist}")

            bkgsTemplate = self.bkg2DTemplateFile.Get(TString_bkg + variations_tag_for_hist)
            if not bkgsTemplate:
                logger.debug(f"Failed to get {process} template: {TString_bkg + variations_tag_for_hist}")
                continue

            logger.debug(f"bkgsTemplate: Name: {bkgsTemplate.GetName()} Title: {bkgsTemplate.GetTitle()} NbinsX: {bkgsTemplate.GetNbinsX()}")

            TemplateName = f"{process}TempDataHist_{TString_bkg}{variation}_{self.year}"
            self.rooDataHist[TemplateName] = ROOT.RooDataHist(
                TemplateName,
                TemplateName,
                ROOT.RooArgList(self.zz2l2q_mass, self.rooVars["D"]),
                bkgsTemplate,
            )

            PdfName = f"{process}TemplatePdf_{TString_bkg}{variation}_{self.year}"
            self.rooDataHist[PdfName] = ROOT.RooHistPdf(
                PdfName,
                PdfName,
                ROOT.RooArgSet(self.zz2l2q_mass, self.rooVars["D"]),
                self.rooDataHist[TemplateName],
            )
            self.rooDataHist[PdfName].graphVizTree(f"{self.outputDir}/figs/dotFiles/{PdfName}.dot")

            self.rooArgSets[f"funcList_{process}"].add(self.rooDataHist[PdfName])

        for i in range(self.rooArgSets[f"funcList_{process}"].getSize()):
            logger.debug(f"{i:2}: funcList_{process}: {self.rooArgSets[f"funcList_{process}"].at(i).GetName()}")

    def setup_background_shapes_ReproduceRate_fs(self):
        """Setup background shapes for ReproduceRate_fs."""
        TString_bkg = "{}_{}_{}".format("ReproduceRate_fs", self.appendName, self.year)
        self.general_setup_background_shapes("ReproduceRate_fs", TString_bkg)

    def setup_background_shapes_ReproduceRate_2l(self):
        """Setup background shapes for ReproduceRate_2l."""
        TString_bkg = "{}_{}_{}".format("ReproduceRate_2l", self.appendName, self.year)
        self.general_setup_background_shapes("ReproduceRate_2l", TString_bkg)

    def setup_background_shapes_ReproduceRate(self):
        """Setup background shapes for ReproduceRate."""
        TString_bkg = "{}_{}_{}".format("ReproduceRate", self.appendName, self.year)
        self.general_setup_background_shapes("ReproduceRate", TString_bkg)

    def do_background_morphing(self):
        """Perform background morphing."""
        logger.debug("Inside do_background_morphing")

        self.setup_background_shapes_ReproduceRate_fs()
        self.setup_background_shapes_ReproduceRate_2l()
        self.setup_background_shapes_ReproduceRate()

        for bkg in self.background_list:
            self.getRooProdPDFofMorphedBackgrounds()

    def save_workspace(self):
        """Save the workspace to a ROOT file."""
        workspace_output_path = f"{self.outputDir}/workspace_{self.appendName}_{self.year}.root"
        self.workspace.writeToFile(workspace_output_path)
        logger.debug(f"Workspace saved to: {workspace_output_path}")

    def run(self, theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, BinStatUnc, SanityCheckPlot):
        """Run the datacard preparation."""
        self.initialize_settings(theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, BinStatUnc, SanityCheckPlot)
        self.initialize_workspace_and_observables(theMH, theInputs)
        self.getData()
        self.get_Backgrounds_funcList()
        self.getRooProdPDFofMorphedSignal("someTString", "someTemplateSigName")
        self.do_background_morphing()
        self.save_workspace()
