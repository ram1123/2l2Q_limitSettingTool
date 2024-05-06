#! /usr/bin/env python
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kInfo
import math
import sys
from array import array
from decimal import *
from subprocess import *

from inputReader import *
from systematicsClass import *
from utils import *
from utils_hist import getTH1F, save_hisograms, get_histogram, create_up_down_hist
from utils_hist import check_object_validity

ROOT.gROOT.ProcessLine(
    "struct zz2lJ_massStruct {\
   Double_t zz2lJ_mass;\
   };"
)

from ROOT import zz2lJ_massStruct

## ------------------------------------
##  card and workspace class
## ------------------------------------


class datacardClass:

    def __init__(self, year, DEBUG=False):
        self.year = year
        self.DEBUG = DEBUG
        self.loadIncludes()
        self.setup_parameters()
        # self.systematics = systematicsClass()

        #  To extend the lifecycle of all RooFit objects by storing them as attributes of self
        self.rooVars = {}

    def setup_parameters(self):
        # Parameters for the analysis
        self.low_M = 0
        self.high_M = 4000
        self.bins = int((self.high_M - self.low_M) / 100)
        # bins_val = [0, 50, 100, 150, 200, 250, 300, 350, 400, 500, 600, 700, 800, 900, 1000, 1200, 1500, 2000, 2500, 3000, 4000]
        # self.bins = len(bins_val  ) - 1
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

    def setup_workspace(self):
        self.workspace = ROOT.RooWorkspace("w", "workspace")
        self.workspace.importClassCode(ROOT.RooDoubleCB.Class(), True)
        self.workspace.importClassCode(ROOT.RooFormulaVar.Class(), True)

    def open_root_file(self, file_path):
        file = ROOT.TFile(file_path, "READ")
        if file.IsOpen():
            logger.debug("Successfully opened file: {}".format(file_path))
        else:
            logger.error("Failed to open file: {}".format(file_path))
            raise FileNotFoundError("Could not open file: {}".format(file_path))
        return file

    def setup_roo_real_var(self, name, title, value, constant=True):
        var = ROOT.RooRealVar(name, title, value)
        var.setConstant(constant)
        return var

    def set_jet_type(self):
        self.jetType = "resolved"
        if 'merged' in (self.channel).lower():
            self.jetType = "merged"

    def setup_observables(self):
        """Setup the observable with specific ranges and binning."""
        logger.error("Setting up observables")
        self.mzz_name = "zz2l2q_mass"

        # add zz2l2q_mass to rooVars
        self.zz2l2q_mass = ROOT.RooRealVar(self.mzz_name, self.mzz_name, self.low_M, self.high_M)
        self.zz2l2q_mass.setBins(self.bins)

        if self.jetType == "merged":
            self.zz2l2q_mass.SetName("zz2lJ_mass")
            self.zz2l2q_mass.SetTitle("zz2lJ_mass")

        # INFO: Set fullsignalrange as 25% of the mass window around the Higgs mass
        self.zz2l2q_mass.setRange("fullrange", self.low_M, self.high_M)
        self.zz2l2q_mass.setRange("fullsignalrange",  self.mH - 0.25*self.mH,  self.mH + 0.25*self.mH)
        self.rooVars["zz2l2q_mass"] = self.zz2l2q_mass

    def get_signal_shape_mean_error(self, SignalShape, signal_type):
        ## -------- Variable Definitions -------- ##
        ## e
        name = "CMS_zz2l2q_mean_e_sig"
        self.rooVars['mean_e_sig'] = ROOT.RooRealVar(name, "mzz_mean_e_sig", 0.0, -5.0, 5.0)
        self.rooVars['mean_e_sig'].setVal(0.0)
        ## resolution
        name = "CMS_zz2l2q_sigma_e_sig"
        self.rooVars['sigma_e_sig'] = ROOT.RooRealVar(name, "mzz_sigma_e_sig", 0.0, -5.0, 5.0)
        self.rooVars['sigma_e_sig'].setVal(0.0)
        ## m
        name = "CMS_zz2l2q_mean_m_sig"
        self.rooVars['mean_m_sig'] = ROOT.RooRealVar(name, "mzz_mean_m_sig", 0.0, -5.0, 5.0)
        self.rooVars['mean_m_sig'].setVal(0.0)
        ## resolution
        name = "CMS_zz2l2q_sigma_m_sig"
        self.rooVars['sigma_m_sig'] = ROOT.RooRealVar(name, "mzz_sigma_m_sig", 0.0, -5.0, 5.0)
        self.rooVars['sigma_m_sig'].setVal(0.0)
        ## resolved jet JES JER
        name = "CMS_zz2l2q_mean_j_sig"
        self.rooVars['mean_j_sig'] = ROOT.RooRealVar(name, "mzz_mean_j_sig", 0.0, -5.0, 5.0)
        self.rooVars['mean_j_sig'].setVal(0.0)
        ## resolution
        name = "CMS_zz2l2q_sigma_j_sig"
        self.rooVars['sigma_j_sig'] = ROOT.RooRealVar(name, "mzz_sigma_j_sig", 0.0, -5.0, 5.0)
        self.rooVars['sigma_j_sig'].setVal(0.0)
        ## merged jet JEC JER
        name = "CMS_zz2lJ_mean_J_sig"
        self.rooVars['mean_J_sig'] = ROOT.RooRealVar(name, "mzz_mean_J_sig", 0.0, -5.0, 5.0)
        self.rooVars['mean_J_sig'].setVal(0.0)
        ## resolution
        name = "CMS_zz2lJ_sigma_J_sig"
        self.rooVars['sigma_J_sig'] = ROOT.RooRealVar(name, "mzz_sigma_J_sig", 0.0, -5.0, 5.0)
        self.rooVars['sigma_J_sig'].setVal(0.0)

        ########################
        ## JES lepton scale uncertainty
        name = "mean_m_err"
        self.rooVars['mean_m_err'] = ROOT.RooRealVar(
            name, name, float(self.theInputs["CMS_zz2l2q_mean_m_err"])
        )
        name = "mean_e_err"
        self.rooVars['mean_e_err'] = ROOT.RooRealVar(
            name, name, float(self.theInputs["CMS_zz2l2q_mean_e_err"])
        )
        name = "mean_j_err"
        self.rooVars['mean_j_err'] = ROOT.RooRealVar(
            name, name, float(self.theInputs["CMS_zz2l2q_mean_j_err"])
        )
        name = "mean_J_err"
        self.rooVars['mean_J_err'] = ROOT.RooRealVar(
            name, name, float(self.theInputs["CMS_zz2lJ_mean_J_err"])
        )
        ###
        ## resolution uncertainty
        name = "sigma_m_err"
        self.rooVars['sigma_m_err'] = ROOT.RooRealVar(
            name, name, float(self.theInputs["CMS_zz2l2q_sigma_m_err"])
        )
        logger.debug("{}: {}".format(name, self.rooVars['sigma_m_err'].getVal()))
        name = "sigma_e_err"
        self.rooVars['sigma_e_err'] = ROOT.RooRealVar(
            name, name, float(self.theInputs["CMS_zz2l2q_sigma_e_err"])
        )
        logger.debug("{}: {}".format(name, self.rooVars['sigma_e_err'].getVal()))
        name = "sigma_j_err"
        self.rooVars['sigma_j_err'] = ROOT.RooRealVar(
            name, name, float(self.theInputs["CMS_zz2l2q_sigma_j_err"])
        )
        logger.debug("{}: {}".format(name, self.rooVars['sigma_j_err'].getVal()))
        name = "sigma_J_err"
        self.rooVars['sigma_J_err'] = ROOT.RooRealVar(
            name, name, float(self.theInputs["CMS_zz2lJ_sigma_J_err"])
        )
        logger.debug("{}: {}".format(name, self.rooVars['sigma_J_err'].getVal()))

        self.rooVars['mean_err'] = ROOT.RooFormulaVar()
        name = "mean_err_" + (self.channel)
        if self.channel == self.ID_2eResolved:
            self.rooVars['mean_err'] = ROOT.RooFormulaVar(
                name,
                "(@0*@1*@3 + @0*@2*@4)/2",
                ROOT.RooArgList(
                    self.MH, self.rooVars['mean_e_sig'], self.rooVars['mean_j_sig'], self.rooVars['mean_e_err'], self.rooVars['mean_j_err']
                ),
            )
        elif self.channel == self.ID_2eMerged:
            self.rooVars['mean_err'] = ROOT.RooFormulaVar(
                name,
                "(@0*@1*@3 + @0*@2*@4)/2",
                ROOT.RooArgList(
                    self.MH, self.rooVars['mean_e_sig'], self.rooVars['mean_J_sig'], self.rooVars['mean_e_err'], self.rooVars['mean_J_err']
                ),
            )
        elif self.channel == self.ID_2muResolved:
            self.rooVars['mean_err'] = ROOT.RooFormulaVar(
                name,
                "(@0*@1*@3 + @0*@2*@4)/2",
                ROOT.RooArgList(
                    self.MH, self.rooVars['mean_m_sig'], self.rooVars['mean_j_sig'], self.rooVars['mean_m_err'], self.rooVars['mean_j_err']
                ),
            )
        elif self.channel == self.ID_2muMerged:
            self.rooVars['mean_err'] = ROOT.RooFormulaVar(
                name,
                "(@0*@1*@3 + @0*@2*@4)/2",
                ROOT.RooArgList(
                    self.MH, self.rooVars['mean_m_sig'], self.rooVars['mean_J_sig'], self.rooVars['mean_m_err'], self.rooVars['mean_J_err']
                ),
            )
        logger.debug("{}: {}".format(name, self.rooVars['mean_err'].getVal()))

        self.rooVars['rfv_sigma_SF'] = ROOT.RooFormulaVar()
        name = "sigma_SF_" + (self.channel)
        if self.channel == self.ID_2muResolved:  # FIXME: How we get the number 0.05?
            self.rooVars['rfv_sigma_SF'] = ROOT.RooFormulaVar(
                name,
                "TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))",
                ROOT.RooArgList(self.rooVars['sigma_m_sig'], self.rooVars['sigma_j_sig'], self.rooVars['sigma_m_err'], self.rooVars['sigma_j_err']),
            )
        if self.channel == self.ID_2eResolved:
            self.rooVars['rfv_sigma_SF'] = ROOT.RooFormulaVar(
                name,
                "TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))",
                ROOT.RooArgList(self.rooVars['sigma_e_sig'], self.rooVars['sigma_j_sig'], self.rooVars['sigma_e_err'], self.rooVars['sigma_j_err']),
            )
        if self.channel == self.ID_2muMerged:
            self.rooVars['rfv_sigma_SF'] = ROOT.RooFormulaVar(
                name,
                "TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))",
                ROOT.RooArgList(self.rooVars['sigma_m_sig'], self.rooVars['sigma_J_sig'], self.rooVars['sigma_m_err'], self.rooVars['sigma_J_err']),
            )
        if self.channel == self.ID_2eMerged:
            self.rooVars['rfv_sigma_SF'] = ROOT.RooFormulaVar(
                name,
                "TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))",
                ROOT.RooArgList(self.rooVars['sigma_e_sig'],self.rooVars['sigma_J_sig'], self.rooVars['sigma_e_err'], self.rooVars['sigma_J_err']),
            )

        logger.debug("{}: {}".format(name, self.rooVars['rfv_sigma_SF'].getVal()))

        ##################
        # sigma of DCB
        name = "sigma_{}_{}".format(signal_type, self.channel)
        self.rooVars['sigma'] = ROOT.RooRealVar(
            name,
            name,
            (SignalShape.Get("sigma")).GetListOfFunctions().First().Eval(self.mH),
        )
        logger.debug("{}: {}".format(name, self.rooVars['sigma'].getVal()))

        name = "rfv_sigma_{}_{}".format(signal_type, self.channel)
        self.rooVars['rfv_sigma'] = ROOT.RooFormulaVar(
            name, "@0*@1", ROOT.RooArgList(self.rooVars['sigma'], self.rooVars['rfv_sigma_SF'])
        )
        # print name of RooFormulaVar and its value to the logger
        logger.debug("{}: {}".format(self.rooVars['mean_err'].GetName(), self.rooVars['mean_err'].getVal()))
        logger.debug("{}: {}".format(self.rooVars['rfv_sigma'].GetName(), self.rooVars['rfv_sigma'].getVal()))

        return self.rooVars['mean_err'], self.rooVars['rfv_sigma']

    def setup_signal_shape(self, SignalShape, systematics, signal_type, channel):
        """Setup the signal shape with systematic adjustments and channel-specific errors using RooFormulaVar.
        signal_type (str): The type of signal to setup the shape for (e.g. 'ggH', 'VBF').
        """
        # mean (bias) of DCB
        # MOREINFO: Did not understand why we get the bias from the mean of the gaussian then again obtain the mean of the DCB by adding the bias to the mean of the gaussian?
        name = "bias_{}_{}".format(signal_type, channel)
        self.rooVars["bias_{}_{}".format(signal_type, channel)] = ROOT.RooRealVar(
            name,
            name,
            SignalShape.Get("mean").GetListOfFunctions().First().Eval(self.mH)
            - self.mH,
        )

        name = "mean_{}_{}".format(signal_type, channel)
        self.rooVars["mean_{}_{}".format(signal_type, channel)] = ROOT.RooFormulaVar(name, "@0+@1", ROOT.RooArgList(self.MH, self.rooVars["bias_{}_{}".format(signal_type, channel)]))

        self.rooVars['mean_err'], self.rooVars['rfv_sigma'] = self.get_signal_shape_mean_error(SignalShape, signal_type)
        logger.debug("mean_err: {}".format(self.rooVars['mean_err'].getVal()))
        logger.debug("rfv_sigma: {}".format(self.rooVars['rfv_sigma'].getVal()))

        # mean of DCB
        name = "rfv_mean_{}_{}".format(signal_type, channel)
        self.rooVars['rfv_mean'] = ROOT.RooFormulaVar(
            name, "@0+@1", ROOT.RooArgList(self.rooVars["mean_{}_{}".format(signal_type, channel)], self.rooVars['mean_err'])
        )
        logger.debug("{}: {}".format(name, self.rooVars['rfv_mean'].getVal()))

        # Double Crystal Ball parameters
        self.rooVars["a1_{}_{}_{}".format(signal_type, channel, self.year)] = ROOT.RooRealVar("a1_{}_{}_{}".format(signal_type, channel, self.year), "Low tail", SignalShape.Get("a1").GetListOfFunctions().First().Eval(self.mH))
        self.rooVars["n1_{}_{}_{}".format(signal_type, channel, self.year)] = ROOT.RooRealVar("n1_{}_{}_{}".format(signal_type, channel, self.year), "Low tail parameter", SignalShape.Get("n1").GetListOfFunctions().First().Eval(self.mH))
        self.rooVars["a2_{}_{}_{}".format(signal_type, channel, self.year)] = ROOT.RooRealVar("a2_{}_{}_{}".format(signal_type, channel, self.year), "High tail", SignalShape.Get("a2").GetListOfFunctions().First().Eval(self.mH))
        self.rooVars["n2_{}_{}_{}".format(signal_type, channel, self.year)] = ROOT.RooRealVar("n2_{}_{}_{}".format(signal_type, channel, self.year), "High tail parameter", SignalShape.Get("n2").GetListOfFunctions().First().Eval(self.mH))

        # print a1, a2, n1, and n2
        logger.debug(self.rooVars["a1_{}_{}_{}".format(signal_type, channel, self.year)].getValV())
        logger.debug(self.rooVars["a2_{}_{}_{}".format(signal_type, channel, self.year)].getValV())
        logger.debug(self.rooVars["n1_{}_{}_{}".format(signal_type, channel, self.year)].getValV())
        logger.debug(self.rooVars["n2_{}_{}_{}".format(signal_type, channel, self.year)].getValV())

        # Create the Double Crystal Ball signal model
        self.rooVars["signalCB_{}_{}".format(signal_type, channel)] = ROOT.RooDoubleCB(
            "signalCB_{}_{}".format(signal_type, channel),
            "Double Crystal Ball Model for {} in {}".format(signal_type, channel),
            self.rooVars["zz2l2q_mass"],
            self.rooVars["rfv_mean"],
            self.rooVars["rfv_sigma"],
            self.rooVars["a1_{}_{}_{}".format(signal_type, channel, self.year)],
            self.rooVars["n1_{}_{}_{}".format(signal_type, channel, self.year)],
            self.rooVars["a2_{}_{}_{}".format(signal_type, channel, self.year)],
            self.rooVars["n2_{}_{}_{}".format(signal_type, channel, self.year)],
        )
        self.rooVars["signalCB_{}_{}".format(signal_type, self.channel)].Print("v")
        # logger.debug("DCB shape: {}".format(self.rooVars['signalCB_{}_{}'.format(signal_type, channel)]))
        # logger.error(self.rooVars["signalCB_{}_{}".format(signal_type, channel)].Print('v'))

        # logger.debug(self.rooVars["signalCB_{}_{}".format(signal_type, channel)].getValV())
        # logger.debug(self.rooVars["zz2l2q_mass"].getValV())

        low, high = self.rooVars["zz2l2q_mass"].getRange("fullsignalrange")
        logger.debug("fullsignalrange: {low} to {high}".format(low=low, high=high))

        fullRangeSigRate = (
            self.rooVars["signalCB_{}_{}".format(signal_type, channel)]
            .createIntegral(
                ROOT.RooArgSet(self.rooVars["zz2l2q_mass"]),
                ROOT.RooFit.Range("fullsignalrange"),
            )
            .getVal()
        )

        logger.debug("{} rate: {}".format(self.rooVars["signalCB_{}_{}".format(signal_type, channel)].GetName(), fullRangeSigRate))

    def set_append_name(self):
        self.fs = "2e"
        if self.channel == self.ID_2muResolved:
            self.fs = "2mu"
        if self.channel == self.ID_2muMerged:
            self.fs = "2mu"
        postfix = self.channel + "_" + self.cat
        self.appendName = postfix
        if self.DEBUG:
            print("appendName is channel + cat", postfix)

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

    def initialize_settings(self, theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, SanityCheckPlot):
        self.mH = theMH
        self.lumi = theInputs["lumi"]
        self.sqrts = theInputs["sqrts"]
        self.channel = theInputs["decayChannel"]
        # print("Channel: ", self.channel)
        self.is2D = theis2D
        self.outputDir = theOutputDir
        self.sigMorph = True  # assuming this is always True; adjust as needed
        self.bkgMorph = True  # assuming this is always True; adjust as needed
        self.cat = theCat
        self.FracVBF = theFracVBF
        self.SanityCheckPlot = SanityCheckPlot
        logger.debug("Settings initialized for channel: {}".format(self.channel))

    # main datacard and workspace function
    def makeCardsWorkspaces(
        self,
        theMH,
        theis2D,
        theOutputDir,
        theInputs,
        theCat,
        theFracVBF,
        SanityCheckPlot=True,
    ):

        ## --------------- SETTINGS AND DECLARATIONS --------------- ##
        self.initialize_settings(theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, SanityCheckPlot)
        # self.setup_workspace()
        self.set_append_name()
        self.set_category_tree()
        self.set_channels(theInputs)
        self.set_jet_type()
        self.theInputs = theInputs

        self.LUMI = self.setup_roo_real_var(
            "LUMI_{0:.0f}_{1}".format(self.sqrts, self.year),
            "Integrated Luminosity",
            self.lumi,
        )
        self.MH = self.setup_roo_real_var("MH", "MH", self.mH)

        ## ---------------- SET PLOTTING STYLE ---------------- ##
        ROOT.setTDRStyle(True)
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetPadLeftMargin(0.16)

        ## ------------------------- SYSTEMATICS CLASSES ----------------------------- ##
        ## systematic uncertainty for Xsec X BR, no uncertainies on signal PDF/QCD scale
        systematics = systematicsClass(
            self.mH, True, theInputs, self.year, self.DEBUG
        )  # the second argument is for the systematic unc. coming from XSxBR

        self.setup_observables()
        zz2l2q_mass = self.zz2l2q_mass

        # ================== SIGNAL SHAPE ================== #
        # INFO: Setup signal shapes for ggH and VBF for each channel
        # Read signal parameters from Resolution root file:
        SignalShapeFile = "Resolution/2l2q_resolution_{}_{}.root".format(self.jetType, self.year)
        SignalShape = self.open_root_file(SignalShapeFile)

        self.setup_signal_shape(SignalShape, systematics, 'ggH', self.channel)
        signalCB_ggH = self.rooVars["signalCB_ggH_{}".format(self.channel)]
        self.rooVars["signalCB_{}_{}".format("ggH", self.channel)].Print("v")

        self.setup_signal_shape(SignalShape, systematics, 'VBF', self.channel)
        signalCB_VBF = self.rooVars['signalCB_VBF_{}'.format(self.channel)]
        self.rooVars["signalCB_{}_{}".format("VBF", self.channel)].Print("v")

        low, high = self.rooVars["zz2l2q_mass"].getRange("fullsignalrange")
        logger.debug("fullsignalrange: {low} to {high}".format(low=low, high=high))

        check_object_validity(self.rooVars['zz2l2q_mass'], "zz2l2q_mass")
        check_object_validity(self.rooVars['signalCB_ggH_{}'.format(self.channel)], "signalCB_ggH_{}".format(self.channel))

        fullRangeSigRate = (self.rooVars["signalCB_{}_{}".format("ggH", self.channel)].createIntegral(ROOT.RooArgSet(self.zz2l2q_mass),ROOT.RooFit.Range("fullsignalrange")).getVal())
        logger.debug("{} rate: {}".format(self.rooVars["signalCB_{}_{}".format("ggH", channel)].GetName(), fullRangeSigRate))

        # fullRangeSigRate_VBF = (self.rooVars["signalCB_{}_{}".format("VBF", self.channel)].createIntegral(ROOT.RooArgSet(self.zz2l2q_mass),ROOT.RooFit.Range("fullsignalrange")).getVal())
        # logger.debug("{} rate: {}".format(self.rooVars["signalCB_{}_{}".format("VBF", channel)].GetName(), fullRangeSigRate_VBF))

        exit()
