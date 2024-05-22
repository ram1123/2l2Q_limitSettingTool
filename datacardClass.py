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
        logger.debug("Creating a new instance of datacardClass")
        self.year = year
        self.DEBUG = DEBUG
        self.loadIncludes()
        self.setup_parameters()
        #  To extend the lifecycle of all RooFit objects by storing them as attributes of self
        self.rooVars = {}
        self.rooDataSet = {}
        self.rooDataHist = {}
        self.signalCBs = {}  # Dictionary to store signalCB objects
        self.rooProdPdf = {}  # Dictionary to store rooProdPdf objects
        self.rooFormulaVars = {}  # Dictionary to store RooFormulaVar objects
        self.rooArgSets = {}  # Dictionary to store RooArgSet objects
        self.background_hists = {}
        self.background_hists_smooth = {}
        self.workspace = ROOT.RooWorkspace("w", "workspace")
        self.sigFraction = 1.0 # Fraction of signal to be used
        self.rooArgSets["funcList_zjets"] = ROOT.RooArgList()

    def clearRooArgSets(self):
        """Added this as this datacard is initialized one time and used multiple times.
            So, we need to clear the RooArgSets before using them again.
        """
        self.rooVars = {}
        self.rooDataSet = {}
        self.rooDataHist = {}
        self.signalCBs = {}  # Dictionary to store signalCB objects
        self.rooProdPdf = {}  # Dictionary to store rooProdPdf objects
        self.rooFormulaVars = {}  # Dictionary to store RooFormulaVar objects
        self.rooArgSets = {}  # Dictionary to store RooArgSet objects
        self.background_hists = {}
        self.background_hists_smooth = {}
        self.workspace = ROOT.RooWorkspace("w", "workspace")
        self.sigFraction = 1.0  # Fraction of signal to be used

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
        self.zz2l2q_mass.setRange("fullsignalrange", self.mH - 0.25 * self.mH, self.mH + 0.25 * self.mH)
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

    def setup_nuisances(self, systematics):
        """
        Set up the JES and BTAG nuisances and prepare RooArgList with all nuisances.
        """
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
            self.rooVars["CMS_scale_{}_{}_{}".format(jetString, source, self.year)] = (
                nuisance
            )

        # Create a RooArgList from all JES nuisances
        arglist_all_JES = ROOT.RooArgList()
        for nuisance in all_nuisances:
            arglist_all_JES.add(nuisance)

        # Creating BTAG nuisance
        BTAG = ROOT.RooRealVar("BTAG_" + self.jetType, "BTAG_" + self.jetType, 0, -2, 2)
        self.rooVars["BTAG_" + self.jetType] = BTAG

        # Combining BTAG with JES nuisances for cumulative effect
        arglist_all_JES_BTAG = ROOT.RooArgList()
        arglist_all_JES_BTAG.add(BTAG)
        for nuisance in all_nuisances:
            arglist_all_JES_BTAG.add(nuisance)

        # Generating the formula string for cumulative effects
        cumulative_jes_effect = "+".join(
            "@{}".format(i) for i in range(len(arglist_all_JES))
        )
        cumulative_jes_effect_with_btag = "+".join(
            "@{}".format(i + 1) for i in range(len(arglist_all_JES)) # +1 to skip the first BTAG nuisance, so len should be used with without_btag
        )
        for i in range(arglist_all_JES.getSize()):
            logger.debug("{:4}. JES nuisances: {}".format(i, arglist_all_JES[i]))

        for i in range(arglist_all_JES_BTAG.getSize()):
            logger.debug("{:4}. JES nuisances with BTAG: {}".format(i, arglist_all_JES_BTAG[i]))
        # logger.debug("BTAG nuisance: {}".format(BTAG.GetName()))
        logger.debug("cumulative_jes_effect: {}".format(cumulative_jes_effect))
        logger.debug("cumulative_jes_effect_with_btag: {}".format(cumulative_jes_effect_with_btag))

        self.rooVars["arglist_all_JES"] = arglist_all_JES
        self.rooVars["arglist_all_JES_BTAG"] = arglist_all_JES_BTAG
        self.rooVars["cumulative_jes_effect"] = cumulative_jes_effect
        self.rooVars["cumulative_jes_effect_with_btag"] = cumulative_jes_effect_with_btag

    def initialize_settings(self, theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, SanityCheckPlot):
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

    def initialize_workspace_and_observables(self, theMH, theInputs):
        self.setup_workspace()  # Setup the RooWorkspace
        self.set_append_name()  # Set the finalState (fs) and postfix variable
        self.set_category_tree()  # Set the category tree: cat_tree and cat
        self.set_channels(theInputs) # Set the channels: ggH, qqH, vz, zjets, ttbar
        self.set_jet_type() # Set the jet type: resolved or merged
        self.theInputs = theInputs # Set the inputs coming from txt file

        logger.error("channel: {}, cat: {}, jetType: {}".format(self.channel, self.cat, self.jetType))

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

    def makeCardsWorkspaces(self, theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, SanityCheckPlot=True):
        self.clearRooArgSets() #Added this as this datacard is initialized one time and used multiple times.
        # So, we need to clear the RooArgSets before using them again.
        self.initialize_settings(theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, SanityCheckPlot)
        self.initialize_workspace_and_observables(theMH, theInputs)

        # if (
        #     (self.channel == self.ID_2muMerged and self.cat == "b_tagged" and self.jetType == "merged")
        #     or
        #     (self.channel == self.ID_2muMerged and self.cat == "untagged" and self.jetType == "merged")
        #     or
        #     (self.channel == self.ID_2eMerged and self.cat == "vbf_tagged" and self.jetType == "merged")
        # ):
        #     """ For debugging purpose, break if channel is 2mu_Merged and cat is b_tagged and jetType is merged.
        #     """
        #     logger.error("break if channel: {}, cat: {}, jetType: {}".format(self.channel, self.cat, self.jetType))
        #     return

        ## ------------------------- SYSTEMATICS CLASSES ----------------------------- ##
        systematics = systematicsClass(self.mH, True, theInputs, self.year, self.DEBUG)  # the second argument is for the systematic unc. coming from XSxBR

        ## ------------------------- RATES ----------------------------- ##
        sigRate_ggH_Shape, vbf_ratioGGH, btag_ratioGGH = self.getSignalRates("ggH")
        sigRate_VBF_Shape, vbf_ratioVBF, btag_ratioVBF = self.getSignalRates("VBF")

        self.setup_background_shapes_ReproduceRate_fs()
        self.setup_background_shapes_ReproduceRate_2l()
        self.setup_background_shapes_ReproduceRate("vz")
        self.setup_background_shapes_ReproduceRate("ttbar")
        self.setup_background_shapes_ReproduceRate("zjet")

        if self.SanityCheckPlot:
            self.compareOldNewBinnedHistogram()

        self.setup_background_shapes()
        # FIXME: This rate is not used in the legacy code. But, we should switch to this for rate calculation
        # bkgRate_vz_Shape = self.calculate_background_rates("vz")
        # bkgRate_ttbar_Shape = self.calculate_background_rates("ttbar")
        # bkgRate_zjets_Shape = self.calculate_background_rates("zjet")

        # obtain rate using the new histogram based on the number of bins and range used in self.bins and self.low_M, self.high_M
        # this is obtained from the 1D histograms present in the templates1D directory
        bkgRate_vz_Shape = self.getRateFromSmoothedHist("vz")
        bkgRate_ttbar_Shape = self.getRateFromSmoothedHist("ttbar")
        bkgRate_zjets_Shape = self.getRateFromSmoothedHist("zjet")

        logger.debug("Signal rates: ggH: {:.4f}, qqH: {:.4f}".format(sigRate_ggH_Shape, sigRate_VBF_Shape))
        # logger.debug("Background rates (smoothed): VZ: {:.4f}".format(bkgRate_vz_Shape))
        logger.debug("Background rates: VZ: {:.4f}, TTbar: {:.4f}, Zjets: {:.4f}\n\n".format(bkgRate_vz_Shape, bkgRate_ttbar_Shape, bkgRate_zjets_Shape))

        ## --------------------------- DATACARDS -------------------------- ##

        rates = {}
        rates["ggH"] = sigRate_ggH_Shape
        rates["qqH"] = sigRate_VBF_Shape

        rates["vz"] = bkgRate_vz_Shape
        rates["ttbar"] = bkgRate_ttbar_Shape
        rates["zjets"] = bkgRate_zjets_Shape

        name_ShapeWS = ""
        name_ShapeWS2 = ""
        name_ShapeWS = "{0}/HCG/{1:.0f}/hzz2l2q_{2}_{3:.0f}TeV.input.root".format(self.outputDir, self.mH, self.appendName, self.sqrts)
        name_ShapeWS2 = "hzz2l2q_{0}_{1:.0f}TeV.input.root".format(self.appendName, self.sqrts)

        # ================== SIGNAL SHAPE ================== #
        SignalShapeFile = "Resolution/2l2q_resolution_{0}_{1}.root".format(self.jetType, self.year)
        SignalShape = self.open_root_file(SignalShapeFile)

        self.get_signal_shape_mean_error(SignalShape)
        self.setup_signal_shape(SignalShape, systematics, "VBF", self.channel)
        self.setup_signal_shape(SignalShape, systematics, "ggH", self.channel)

        # logger.info("==========  print mean and sigma  =========")
        # self.rooVars["rfv_mean_{}_{}".format("VBF", self.channel)].Print("v")
        # self.rooVars["rfv_sigma_{}_{}".format("VBF", self.channel)].Print("v")
        # self.rooVars["rfv_mean_{}_{}".format("ggH", self.channel)].Print("v")
        # self.rooVars["rfv_sigma_{}_{}".format("ggH", self.channel)].Print("v")
        # logger.info("==========  END =========")

        # logger.debug("============  SignalCB Shape ggH  ============")
        # self.signalCBs["signalCB_{}_{}".format("ggH", self.channel)].Print("v")

        # logger.debug("============  SignalCB Shape VBF  ============")
        # self.signalCBs["signalCB_{}_{}".format("VBF", self.channel)].Print("v")

        ## -------------------------  Get 2D template ----------------------------- ##
        templateDir = "templates2D"
        templateSigName = "{}/2l2q_spin0_template_{}.root".format(
            templateDir, self.year
        )
        logger.debug("Using templateSigName: {}".format(templateSigName))

        TString_sig = "sig_resolved"
        if self.channel in ["mumuqq_Merged", "eeqq_Merged"]:
            TString_sig = "sig_merged"

        # Opening template ROOT files
        sigTempFile = ROOT.TFile(templateSigName)
        if not sigTempFile or sigTempFile.IsZombie():
            print("Error opening signal template file:", templateSigName)
            return

        # Setup discriminant variable
        sigTemplate = sigTempFile.Get(TString_sig)
        dBins = sigTemplate.GetYaxis().GetNbins()
        dLow = sigTemplate.GetYaxis().GetXmin()
        dHigh = sigTemplate.GetYaxis().GetXmax()
        self.rooVars["D"] = ROOT.RooRealVar("Dspin0", "Discriminant Variable (Dspin0)", dLow, dHigh)
        self.rooVars["D"].setBins(dBins)
        logger.debug("Discriminant variable setup with bins: {}, range: [{}, {}]".format(dBins, dLow, dHigh))
        sigTempFile.Close()

        ## ------------------------- DATA ----------------------------- ##
        self.rooDataSet["data_obs"] = self.getData()
        getattr(self.workspace, "import")(self.rooDataSet["data_obs"], ROOT.RooFit.Rename("data_obs"))
        # self.workspace.Print("v")

        ## ------------------------- MELA 2D ----------------------------- ##
        self.getRooProdPDFofMorphedSignal(TString_sig, templateSigName)
        self.setup_nuisances(systematics) # needed for  module "calculate_signal_rates_next"
        self.setup_signal_fractions(vbf_ratioVBF)
        self.calculate_signal_rates_next(self.rooVars["frac_VBF"], self.rooVars["frac_ggH"], vbf_ratioGGH, vbf_ratioVBF, btag_ratioGGH, btag_ratioVBF)

        logger.debug("jetType: {}, cat: {}".format(self.jetType, self.cat))
        # self.workspace.Print("v")

        ## ------------------------- Backgrounds 2D: Write to workspace ----------------------------- ##

        morphBkgVarName = "CMS_zz2l2q_bkgMELA_{}".format(self.jetType)
        self.rooVars[morphBkgVarName] = ROOT.RooRealVar(morphBkgVarName, morphBkgVarName, 0, -2, 2)
        self.rooVars[morphBkgVarName].setConstant(False)
        self.rooArgSets["morphVarListBkg"] = ROOT.RooArgList(self.rooVars[morphBkgVarName])

        self.get_Zjets_funcList()
        self.getRooProdPDFofMorphedBackgrounds() # I am trying to add all process inside the function so no need to pass the process
        self.workspace.writeToFile(name_ShapeWS)
        if self.DEBUG:
            self.workspace.Print("v")
            exit()

        ## Write Datacards
        systematics.setSystematics(rates)

        name_Shape = "{0}/HCG/{1:.0f}/hzz2l2q_{2}_{3:.0f}TeV.txt".format(self.outputDir, self.mH, self.appendName, self.sqrts)
        fo = open(name_Shape, "wb")
        self.WriteDatacard(fo, theInputs, name_ShapeWS2, rates, self.rooDataSet["data_obs"].numEntries(), self.is2D)

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

    def getRateFromSmoothedHist(self, process):
        """
        Get the rate for the given process from the smoothed histograms.
        """
        rate = 0.0
        # rate = self.background_hists_smooth["{}_smooth".format(process, )].Integral()
        for key, hist in self.background_hists_smooth.items():
            logger.debug("key: {}, hist: {}".format(key, hist))
        logger.debug("Hist name from rate is obtained: {}_{}_smooth".format(process, self.cat_tree))
        rate = self.background_hists_smooth["{}_{}_smooth".format(process, self.cat_tree)].Integral()
        return rate

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
        self.rooDataSet["data_obs"] = ROOT.RooDataSet(datasetName, datasetName, data_obs_tree, ROOT.RooArgSet(self.zz2l2q_mass, self.rooVars["D"]))

        logger.debug("data_obs: {}".format(self.rooDataSet["data_obs"]))
        return self.rooDataSet["data_obs"]

    def getRooProdPDFofMorphedSignal(self, TString_sig, templateSigName):
        # Determine the signal template name based on the channel
        logger.debug("Inside getRooProdPDFofMorphedSignal")
        # self.signalCBs["signalCB_{}_{}".format("VBF", self.channel)].Print("v")
        # self.signalCBs["signalCB_{}_{}".format("ggH", self.channel)].Print("v")
        # logger.debug("====================================================")

        self.rooVars["funcList_ggH"] = ROOT.RooArgList()
        self.rooVars["funcList_VBF"] = ROOT.RooArgList()

        # Opening template ROOT files
        sigTempFile = ROOT.TFile(templateSigName)
        if not sigTempFile or sigTempFile.IsZombie():
            print("Error opening signal template file:", templateSigName)
            return

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

        # Get the RooHistPdf for signal templates separately for ggH and VBF
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
            self.rooVars["morphVarListSig_" + self.jetType].add(self.rooVars[morphSigVarName])  ## just one morphing for all signal processes

        logger.debug("I am here...")
        # ERROR: Date: 16 may 2024: Find out why it is not working for ggH. But its working fine for VBF.
        # sample_list = ["ggH"]
        # sample_list = ["VBF"]
        sample_list = ["ggH", "VBF"]
        logger.debug("=========   Print FastVerticalInterpHistPdf2D: START  =========")
        for sample in sample_list:
            logger.debug("sample: {}".format(sample))
            # get the morphing variable ROOT.FastVerticalInterpHistPdf2D
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
            # self.rooVars[TemplateName].Print("v")
        logger.debug("=========   Print FastVerticalInterpHistPdf2D: END  =========")

        for sample in sample_list:
            # 2D -> mzz + Djet
            if sample == "ggH":
                tag_temp = "ggH"
            elif sample == "VBF":
                tag_temp = "qqH"

            TemplateName = "sigTemplateMorphPdf_" + sample + "_" + TString_sig + "_" + str(self.year)
            name = "sigCB2d_{}_{}".format(tag_temp, self.year)
            logger.debug("======  parameters entered in rooProdPdf  ======")
            logger.debug("self.signalCBs[signalCB_{}_{}]".format(sample, self.channel))
            # self.signalCBs["signalCB_{}_{}".format(sample, self.channel)].Print("v")

            logger.debug("==========  print mean and sigma  =========")
            # self.rooVars["rfv_mean_{}_{}".format(sample, self.channel)].Print("v")
            # self.rooVars["rfv_sigma_{}_{}".format(sample, self.channel)].Print("v")
            logger.debug("==========  END =========")

            logger.debug("self.rooVars[{}]".format(TemplateName))
            # self.rooVars[TemplateName].Print("v")

            logger.debug("self.rooVars[D]")
            # self.rooVars["D"].Print("v")

            self.rooProdPdf[name] = ROOT.RooProdPdf(
                name,
                name,
                ROOT.RooArgSet(self.signalCBs["signalCB_{}_{}".format(sample, self.channel)]),
                ROOT.RooFit.Conditional(
                    ROOT.RooArgSet(self.rooVars[TemplateName]),
                    ROOT.RooArgSet(self.rooVars["D"]),
                ),
            )
            # self.rooVars[name].Print("v")

        # logger.debug("======  Print self.rooProdPdf: START  ======")
        # print(self.rooProdPdf)
        # logger.debug("======  Print self.rooProdPdf: END  ======")

        sample_list = ["ggH", "VBF"]
        for sample in sample_list:
            if sample == "ggH":
                tag_temp = "ggH"
            elif sample == "VBF":
                tag_temp = "qqH"

            name = "sigCB2d_{}_{}".format(tag_temp, self.year)
            if sample == "ggH":
                self.rooProdPdf[name].SetNameTitle("ggH_hzz", "ggH_hzz")
                # self.rooProdPdf[name].Print("v")
            elif sample == "VBF":
                self.rooProdPdf[name].SetNameTitle("qqH_hzz", "qqH_hzz")
                # self.rooProdPdf[name].Print("v")

            getattr(self.workspace, "import")(self.rooProdPdf[name], ROOT.RooFit.RecycleConflictNodes())
            logger.debug("added to workspace: {}".format(name))
            # self.workspace.Print("v")

    def get_Zjets_funcList(self):
        # Open zjets template file
        templatezjetsBkgName = "templates2D/2l2q_spin0_template_{}.root".format(self.year)
        zjetsTempFile = ROOT.TFile(templatezjetsBkgName)
        if not zjetsTempFile or zjetsTempFile.IsZombie():
            logger.error("Failed to open zjets template file: {}".format(templatezjetsBkgName))
            return

        # Initialize funcList_zjets as RooArgList
        if "funcList_zjets" not in self.rooArgSets:
            self.rooArgSets["funcList_zjets"] = ROOT.RooArgList()

        TString_bkg = "DY_resolved"
        if self.channel in ["mumuqq_Merged", "eeqq_Merged"]:
            TString_bkg = "DY_merged"

        # Process variations
        variations = ["", "_Up", "_Down"]
        for variation in variations:
            logger.debug("variation: {}".format(variation))
            if not self.bkgMorph and variation != "":
                logger.error("Skipping variation: {}".format(variation))
                continue

            variations_tag_for_hist = "_up" if variation == "_Up" else "_dn" if variation == "_Down" else ""
            logger.debug("variations: {}, variations_tag_for_hist: {}".format(variation, variations_tag_for_hist))
            logger.debug("Looking for hist: {}".format(TString_bkg + variations_tag_for_hist))

            zjetsTemplate = zjetsTempFile.Get(TString_bkg + variations_tag_for_hist)
            if not zjetsTemplate:
                logger.debug("Failed to get zjets template: {}".format(TString_bkg + variations_tag_for_hist))
                continue

            logger.debug("zjetsTemplate: Name: {} Title: {} NbinsX: {}".format( zjetsTemplate.GetName(), zjetsTemplate.GetTitle(), zjetsTemplate.GetNbinsX(), ) )

            TemplateName = "zjetsTempDataHist_{}{}_{}".format(TString_bkg, variation, self.year)
            self.rooDataHist[TemplateName] = ROOT.RooDataHist(
                TemplateName,
                TemplateName,
                ROOT.RooArgList(self.zz2l2q_mass, self.rooVars["D"]),
                zjetsTemplate,
            )

            PdfName = "zjetsTemplatePdf_{}{}_{}".format(TString_bkg, variation, self.year)
            self.rooDataHist[PdfName] = ROOT.RooHistPdf(
                PdfName,
                PdfName,
                ROOT.RooArgSet(self.zz2l2q_mass, self.rooVars["D"]),
                self.rooDataHist[TemplateName],
            )

            self.rooArgSets["funcList_zjets"].add(self.rooDataHist[PdfName])

        for i in range(self.rooArgSets["funcList_zjets"].getSize()):
            logger.debug("{:2}: funcList_zjets: {}".format(i, self.rooArgSets["funcList_zjets"].at(i).GetName()))

    def getRooProdPDFofMorphedBackgrounds(self):
        background_list = ["vz", "ttbar", "zjets"]
        # background_list = ["vz"]
        # background_list = [process]
        for process in background_list:
            vzTemplateName = "{}_{}_{}".format(process, self.appendName, self.year)
            vzTemplateMVV = self.background_hists["{}_template".format(process.replace("zjets", "zjet"))]
            logger.debug("vzTemplateName: {}, \n\tvzTemplateMVV: {}".format(vzTemplateName, vzTemplateMVV))
            # exit()
            # Create and store RooDataHist
            self.rooDataHist[vzTemplateName] = ROOT.RooDataHist(
                vzTemplateName.replace("zjets", "zjet"), vzTemplateName.replace("zjets", "zjet"), ROOT.RooArgList(self.zz2l2q_mass), vzTemplateMVV
                # Is there any benefit of using smooth vz_smooth instead of vzTemplateMVV?
                # This comment goes same for ttbar and zjet templates
            )

            logger.debug("====    self.rooDataHist[{}]:    ====".format(vzTemplateName))
            # vzTemplateMVV.Print("v")
            # print("++++++++")
            # self.rooDataHist[vzTemplateName].Print("v")
            # logger.debug("====    self.rooDataHist[{}]: END    ====".format(vzTemplateName))

            # Create and store RooHistPdf
            vzTemplatePdfName = "{}Pdf".format(vzTemplateName.replace("zjets", "zjet"))
            self.rooDataHist[vzTemplatePdfName] = ROOT.RooHistPdf(
                vzTemplatePdfName,
                vzTemplatePdfName,
                ROOT.RooArgSet(self.zz2l2q_mass),
                self.rooDataHist[vzTemplateName],
            )

            for i in range(self.rooArgSets["funcList_zjets"].getSize()):
                logger.debug("{:2}: funcList_zjets: {}".format(i, self.rooArgSets["funcList_zjets"].at(i).GetName()))

            # morphing
            for i in range(self.rooArgSets["morphVarListBkg"].getSize()):
                logger.debug("{:2}: morphVarListBkg: {}".format(i, self.rooArgSets["morphVarListBkg"].at(i).GetName()))

            TemplateName = "bkgTemplateMorphPdf_{}_{}_{}".format(process, self.jetType, self.year)
            self.rooVars[TemplateName] = ROOT.FastVerticalInterpHistPdf2D(
                TemplateName,
                TemplateName,
                self.zz2l2q_mass,
                self.rooVars["D"],
                True,
                self.rooArgSets["funcList_zjets"],  # identical to all background processes
                self.rooArgSets["morphVarListBkg"], # identical to all background processes
                1.0,
                1,
            )

            name = "bkg2d_{}_{}".format(process, self.year)
            self.rooProdPdf[name] = ROOT.RooProdPdf(
                name,
                name,
                ROOT.RooArgSet(self.rooDataHist["{}Pdf".format(vzTemplateName.replace("zjets", "zjet"))]),
                ROOT.RooFit.Conditional(
                    ROOT.RooArgSet(self.rooVars["bkgTemplateMorphPdf_{}_{}_{}".format(process, self.jetType, self.year)]),
                    ROOT.RooArgSet(self.rooVars["D"]),
                ),
            )

            self.rooProdPdf[name].SetNameTitle("bkg_{}".format(process), "bkg_{}".format(process))
            # self.rooProdPdf[name].Print("v")

            getattr(self.workspace, "import")(self.rooProdPdf[name], ROOT.RooFit.RecycleConflictNodes())
        # self.workspace.Print("v")

    def get_signal_shape_mean_error(self, SignalShape):
        # Define systematic variables for both electron and muon channels
        systematic_vars = [
            ("mean_e_sig", "CMS_zz2l2q_mean_e_sig", 0.0, -5.0, 5.0),
            ("sigma_e_sig", "CMS_zz2l2q_sigma_e_sig", 0.0, -5.0, 5.0),
            ("mean_m_sig", "CMS_zz2l2q_mean_m_sig", 0.0, -5.0, 5.0),
            ("sigma_m_sig", "CMS_zz2l2q_sigma_m_sig", 0.0, -5.0, 5.0),
            ("mean_j_sig", "CMS_zz2l2q_mean_j_sig", 0.0, -5.0, 5.0),
            ("sigma_j_sig", "CMS_zz2l2q_sigma_j_sig", 0.0, -5.0, 5.0),
            ("mean_J_sig", "CMS_zz2lJ_mean_J_sig", 0.0, -5.0, 5.0),
            ("sigma_J_sig", "CMS_zz2lJ_sigma_J_sig", 0.0, -5.0, 5.0),
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
            # Sigma of DCB using a dynamic approach
            sigma_value = (SignalShape.Get("sigma")).GetListOfFunctions().First().Eval(self.mH)
            self.rooVars["sigma_{}_{}".format(signal_type, self.channel)] = ROOT.RooRealVar(
                "sigma_{}_{}".format(signal_type, self.channel),
                "sigma_{}_{}".format(signal_type, self.channel),
                sigma_value,
            )

            # logger.debug("===      Input values for mean and sigma      ===")
            # self.rooVars["sigma_{}_{}".format(signal_type, self.channel)].Print("v")
            # self.rooFormulaVars["sigma_SF_" + self.channel].Print("v")
            # logger.debug("===      END      ===")

            self.rooVars["rfv_sigma_{}_{}".format(signal_type, self.channel)] = ROOT.RooFormulaVar(
                "rfv_sigma_{}_{}".format(signal_type, self.channel),
                "@0*@1",
                ROOT.RooArgList(self.rooVars["sigma_{}_{}".format(signal_type, self.channel)], self.rooFormulaVars["sigma_SF_" + self.channel]),
            )
            # self.rooVars["rfv_sigma_{}_{}".format(signal_type, self.channel)].Print("v")

    def setup_signal_shape(self, SignalShape, systematics, signal_type, channel):
        name = "bias_{}_{}".format(signal_type, channel)
        self.rooVars["bias_{}_{}".format(signal_type, channel)] = ROOT.RooRealVar(
            name,
            name,
            SignalShape.Get("mean").GetListOfFunctions().First().Eval(self.mH)
            - self.mH,
        )
        name = "mean_{}_{}".format(signal_type, channel)
        self.rooVars["mean_{}_{}".format(signal_type, channel)] = ROOT.RooFormulaVar(name, "@0+@1", ROOT.RooArgList(self.rooVars["MH"], self.rooVars["bias_{}_{}".format(signal_type, channel)]))

        name = "rfv_mean_{}_{}".format(signal_type, channel)
        self.rooVars["rfv_mean_{}_{}".format(signal_type, channel)] = ROOT.RooFormulaVar(
            name, "@0+@1", ROOT.RooArgList(self.rooVars["mean_{}_{}".format(signal_type, channel)], self.rooVars["mean_err_" + self.channel])
        )

        self.rooVars["a1_{}_{}_{}".format(signal_type, channel, self.year)] = ROOT.RooRealVar(
            "a1_{}_{}_{}".format(signal_type, channel, self.year), "Low tail", SignalShape.Get("a1").GetListOfFunctions().First().Eval(self.mH)
        )
        self.rooVars["n1_{}_{}_{}".format(signal_type, channel, self.year)] = ROOT.RooRealVar(
            "n1_{}_{}_{}".format(signal_type, channel, self.year), "Low tail parameter", SignalShape.Get("n1").GetListOfFunctions().First().Eval(self.mH)
        )
        self.rooVars["a2_{}_{}_{}".format(signal_type, channel, self.year)] = ROOT.RooRealVar(
            "a2_{}_{}_{}".format(signal_type, channel, self.year), "High tail", SignalShape.Get("a2").GetListOfFunctions().First().Eval(self.mH),
        )
        self.rooVars["n2_{}_{}_{}".format(signal_type, channel, self.year)] = ROOT.RooRealVar(
            "n2_{}_{}_{}".format(signal_type, channel, self.year), "High tail parameter", SignalShape.Get("n2").GetListOfFunctions().First().Eval(self.mH)
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
        # logger.debug("==========  print mean and sigma  =========")
        # self.rooVars["rfv_mean_{}_{}".format(signal_type, self.channel)].Print("v")
        # self.rooVars["rfv_sigma_{}_{}".format(signal_type, self.channel)].Print("v")
        # logger.debug("==========  END =========")

    def getSignalRates(self, signal_type):
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

    def calculate_background_rates(self, process):
        """
        Calculate and return background rates for various processes based on the histograms provided in self.background_hists.
        For now not used. But keep it for future reference or some cross-checking.
        """
        # Integral calculations for background histograms
        bkgRate_Shape = {
            "untagged": self.background_hists[process + "_untagged_template"].Integral(),
            "btagged": self.background_hists[process + "_btagged_template"].Integral(),
            "vbftagged": self.background_hists[process + "_vbftagged_template"].Integral(),
        }

        # return the integral values based on jet type and category
        #  check which category and jet type is being used then return the integral value

        if self.cat == "untagged":
            return bkgRate_Shape["untagged"]
        elif self.cat == "b_tagged":
            return bkgRate_Shape["btagged"]
        elif self.cat == "vbf_tagged":
            return bkgRate_Shape["vbftagged"]

    def setup_background_shapes_ReproduceRate_fs(self):
        """This function sets the histogram templates for the background shapes for the given final state that can be 2e, or 2mu and based on jets category.

        Raises:
            IOError: If no root file is found or the file is a zombie
            ValueError: If the histogram is not found in the file
        """
        # Open the template file
        template_file_path = "templates1D/Template1D_spin0_{}_{}.root".format(self.fs, self.year)
        temp_file_fs = ROOT.TFile(template_file_path, "READ")

        if not temp_file_fs or temp_file_fs.IsZombie():
            raise IOError("Could not open the template file: {}".format(template_file_path))

        # Define histogram names based on jet type and category
        prefix = "hmass_{}SR".format(self.jetType)
        hist_suffixes = {
            "vz": "VZ_perInvFb_Bin50GeV",
            "ttbar": "TTplusWW_perInvFb_Bin50GeV",
            "zjet": "Zjet_perInvFb_Bin50GeV",
        }
        categories = {
            "untagged": "",
            "btagged": "btag",
            "vbftagged": "vbf",
        }

        # Retrieve histograms for each background and category
        for key, suffix in hist_suffixes.items():
            for category, cat_string in categories.items():
                hist_name = "{}{}_{}".format(prefix, cat_string, suffix)
                hist = temp_file_fs.Get(hist_name)

                if not hist:
                    raise ValueError("Histogram {} not found in file: {}".format(hist_name, template_file_path))

                # Detach histogram from file ref: https://root-forum.cern.ch/t/nonetype-feturned-from-function-that-returns-th1f/18287/2?u=ramkrishna
                hist.SetDirectory(ROOT.gROOT)

                logger.debug("Range of histogram {}: {} to {}".format(hist_name, hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax()))

                # Store the histogram in the background_hists dictionary
                hist_key = "{}_{}_template".format(key, category)
                self.background_hists[hist_key] = hist

                logger.debug("Stored histogram {} in background_hists".format(hist_key))

        # Log all histograms in background_hists
        for key, hist in self.background_hists.items():
            logger.debug("Background histogram - key: {}, hist: {}".format(key, hist))

        temp_file_fs.Close()

    def setup_background_shapes_ReproduceRate_2l(self):
        """This function sets the histogram templates for the background shapes for the inclusive 2l final state and inclusive jet category and year.

        Raises:
            IOError: If no root file is found or the file is a zombie
            ValueError: If the histogram is not found in the file
        """
        # Open the template file
        template_file_path = "templates1D/Template1D_spin0_2l_{}.root".format(self.year)
        temp_file_fs = ROOT.TFile(template_file_path, "READ")

        if not temp_file_fs or temp_file_fs.IsZombie():
            raise IOError("Could not open the template file: {}".format(template_file_path))

        # Define histogram names based on jet type and category
        prefix = "hmass_{}SR".format(self.jetType)
        hist_suffixes = {
            "vz": "VZ_perInvFb_Bin50GeV",
            "ttbar": "TTplusWW_perInvFb_Bin50GeV",
            "zjet": "Zjet_perInvFb_Bin50GeV",
        }

        # Retrieve histograms for each background
        for key, suffix in hist_suffixes.items():
            hist_name = "{}_{}".format(prefix, suffix)
            hist = temp_file_fs.Get(hist_name)

            if not hist:
                raise ValueError("Histogram {} not found in file: {}".format(hist_name))

            # Detach histogram from file ref: https://root-forum.cern.ch/t/nonetype-feturned-from-function-that-returns-th1f/18287/2?u=ramkrishna
            hist.SetDirectory(ROOT.gROOT)

            logger.debug("Range of histogram {}: {} to {}".format(hist_name, hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax()))

            # Store the histogram in the background_hists dictionary
            hist_key = "{}_template".format(key)
            self.background_hists[hist_key] = hist

            logger.debug("Stored histogram {} in background_hists".format(hist_key))

        # Log all histograms in background_hists
        for key, hist in self.background_hists.items():
            logger.debug("Background histogram - key: {}, hist: {}".format(key, hist))

        temp_file_fs.Close()

    def setup_background_shapes_ReproduceRate(self, process):
        categories = ["_untagged", "_btagged", "_vbftagged", ""]

        # for cat in categories:
        # print("{}{}_template".format(process, cat))
        # vzTemplateMVV = self.background_hists["{}{}_template".format(process, cat)]

        vzTemplateMVV = self.background_hists["{}{}_template".format(process, "")]

        hist_smooth_name = "{}_smooth".format(process)
        self.background_hists_smooth["{}{}_smooth".format(process, "")] = ROOT.TH1F(hist_smooth_name, hist_smooth_name, self.bins, self.low_M, self.high_M)
        self.background_hists_smooth["{}{}_smooth".format(process, "_untagged")]= ROOT.TH1F(hist_smooth_name + "_untagged", hist_smooth_name + "_untagged", self.bins, self.low_M, self.high_M)
        self.background_hists_smooth["{}{}_smooth".format(process, "_btagged")] = ROOT.TH1F(hist_smooth_name + "_btagged", hist_smooth_name + "_btagged", self.bins, self.low_M, self.high_M)
        self.background_hists_smooth["{}{}_smooth".format(process, "_vbftagged")] = ROOT.TH1F(hist_smooth_name + "_vbftagged", hist_smooth_name + "_vbftagged", self.bins, self.low_M, self.high_M)

        # Smooth the histograms
        for i in range(0, self.bins):
            mVV_tmp = self.background_hists_smooth["{}{}_smooth".format(process, "")].GetBinCenter(i + 1)
            bin_width = self.background_hists_smooth["{}{}_smooth".format(process, "")].GetBinWidth(i + 1)

            for j in range(0, vzTemplateMVV.GetXaxis().GetNbins()):
                mVV_tmp_low = vzTemplateMVV.GetXaxis().GetBinLowEdge(j + 1)
                mVV_tmp_up = vzTemplateMVV.GetXaxis().GetBinUpEdge(j + 1)
                bin_width_tmp = vzTemplateMVV.GetXaxis().GetBinWidth(j + 1)

                if mVV_tmp >= mVV_tmp_low and mVV_tmp < mVV_tmp_up:
                    # Below the histogram is scaled by the ratio of the bin widths to factor out the different binning
                    self.background_hists_smooth["{}{}_smooth".format(process, "")].SetBinContent(i + 1, self.background_hists["{}{}_template".format(process, "")].GetBinContent(j + 1) * bin_width / bin_width_tmp)
                    self.background_hists_smooth["{}{}_smooth".format(process, "")].SetBinError(i + 1, self.background_hists["{}{}_template".format(process, "")].GetBinError(j + 1) * bin_width / bin_width_tmp)

                    self.background_hists_smooth["{}{}_smooth".format(process, "_untagged")].SetBinContent(i + 1, self.background_hists["{}{}_template".format(process, "_untagged")].GetBinContent(j + 1) * bin_width / bin_width_tmp)
                    self.background_hists_smooth["{}{}_smooth".format(process, "_untagged")].SetBinError(i + 1, self.background_hists["{}{}_template".format(process, "_untagged")].GetBinError(j + 1) * bin_width / bin_width_tmp)

                    self.background_hists_smooth["{}{}_smooth".format(process, "_btagged")].SetBinContent(i + 1, self.background_hists["{}{}_template".format(process, "_btagged")].GetBinContent(j + 1) * bin_width / bin_width_tmp)
                    self.background_hists_smooth["{}{}_smooth".format(process, "_btagged")].SetBinError(i + 1, self.background_hists["{}{}_template".format(process, "_btagged")].GetBinError(j + 1) * bin_width / bin_width_tmp)

                    self.background_hists_smooth["{}{}_smooth".format(process, "_vbftagged")].SetBinContent(i + 1, self.background_hists["{}{}_template".format(process, "_vbftagged")].GetBinContent(j + 1) * bin_width / bin_width_tmp)
                    self.background_hists_smooth["{}{}_smooth".format(process, "_vbftagged")].SetBinError(i + 1, self.background_hists["{}{}_template".format(process, "_vbftagged")].GetBinError(j + 1) * bin_width / bin_width_tmp)

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
        # Open the template file for the given final state (fs)
        TempFile_fs = ROOT.TFile(
            "templates1D/Template1D_spin0_{}_{}.root".format(self.fs, self.year), "READ"
        )
        if not TempFile_fs or TempFile_fs.IsZombie():
            raise FileNotFoundError(
                "Could not open the template file for final state {}".format(self.fs)
            )

        # Define the histogram names based on jet type and category
        prefix = "hmass_{}SR".format(self.jetType)
        hist_suffixes = {
            "vz": "VZ_perInvFb_Bin50GeV",
            "ttbar": "TTplusWW_perInvFb_Bin50GeV",
            "zjet": "Zjet_perInvFb_Bin50GeV",
        }
        categories = {"untagged": "", "btagged": "btag", "vbftagged": "vbf"}

        # Retrieve histograms for each background
        for key, suffix in hist_suffixes.items():
            for category, cat_string in categories.items():
                hist_name = "{}{}_{}".format(prefix, cat_string, suffix)
                hist = TempFile_fs.Get(hist_name)
                hist.SetDirectory(
                    ROOT.gROOT
                )  # Detach histogram from file ref: https://root-forum.cern.ch/t/nonetype-feturned-from-function-that-returns-th1f/18287/2?u=ramkrishna

                # print range of histogram
                logger.debug("Range of histogram {}: {} to {}".format(hist_name, hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax()))
                if not hist:
                    raise ValueError("Histogram {} not found in file".format(hist_name))
                self.background_hists[key + "_" + category + "_template"] = hist

                # Print integral for sanity check
                logger.debug("{} integral: {}".format(hist_name, hist.Integral()))

        # Smooth the histograms
        for key, hist in self.background_hists.items():
            hist_smooth = hist.Clone()
            hist_smooth.Smooth(1)  # Apply simple smoothing; adjust parameters as needed

            # Print integral for sanity check
            logger.debug("Smoothed {} integral: {}".format(key, hist.Integral()))
            if self.SanityCheckPlot:
                save_histograms(hist, hist_smooth, "{}/{}_smoothed.png".format(self.outputDir, key))

        # Create RooHistPdf objects
        self.rooHistPdfs = {}
        for key, hist in self.background_hists.items():
            # get the integral of hist
            # Create rooDataHist from TH1 histogram
            self.rooVars["data_hist"] = ROOT.RooDataHist(
                "dh_{}".format(key),
                "DataHist for {}".format(key),
                ROOT.RooArgList(self.zz2l2q_mass),
                hist,
            )

            # Create RooHistPdf from rooDataHist
            self.rooHistPdfs["pdf_{}".format(key)] = ROOT.RooHistPdf(
                "pdf_{}".format(key),
                "PDF for {}".format(key),
                ROOT.RooArgSet(self.zz2l2q_mass),
                self.rooVars["data_hist"],
            )

            # logger.debug("check rooHistPdfs: {}".format("pdf_{}".format(key)))
            # self.rooHistPdfs["pdf_{}".format(key)].Print("v")
            # logger.debug("check rooHistPdfs: END")

            # plot and save the rooDataHist and RooHistPdf
            if self.SanityCheckPlot:
                # compute the integral of the pdf
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

                # plot_and_save(
                #     self.rooVars["data_hist"],
                #     self.rooHistPdfs["pdf_{}".format(key)],
                #     self.zz2l2q_mass,
                #     key,
                #     self.outputDir,
                # )

        logger.debug(self.background_hists)
        # return self.rooHistPdfs

    def setup_signal_fractions(self, vbfRatioVBF):
        # Set the VBF fraction based on condition
        if self.FracVBF == -1:
            logger.info("FracVBF is set to be floating within [0, 1]")
            self.rooVars["frac_VBF"] = ROOT.RooRealVar("frac_VBF", "Fraction of VBF", vbfRatioVBF, 0.0, 1.0)
            # Define fraction of events coming from ggH process
            self.rooVars["frac_ggH"] = ROOT.RooFormulaVar("frac_ggH", "(1-@0)", ROOT.RooArgList(self.rooVars["frac_VBF"]))
        else:
            logger.info("Using fixed FracVBF = {}".format(self.FracVBF))
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
        # Calculate signal rates using predefined formulas based on category and jet type
        formula_ggH, formula_VBF = self.get_formulas(ggH_vbf_ratio, vbfRatioVBF, ggH_btag_ratio, VBF_btag_ratio)
        logger.debug("Formula ggH: {}".format(formula_ggH))
        logger.debug("Formula VBF: {}".format(formula_VBF))
        # Create RooFormulaVars for ggH and VBF signal rates, use appropriate arguments list based on category
        if self.cat == "b_tagged" or self.cat == "untagged":
            for i in range(0, len(self.rooVars["arglist_ggH_with_BTAG"])):  # 0, 1, 2, 3, 4, 5
                logger.debug("{:2}: arglist_ggH_with_BTAG: {}".format(i, self.rooVars["arglist_ggH_with_BTAG"].at(i).GetName()))
            for i in range(0, len(self.rooVars["arglist_ggH_with_BTAG"])):  # 0, 1, 2, 3, 4, 5
                logger.debug("{:2}: arglist_ggH_with_BTAG: {}".format(i, self.rooVars["arglist_ggH_with_BTAG"].at(i).GetName()))
            for i in range(0, len(self.rooVars["arglist_VBF"])):  # 0, 1, 2, 3, 4, 5
                logger.debug("{:2}: arglist_VBF: {}".format(i, self.rooVars["arglist_VBF"].at(i).GetName()))
            for i in range(0, len(self.rooVars["arglist_ggH"])):  # 0, 1, 2, 3, 4, 5
                logger.debug("{:2}: arglist_ggH: {}".format(i, self.rooVars["arglist_ggH"].at(i).GetName()))
            rfvSigRate_ggH = ROOT.RooFormulaVar("ggH_hzz_norm", formula_ggH, self.rooVars["arglist_ggH_with_BTAG"])
            rfvSigRate_VBF = ROOT.RooFormulaVar("qqH_hzz_norm", formula_VBF, self.rooVars["arglist_VBF_with_BTAG"])
        else:
            for i in range(0, len(self.rooVars["arglist_ggH_with_BTAG"])):  # 0, 1, 2, 3, 4, 5
                logger.debug("{:2}: arglist_ggH_with_BTAG: {}".format(i, self.rooVars["arglist_ggH_with_BTAG"].at(i).GetName()))
            for i in range(0, len(self.rooVars["arglist_ggH_with_BTAG"])):  # 0, 1, 2, 3, 4, 5
                logger.debug("{:2}: arglist_ggH_with_BTAG: {}".format(i, self.rooVars["arglist_ggH_with_BTAG"].at(i).GetName()))
            for i in range(0, len(self.rooVars["arglist_VBF"])):  # 0, 1, 2, 3, 4, 5
                logger.debug("{:2}: arglist_VBF: {}".format(i, self.rooVars["arglist_VBF"].at(i).GetName()))
            for i in range(0, len(self.rooVars["arglist_ggH"])):  # 0, 1, 2, 3, 4, 5
                logger.debug("{:2}: arglist_ggH: {}".format(i, self.rooVars["arglist_ggH"].at(i).GetName()))
            logger.debug("formula_ggH: {}".format(formula_ggH))
            for i in range(0, len(self.rooVars["arglist_ggH"])):
                logger.debug("{:2}: arglist_ggH: {}".format(i, self.rooVars["arglist_ggH"].at(i).GetName()))

            logger.debug("formula_VBF: {}".format(formula_VBF))
            for i in range(0, len(self.rooVars["arglist_VBF"])):
                logger.debug("{:2}: arglist_VBF: {}".format(i, self.rooVars["arglist_VBF"].at(i).GetName()))
            rfvSigRate_ggH = ROOT.RooFormulaVar("ggH_hzz_norm", formula_ggH, self.rooVars["arglist_ggH"])
            rfvSigRate_VBF = ROOT.RooFormulaVar("qqH_hzz_norm", formula_VBF, self.rooVars["arglist_VBF"])

        # # Debugging outputs
        logger.debug("Signal Rate ggH: {}".format(rfvSigRate_ggH.getVal()))
        logger.debug("Signal Rate VBF: {}".format(rfvSigRate_VBF.getVal()))

        getattr(self.workspace, "import")(rfvSigRate_ggH, ROOT.RooFit.RecycleConflictNodes())
        getattr(self.workspace, "import")(rfvSigRate_VBF, ROOT.RooFit.RecycleConflictNodes())

    def get_formulas(self, vbfRatioGGH, vbfRatioVBF, btagRatioGGH, btagRatioVBF):
        num_jes_sources = len(self.rooVars["arglist_all_JES"])
        cumulative_jes_effect = self.rooVars["cumulative_jes_effect"]
        cumulative_jes_effect_with_btag = self.rooVars["cumulative_jes_effect_with_btag"]
        logger.debug("Number of JES sources: {}".format(num_jes_sources))
        # Define the formula strings based on category and jet type
        if self.cat == "vbf_tagged":
            formula_ggH = "(1+0.16*({}))*@{}*@{}*@{}".format(
                self.rooVars["cumulative_jes_effect"],
                num_jes_sources,
                num_jes_sources+1,
                num_jes_sources+2,
            )
            # formula_VBF = "(1+0.12*@0)*@1*@2*@3"
            formula_VBF = "(1+0.12*({}))*@{}*@{}*@{}".format(
                self.rooVars["cumulative_jes_effect"],
                num_jes_sources,
                num_jes_sources+1,
                num_jes_sources+2,
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
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
        elif self.jetType == "resolved" and self.cat == "untagged":
            formula_ggH = "(1-0.03*@0*{})*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioGGH),
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioGGH),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            formula_VBF = "(1-0.11*@0*{})*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioVBF),
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioVBF),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
                )
        elif self.jetType == "merged" and self.cat == "b_tagged":
            formula_ggH = "(1+0.08*@0)*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioGGH),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            formula_VBF = "(1+0.07*@0)*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioVBF),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
        elif self.jetType == "merged" and self.cat == "untagged":
            formula_ggH = "(1-0.16*@0*{})*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioGGH),
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioGGH),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            formula_VBF = "(1-0.2*@0*{})*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioVBF),
                self.rooVars["cumulative_jes_effect_with_btag"],
                str(vbfRatioVBF),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
        else:
            # Give error that the category is not recognized
            raise ValueError("Category {} not recognized. So, can't get_formulas()".format(self.cat))

        return formula_ggH, formula_VBF

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

    def compareOldNewBinnedHistogram(self):
        # Make a comparison of the smoothed histograms and the original histograms
        #  plot them on the same canvas with different colors and add the legend

        process = {"vz", "ttbar", "zjet"}
        categories = {"_untagged", "_btagged", "_vbftagged", ""}

        for proc in process:
            for cat in categories:
                hist = self.background_hists["{}{}_template".format(proc, cat)]
                hist_smooth = self.background_hists_smooth["{}{}_smooth".format(proc, cat)]
                # save_histograms(hist_smooth, hist, "{}/{}_{}_smoothed.png".format(self.outputDir, proc, cat))
                save_histograms(hist, hist_smooth, "{}/{}_{}_smoothed.png".format(self.outputDir, proc, cat))
