#!/usr/bin/env python
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kInfo
import sys
from decimal import *
from subprocess import *
from array import array

from inputReader import *
from systematicsClass import *
from utils import *
from utils_hist import plot_and_save, save_histograms

ROOT.gROOT.ProcessLine("struct zz2lJ_massStruct {" "   Double_t zz2lJ_mass;" "};")

from ROOT import zz2lJ_massStruct


class datacardClass:

    def __init__(self, year, DEBUG=False):
        self.year = year
        self.DEBUG = DEBUG
        self.loadIncludes()
        self.setup_parameters()
        #  To extend the lifecycle of all RooFit objects by storing them as attributes of self
        self.rooVars = {}
        self.rooDataSet = {}
        self.background_hists = {}
        self.workspace = ROOT.RooWorkspace("w", "workspace")
        self.sigFraction = 1.0 # Fraction of signal to be used

    def setup_parameters(self):
        self.low_M = 0
        self.high_M = 4000
        self.bins = int((self.high_M - self.low_M) / 10)
        self.ID_2muResolved = "mumuqq_Resolved"
        self.ID_2eResolved = "eeqq_Resolved"
        self.ID_2muMerged = "mumuqq_Merged"
        self.ID_2eMerged = "eeqq_Merged"

    def loadIncludes(self):
        ROOT.gSystem.AddIncludePath("-I$ROOFITSYS/include/")
        ROOT.gSystem.AddIncludePath("-Iinclude/")
        ROOT.gROOT.ProcessLine(".L include/tdrstyle.cc")
        ROOT.gSystem.Load("libRooFit")
        ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so")

    def open_root_file(self, file_path):
        file = ROOT.TFile.Open(file_path, "READ")
        if not file or file.IsZombie():
            logger.error("Failed to open file: {}".format(file_path))
            raise FileNotFoundError("Could not open file: {}".format(file_path))
        logger.debug("Successfully opened file: {}".format(file_path))
        return file

    def setup_workspace(self):
        self.workspace.importClassCode(ROOT.RooDoubleCB.Class(), True)
        self.workspace.importClassCode(ROOT.RooFormulaVar.Class(), True)

    def set_jet_type(self):
        self.jetType = "resolved"
        if "merged" in (self.channel).lower():
            self.jetType = "merged"

    def setup_observables(self):
        logger.info("Setting up observables")
        self.mzz_name = "zz2l2q_mass"
        self.zz2l2q_mass = ROOT.RooRealVar(
            self.mzz_name, self.mzz_name, self.low_M, self.high_M
        )
        self.zz2l2q_mass.setBins(self.bins)

        if self.jetType == "merged":
            self.zz2l2q_mass.SetName("zz2lJ_mass")
            self.zz2l2q_mass.SetTitle("zz2lJ_mass")

        self.zz2l2q_mass.setRange("fullrange", self.low_M, self.high_M)
        self.zz2l2q_mass.setRange(
            "fullsignalrange", self.mH - 0.25 * self.mH, self.mH + 0.25 * self.mH
        )
        self.rooVars["zz2l2q_mass"] = self.zz2l2q_mass
        logger.info("Observables are set up successfully")

    def set_append_name(self):
        self.fs = "2e"
        if self.channel == self.ID_2muResolved:
            self.fs = "2mu"
        if self.channel == self.ID_2muMerged:
            self.fs = "2mu"
        postfix = self.channel + "_" + self.cat
        self.appendName = postfix
        logger.debug("appendName is channel + cat: {}".format(postfix))

    def set_category_tree(self):
        self.cat_tree = "untagged"
        if self.cat == "b_tagged":
            self.cat_tree = "btagged"
        if self.cat == "vbf_tagged":
            self.cat_tree = "vbftagged"

    def set_channels(self, inputs):
        self.all_chan = inputs["all"]
        self.ggH_chan = inputs["ggH"]
        self.qqH_chan = inputs["qqH"]
        self.vz_chan = inputs["vz"]
        self.zjets_chan = inputs["zjets"]
        self.ttbar_chan = inputs["ttbar"]

    def initialize_settings(
        self,
        theMH,
        theis2D,
        theOutputDir,
        theInputs,
        theCat,
        theFracVBF,
        SanityCheckPlot,
    ):
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
        self.SanityCheckPlot = SanityCheckPlot
        logger.debug("Settings initialized for channel: {}".format(self.channel))

    def makeCardsWorkspaces(self, theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, SanityCheckPlot=True):
        self.initialize_settings(theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, SanityCheckPlot)
        self.setup_workspace()  # Setup the RooWorkspace
        self.set_append_name()  # Set the finalState (fs) and postfix variable
        self.set_category_tree()  # Set the category tree: cat_tree and cat
        self.set_channels(theInputs) # Set the channels: ggH, qqH, vz, zjets, ttbar
        self.set_jet_type() # Set the jet type: resolved or merged
        self.theInputs = theInputs # Set the inputs coming from txt file

        ## ------------------------- OBSERVABLES ----------------------------- ##
        self.setup_observables()
        self.rooVars["LUMI"] = ROOT.RooRealVar("LUMI_{0:.0f}_{1}".format(self.sqrts, self.year), "Integrated Luminosity", self.lumi)
        self.rooVars["LUMI"].setConstant(True)

        self.rooVars["MH"] = ROOT.RooRealVar("MH", "MH", self.mH)
        self.rooVars["MH"].setConstant(True)

        ## ---------------- SET PLOTTING STYLE ---------------- ##
        ROOT.setTDRStyle(True)
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetPadLeftMargin(0.16)

        ## ------------------------- SYSTEMATICS CLASSES ----------------------------- ##
        systematics = systematicsClass(self.mH, True, theInputs, self.year, self.DEBUG)  # the second argument is for the systematic unc. coming from XSxBR

        ## ------------------------- RATES ----------------------------- ##
        sigRate_ggH_Shape, vbf_ratio, btag_ratio = self.getRates("ggH")
        sigRate_VBF_Shape, vbf_ratio, btag_ratio = self.getRates("VBF")

        ## --------------------------- DATACARDS -------------------------- ##

        rates = {}
        rates["ggH"] = sigRate_ggH_Shape
        rates["qqH"] = sigRate_VBF_Shape

        rates["vz"] = 0.0 # bkgRate_vz_Shape
        rates["ttbar"] = 0.0 # bkgRate_ttbar_Shape
        rates["zjets"] = 0.0 # bkgRate_zjets_Shape

        name_ShapeWS2 = ""
        name_ShapeWS2 = "hzz2l2q_{0}_{1:.0f}TeV.input.root".format(self.appendName, self.sqrts)

        ## ------------------------- DATA ----------------------------- ##
        self.rooDataSet["data_obs"] = self.getData()
        logger.debug("Data: {}".format(self.rooDataSet["data_obs"].Print("v")))

        ## Write Datacards
        systematics.setSystematics(rates)

        name_Shape = "{0}/HCG/{1:.0f}/hzz2l2q_{2}_{3:.0f}TeV.txt".format(self.outputDir, self.mH, self.appendName, self.sqrts)
        fo = open(name_Shape, "wb")
        self.WriteDatacard(
            fo,
            theInputs,
            name_ShapeWS2,
            rates,
            self.rooDataSet["data_obs"].numEntries(),
            self.is2D,
        )

        # FIXME: This is a temporary fix to write the systematics to the datacard
        # FIXME: Why we are just using the ttbar_MuEG_file for systematics?
        #  Also, this part is not used by the systematicClass.py to write the systematics
        # ttbar_MuEG_file = ROOT.TFile("CMSdata/alphaMethod_MuEG_Data_2016.root")
        # channel_plus_cat = "resolvedSR"
        # if self.channel == "eeqq_Resolved" or self.channel == "mumuqq_Resolved":
        #     channel_plus_cat = "resolvedSR"
        # if self.channel == "eeqq_Merged" or self.channel == "mumuqq_Merged":
        #     channel_plus_cat = "mergedSR"
        # if self.cat == "b_tagged":
        #     channel_plus_cat = channel_plus_cat + "btag"
        # elif self.cat == "vbf_tagged":
        #     channel_plus_cat = channel_plus_cat + "vbf"
        # ttbar_MuEG_data = ttbar_MuEG_file.Get("hmass_" + channel_plus_cat + "_Data_emu_Bin50GeV")

        # systematics.WriteSystematics(fo, theInputs, rates, int(ttbar_MuEG_data.Integral("width") / 50))
        systematics.WriteSystematics(fo, theInputs, rates, 0.0)
        systematics.WriteShapeSystematics(fo, theInputs)

        fo.close()
        logger.debug("appendName is channel + cat: {}".format(self.appendName))

    def get_tree_name(self):
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
        dataFileDir = "CMSdata"
        dataFileName = "{}/Data_SR.root".format(dataFileDir)
        logger.debug("dataFileName: {}".format(dataFileName))

        # Open ROOT file
        data_obs_file = ROOT.TFile(dataFileName)
        if data_obs_file.IsZombie() or not data_obs_file.IsOpen():
            logger.error(
                "Failed to open file: {}. Existing the program".format(dataFileName)
            )
            sys.exit(1)

        # Define tree names based on channel and category
        treeName = self.get_tree_name()
        logger.debug("treeName: {}".format(treeName))
        tree = data_obs_file.Get(treeName)
        if not tree:
            logger.error('File "{}", or tree "{}", not found'.format(dataFileName, treeName))
            logger.error("Exiting...")
            sys.exit(1)
        else:
            logger.debug('File "{}", tree "{}" found'.format(dataFileName, treeName))

        # Clone tree and create new branch
        tmpFile = ROOT.TFile("tmpFile.root", "RECREATE")  # This is a temporary fix. We don't need tempFile.root. But if its not there then it gives error
        data_obs_tree = tree.CloneTree(0)
        logger.debug("data_obs_tree: {}".format(data_obs_tree))

        zz2lJ_mass_struct = zz2lJ_massStruct()
        data_obs_tree.Branch("zz2lJ_mass", zz2lJ_mass_struct, "zz2lJ_mass/D")
        logger.debug("zz2lJ_mass_struct: {}".format(zz2lJ_mass_struct))

        # Fill tree with adjusted mass values
        for i in xrange(tree.GetEntries()):  # Use xrange for Python 2
            tree.GetEntry(i)
            # zz2lJ_mass_struct.zz2lJ_mass = getattr(tree, "zz2l2q_mass")
            zz2lJ_mass_struct.zz2lJ_mass = data_obs_file.Get(treeName).zz2l2q_mass
            data_obs_tree.Fill()

        # Log entries and create RooDataSet
        logger.info("Data entries: {}".format(tree.GetEntries()))

        datasetName = "data_obs"
        self.rooDataSet["data_obs"] = ROOT.RooDataSet(datasetName, datasetName, data_obs_tree, ROOT.RooArgSet(self.zz2l2q_mass))

        logger.debug("data_obs: {}".format(self.rooDataSet["data_obs"]))
        return self.rooDataSet["data_obs"]

    def getRates(self, signal_type):
        logger.debug("Calculating signal rates for {}".format(signal_type))

        # Open the ROOT file for the given signal type
        file_path = "SigEff/2l2q_Efficiency_spin0_{}_{}.root".format(signal_type, self.year)
        accxeff_file = ROOT.TFile(file_path)
        logger.debug("Opened file: {}".format(file_path))

        # Extract acceptance x efficiency for various tagging categories
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

        # Calculate ratios
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

        # Retrieve the specific signal rate for this category and signal type
        formatted_name = self.appendName.replace("b_tagged", "b-tagged").replace(
            "vbf_tagged", "vbf-tagged"
        )
        sig_rate_shape = (
            accxeff_file.Get("spin0_{}_{}".format(signal_type, formatted_name))
            .GetListOfFunctions()
            .First()
            .Eval(self.mH)
        )

        # Adjust rate by the given fraction (sigFraction)
        sig_rate_shape *= self.sigFraction

        # Ensure non-negative rates
        sig_rate_shape = max(sig_rate_shape, 0.0)
        logger.debug("{} Signal rate: {}".format(signal_type, sig_rate_shape))

        # Close the ROOT file
        accxeff_file.Close()
        return sig_rate_shape, vbf_ratio, btag_ratio

    def WriteDatacard(self, file, theInputs, nameWS, theRates, obsEvents, is2D):

        numberSig = self.numberOfSigChan(theInputs)
        numberBg = self.numberOfBgChan(theInputs)

        file.write("imax 1\n")
        file.write("jmax {0}\n".format(numberSig + numberBg - 1))
        file.write("kmax *\n")

        file.write("------------\n")
        file.write("shapes * * {0} w:$PROCESS \n".format(nameWS))
        file.write("------------\n")

        file.write("bin {0} \n".format(self.appendName))
        file.write("observation {0} \n".format(obsEvents))

        file.write("------------\n")
        file.write("## mass window [{0},{1}] \n".format(self.low_M, self.high_M))
        file.write("bin ")

        channelList = ["ggH", "qqH", "vz", "ttbar", "zjets"]
        channelName1D = ["ggH_hzz", "qqH_hzz", "bkg_vz", "bkg_ttbar", "bkg_zjets"]
        channelName2D = ["ggH_hzz", "qqH_hzz", "bkg_vz", "bkg_ttbar", "bkg_zjets"]

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
        counter = 0
        if inputs["ggH"]: counter += 1
        if inputs["qqH"]: counter += 1

        return counter

    def numberOfBgChan(self, inputs):
        counter = 0
        if inputs["vz"]: counter += 1
        if inputs["zjets"]: counter += 1
        if inputs["ttbar"]: counter += 1

        return counter
