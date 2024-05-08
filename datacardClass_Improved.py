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
from utils_hist import (plot_and_save, save_histograms)

ROOT.gROOT.ProcessLine(
    "struct zz2lJ_massStruct {"
    "   Double_t zz2lJ_mass;"
    "};"
)

from ROOT import zz2lJ_massStruct

class datacardClass:

    def __init__(self, year, DEBUG=False):
        self.year = year
        self.DEBUG = DEBUG
        self.loadIncludes()
        self.setup_parameters()
        #  To extend the lifecycle of all RooFit objects by storing them as attributes of self
        self.rooVars = {}
        self.background_hists = {}
        self.workspace = ROOT.RooWorkspace("w", "workspace")

    def setup_parameters(self):
        self.low_M = 0
        self.high_M = 4000
        self.bins = int((self.high_M - self.low_M) / 100)
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

    def setup_roo_real_var(self, name, title, value, constant=True):
        var = ROOT.RooRealVar(name, title, value)
        var.setConstant(constant)
        return var

    def set_jet_type(self):
        self.jetType = "resolved"
        if 'merged' in (self.channel).lower():
            self.jetType = "merged"

    def setup_observables(self):
        logger.info("Setting up observables")
        self.mzz_name = "zz2l2q_mass"
        self.zz2l2q_mass = ROOT.RooRealVar(self.mzz_name, self.mzz_name, self.low_M, self.high_M)
        self.zz2l2q_mass.setBins(self.bins)

        if self.jetType == "merged":
            self.zz2l2q_mass.SetName("zz2lJ_mass")
            self.zz2l2q_mass.SetTitle("zz2lJ_mass")

        self.zz2l2q_mass.setRange("fullrange", self.low_M, self.high_M)
        self.zz2l2q_mass.setRange("fullsignalrange", self.mH - 0.25*self.mH, self.mH + 0.25*self.mH)
        self.rooVars["zz2l2q_mass"] = self.zz2l2q_mass
        logger.info("Observables are set up successfully")

    def get_signal_shape_mean_error(self, SignalShape, signal_type):
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
        sigma_formula = "sqrt((1+0.05*@0*@2)*(1+@1*@3))"

        self.rooVars["mean_err"] = ROOT.RooFormulaVar(
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

        self.rooVars["rfv_sigma_SF"] = ROOT.RooFormulaVar(
            "sigma_SF_" + self.channel,
            sigma_formula,
            ROOT.RooArgList(
                self.rooVars["sigma_{}_sig".format(lep_type)],
                self.rooVars["sigma_{}_sig".format(jet_suffix)],
                self.rooVars["sigma_{}_err".format(lep_type)],
                self.rooVars["sigma_{}_err".format(jet_suffix)],
            ),
        )

        # Sigma of DCB using a dynamic approach
        sigma_value = (SignalShape.Get("sigma")).GetListOfFunctions().First().Eval(self.mH)
        self.rooVars["sigma"] = ROOT.RooRealVar(
            "sigma_{}_{}".format(signal_type, self.channel),
            "sigma_{}_{}".format(signal_type, self.channel),
            sigma_value,
        )

        self.rooVars["rfv_sigma"] = ROOT.RooFormulaVar(
            "rfv_sigma_{}_{}".format(signal_type, self.channel),
            "@0*@1",
            ROOT.RooArgList(self.rooVars["sigma"], self.rooVars["rfv_sigma_SF"]),
        )

        return self.rooVars["mean_err"], self.rooVars["rfv_sigma"]

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

        mean_err, rfv_sigma = self.get_signal_shape_mean_error(SignalShape, signal_type)
        name = "rfv_mean_{}_{}".format(signal_type, channel)
        self.rooVars['rfv_mean'] = ROOT.RooFormulaVar(
            name, "@0+@1", ROOT.RooArgList(self.rooVars["mean_{}_{}".format(signal_type, channel)], mean_err)
        )
        self.rooVars["a1_{}_{}_{}".format(signal_type, channel, self.year)] = ROOT.RooRealVar(
            "a1_{}_{}_{}".format(signal_type, channel, self.year), "Low tail", SignalShape.Get("a1").GetListOfFunctions().First().Eval(self.mH)
        )
        self.rooVars["n1_{}_{}_{}".format(signal_type, channel, self.year)] = ROOT.RooRealVar(
            "n1_{}_{}_{}".format(signal_type, channel, self.year), "Low tail parameter", SignalShape.Get("n1").GetListOfFunctions().First().Eval(self.mH)
        )
        self.rooVars["a2_{}_{}_{}".format(signal_type, channel, self.year)] = (
            ROOT.RooRealVar(
                "a2_{}_{}_{}".format(signal_type, channel, self.year),
                "High tail",
                SignalShape.Get("a2").GetListOfFunctions().First().Eval(self.mH),
            )
        )
        self.rooVars["n2_{}_{}_{}".format(signal_type, channel, self.year)] = ROOT.RooRealVar(
            "n2_{}_{}_{}".format(signal_type, channel, self.year), "High tail parameter", SignalShape.Get("n2").GetListOfFunctions().First().Eval(self.mH)
        )
        self.rooVars["signalCB_{}_{}".format(signal_type, channel)] = ROOT.RooDoubleCB(
            "signalCB_{}_{}".format(signal_type, channel),
            "Double Crystal Ball Model for {} in {}".format(signal_type, channel),
            self.rooVars["zz2l2q_mass"],
            self.rooVars["rfv_mean"],
            rfv_sigma,
            self.rooVars["a1_{}_{}_{}".format(signal_type, channel, self.year)],
            self.rooVars["n1_{}_{}_{}".format(signal_type, channel, self.year)],
            self.rooVars["a2_{}_{}_{}".format(signal_type, channel, self.year)],
            self.rooVars["n2_{}_{}_{}".format(signal_type, channel, self.year)]
        )
        self.rooVars["signalCB_{}_{}".format(signal_type, channel)].Print("v")

        fullRangeSigRate = (
            self.rooVars["signalCB_{}_{}".format(signal_type, self.channel)]
            .createIntegral(
                ROOT.RooArgSet(self.zz2l2q_mass), ROOT.RooFit.Range("fullsignalrange")
            )
            .getVal()
        )
        logger.debug("{} rate: {}".format(self.rooVars["signalCB_{}_{}".format(signal_type, channel)].GetName(), fullRangeSigRate))

    def setup_background_shapes(self):
        # Open the template file for the given final state (fs)
        TempFile_fs = ROOT.TFile("templates1D/Template1D_spin0_{}_{}.root".format(self.fs, self.year), "READ")
        if not TempFile_fs or TempFile_fs.IsZombie():
            raise FileNotFoundError("Could not open the template file for final state {}".format(self.fs))

        # Define the histogram names based on jet type and category
        prefix = "hmass_{}SR".format(self.jetType)
        hist_suffixes = {
            "vz": "VZ_perInvFb_Bin50GeV",
            "ttbar": "TTplusWW_perInvFb_Bin50GeV",
            "zjet": "Zjet_perInvFb_Bin50GeV"
        }
        categories = {
            "untagged": "",
            "btagged": "btag",
            "vbftagged": "vbf"
        }

        # Retrieve histograms for each background
        for key, suffix in hist_suffixes.items():
            for category, cat_string in categories.items():
                hist_name = "{}{}_{}".format(prefix, cat_string, suffix)
                hist = TempFile_fs.Get(hist_name)
                hist.SetDirectory(ROOT.gROOT)  # Detach histogram from file ref: https://root-forum.cern.ch/t/nonetype-feturned-from-function-that-returns-th1f/18287/2?u=ramkrishna

                # print range of histogram
                logger.debug("Range of histogram {}: {} to {}".format(hist_name, hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax()))
                if not hist:
                    raise ValueError("Histogram {} not found in file".format(hist_name))
                self.background_hists[key + "_" + category + "_template"] = hist

                # Print integral for sanity check
                logger.debug("{} integral: {}".format(hist_name, hist.Integral()))

        # Smooth the histograms
        for key, hist in self.background_hists.items():
            hist_temp = hist.Clone()
            hist.Smooth(1)  # Apply simple smoothing; adjust parameters as needed

            # Print integral for sanity check
            logger.debug("Smoothed {} integral: {}".format(key, hist.Integral()))
            if self.SanityCheckPlot:
                save_histograms(hist, hist_temp, "{}_smoothed.png".format(key))

        # Create RooHistPdf objects
        self.rooHistPdfs = {}
        for key, hist in self.background_hists.items():
            # get the integral of hist
            # Create RooDataHist from TH1 histogram
            data_hist = ROOT.RooDataHist("dh_{}".format(key), "DataHist for {}".format(key), ROOT.RooArgList(self.zz2l2q_mass), hist)

            # Create RooHistPdf from RooDataHist
            pdf = ROOT.RooHistPdf("pdf_{}".format(key), "PDF for {}".format(key), ROOT.RooArgSet(self.zz2l2q_mass), data_hist)
            self.rooHistPdfs[key] = pdf

            # plot and save the RooDataHist and RooHistPdf
            if self.SanityCheckPlot:
                # compute the integral of the pdf
                logger.warning("Integral of hist: {:21}: {}".format(key, hist.Integral()))

                fullRangeBkgRate = (pdf.createIntegral(ROOT.RooArgSet(self.zz2l2q_mass), ROOT.RooFit.Range("fullsignalrange")).getVal())
                logger.warning("Integral of pdf : {:21}: {}".format(pdf.GetName(), fullRangeBkgRate))

                plot_and_save(data_hist, pdf, self.zz2l2q_mass, key, self.outputDir)

        logger.error(self.background_hists)
        # return self.rooHistPdfs

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
            "@{}".format(i + 1) for i in range(len(arglist_all_JES))
        )
        for i in range(arglist_all_JES.getSize()):
            # logger.debug("JES nuisances: {} \n{}".format(arglist_all_JES[i], arglist_all_JES[i].Print("v")))
            logger.debug("{:4}. JES nuisances: {}".format(i, arglist_all_JES[i]))
        # logger.debug("BTAG nuisance: {}".format(BTAG.GetName()))
        logger.debug("cumulative_jes_effect: {}".format(cumulative_jes_effect))
        logger.debug(
            "cumulative_jes_effect_with_btag: {}".format(
                cumulative_jes_effect_with_btag
            )
        )

        self.rooVars["arglist_all_JES"] = arglist_all_JES
        self.rooVars["arglist_all_JES_BTAG"] = arglist_all_JES_BTAG
        self.rooVars["cumulative_jes_effect"] = cumulative_jes_effect
        self.rooVars["cumulative_jes_effect_with_btag"] = (
            cumulative_jes_effect_with_btag
        )

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

    def makeCardsWorkspaces(self, theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, SanityCheckPlot=True):
        self.initialize_settings(theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF, SanityCheckPlot)
        self.setup_workspace()
        self.set_append_name()
        self.set_category_tree()
        self.set_channels(theInputs)
        self.set_jet_type()
        self.theInputs = theInputs

        # logger.error("Check cat and jetType: {}, {}".format(self.cat, self.jetType))
        # if not (self.cat == "untagged" and "merged" in self.jetType):
        # return

        self.rooVars["LUMI"] = self.setup_roo_real_var("LUMI_{0:.0f}_{1}".format(self.sqrts, self.year), "Integrated Luminosity", self.lumi)
        self.rooVars["MH"] = self.setup_roo_real_var("MH", "MH", self.mH)

        ## ---------------- SET PLOTTING STYLE ---------------- ##
        ROOT.setTDRStyle(True)
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetPadLeftMargin(0.16)

        ## ------------------------- SYSTEMATICS CLASSES ----------------------------- ##
        systematics = systematicsClass(
            self.mH, True, theInputs, self.year, self.DEBUG
        )  # the second argument is for the systematic unc. coming from XSxBR

        self.setup_observables()
        zz2l2q_mass = self.zz2l2q_mass

        # ================== SIGNAL SHAPE ================== #
        SignalShapeFile = "Resolution/2l2q_resolution_{0}_{1}.root".format(
            self.jetType, self.year
        )
        SignalShape = self.open_root_file(SignalShapeFile)

        self.setup_signal_shape(SignalShape, systematics, 'ggH', self.channel)
        signalCB_ggH = self.rooVars["signalCB_ggH_{}".format(self.channel)]
        self.rooVars["signalCB_{}_{}".format("ggH", self.channel)].Print("v")

        self.setup_signal_shape(SignalShape, systematics, 'VBF', self.channel)
        signalCB_VBF = self.rooVars['signalCB_VBF_{}'.format(self.channel)]
        self.rooVars["signalCB_{}_{}".format("VBF", self.channel)].Print("v")

        low, high = self.rooVars["zz2l2q_mass"].getRange("fullsignalrange")
        logger.debug("fullsignalrange: {0} to {1}".format(low, high))

        # check_object_validity(self.rooVars['zz2l2q_mass'], "zz2l2q_mass")
        # check_object_validity(self.rooVars['signalCB_ggH_{}'.format(self.channel)], "signalCB_ggH_{}".format(self.channel))

        # for key, value in self.rooVars.items():
        #     logger.info("{}: {}".format(key, value))

        # fullRangeSigRate = (self.rooVars["signalCB_{}_{}".format("ggH", self.channel)].createIntegral(ROOT.RooArgSet(self.zz2l2q_mass),ROOT.RooFit.Range("fullsignalrange")).getVal())
        # self.zz2l2q_mass.setRange("manualRange", 0, 3000)
        # fullRangeSigRate = (self.rooVars["signalCB_{}_{}".format("ggH", self.channel)].createIntegral(ROOT.RooArgSet(self.zz2l2q_mass),ROOT.RooFit.Range("manualRange")).getVal())
        # logger.debug("{} rate: {}".format(self.rooVars["signalCB_{}_{}".format("ggH", channel)].GetName(), fullRangeSigRate))

        # fullRangeSigRate_VBF = (self.rooVars["signalCB_{}_{}".format("VBF", self.channel)].createIntegral(ROOT.RooArgSet(self.zz2l2q_mass),ROOT.RooFit.Range("fullsignalrange")).getVal())
        # logger.debug("{} rate: {}".format(self.rooVars["signalCB_{}_{}".format("VBF", channel)].GetName(), fullRangeSigRate_VBF))
        # sys.exit()

        self.sigFraction = 1.0
        # ================== BACKGROUND SHAPE ================== #
        # Background shape
        self.setup_background_shapes()
        logger.debug("Background shapes are set up successfully")

        # Get JES and JER systematics
        # setup_nuisances(systematics)
        self.setup_nuisances(systematics)

        # # print each nuisances
        # for i in range(self.rooVars["arglist_all_JES"].getSize()):
        #     logger.debug("{:3}. JES nuisances: {} ".format(i, self.rooVars["arglist_all_JES"][i]))

        # for i in range(self.rooVars["arglist_all_JES_BTAG"].getSize()):
        #     logger.debug("{:3}. JES+BTAG nuisances: {} ".format(i, self.rooVars["arglist_all_JES_BTAG"][i]))

        # ================== Background Rate ================== #
        # self.calculate_background_rates_vz()
        # self.workspace.Print("v")

        # ================== SIGNAL RATE ================== #
        VBF_rate, VBF_vbf_ratio, VBF_btag_ratio = self.calculate_signal_rates("VBF")
        ggH_rate, ggH_vbf_ratio, ggH_btag_ratio = self.calculate_signal_rates("ggH")

        logger.info("VBF rate: {}, ggH rate: {}".format(VBF_rate, ggH_rate))
        logger.info("VBF VBF ratio: {}, ggH VBF ratio: {}".format(VBF_vbf_ratio, ggH_vbf_ratio))
        logger.info("VBF B-tag ratio: {}, ggH B-tag ratio: {}".format(VBF_btag_ratio, ggH_btag_ratio))

        self.setup_signal_fractions(VBF_vbf_ratio)
        self.calculate_signal_rates_next(
            self.rooVars["frac_VBF"], self.rooVars["frac_ggH"], ggH_vbf_ratio, VBF_vbf_ratio, ggH_btag_ratio, VBF_btag_ratio
        )
        # sys.exit()

    def setup_signal_fractions(self, vbfRatioVBF):
        # Set the VBF fraction based on condition
        if self.FracVBF == -1:
            logger.info("FracVBF is set to be floating within [0, 1]")
            self.rooVars["frac_VBF"] = ROOT.RooRealVar("frac_VBF", "Fraction of VBF", vbfRatioVBF, 0.0, 1.0)
            # Define fraction of events coming from ggH process
            self.rooVars["frac_ggH"] = ROOT.RooFormulaVar("frac_ggH", "1 - @0", ROOT.RooArgList(self.rooVars["frac_VBF"]))
        else:
            logger.info("Using fixed FracVBF = {}".format(self.FracVBF))
            self.rooVars["frac_VBF"] = ROOT.RooRealVar("frac_VBF", "Fraction of VBF", self.FracVBF, 0.0, 1.0)
            self.rooVars["frac_VBF"].setConstant(True)
            # Define fraction of events coming from ggH process
            self.rooVars["frac_ggH"] = ROOT.RooFormulaVar("frac_ggH", "1 - @0", ROOT.RooArgList(self.rooVars["frac_VBF"]))
            self.rooVars["frac_ggH"].setConstant(True)

        # return self.rooVars["frac_VBF"], self.rooVars["frac_ggH"]

    def calculate_signal_rates_next(
        self, frac_VBF, frac_ggH, ggH_vbf_ratio, VBF_vbf_ratio, ggH_btag_ratio, VBF_btag_ratio
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
        self.rooVars["arglist_ggH"].add(self.rooVars["BR"])
        self.rooVars["arglist_ggH"].add(self.rooVars["frac_ggH"])

        self.rooVars["arglist_VBF"] = ROOT.RooArgList(self.rooVars["arglist_all_JES"])
        self.rooVars["arglist_VBF"].add(self.rooVars["LUMI"])
        self.rooVars["arglist_VBF"].add(self.rooVars["BR"])
        self.rooVars["arglist_VBF"].add(self.rooVars["frac_VBF"])

        self.rooVars["arglist_ggH_with_BTAG"] = ROOT.RooArgList(self.rooVars["arglist_all_JES_BTAG"])
        self.rooVars["arglist_ggH_with_BTAG"].add(self.rooVars["LUMI"])
        self.rooVars["arglist_ggH_with_BTAG"].add(self.rooVars["BR"])
        self.rooVars["arglist_ggH_with_BTAG"].add(self.rooVars["frac_ggH"])

        self.rooVars["arglist_VBF_with_BTAG"] = ROOT.RooArgList(self.rooVars["arglist_all_JES_BTAG"])
        self.rooVars["arglist_VBF_with_BTAG"].add(self.rooVars["LUMI"])
        self.rooVars["arglist_VBF_with_BTAG"].add(self.rooVars["BR"])
        self.rooVars["arglist_VBF_with_BTAG"].add(self.rooVars["frac_VBF"])

        # Calculate signal rates using predefined formulas based on category and jet type
        formula_ggH, formula_VBF = self.get_formulas(
            ggH_vbf_ratio, VBF_vbf_ratio, ggH_btag_ratio, VBF_btag_ratio
        )
        logger.warning("Formula ggH: {}".format(formula_ggH))
        logger.warning("Formula VBF: {}".format(formula_VBF))
        # # Create RooFormulaVars for ggH and VBF signal rates, use appropriate arguments list
        rfvSigRate_ggH = ROOT.RooFormulaVar("ggH_hzz_norm", formula_ggH, self.rooVars["arglist_ggH_with_BTAG"])
        rfvSigRate_VBF = ROOT.RooFormulaVar("qqH_hzz_norm", formula_VBF, self.rooVars["arglist_ggH_with_BTAG"])

        # # Debugging outputs
        logger.debug("Signal Rate ggH: {}".format(rfvSigRate_ggH.getVal()))
        logger.debug("Signal Rate VBF: {}".format(rfvSigRate_VBF.getVal()))

        return rfvSigRate_ggH, rfvSigRate_VBF
        # exit()

    def get_formulas(self, vbfRatioGGH, vbfRatioVBF, btagRatioGGH, btagRatioVBF):
        num_jes_sources = len(self.rooVars["arglist_all_JES"])
        cumulative_jes_effect = self.rooVars["cumulative_jes_effect"]
        cumulative_jes_effect_with_btag = self.rooVars["cumulative_jes_effect_with_btag"]
        # Define the formula strings based on category and jet type
        if self.jetType == "resolved" and self.cat == "vbf_tagged":
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
        elif self.jetType == "merged" and self.cat == "vbf_tagged":
            formula_ggH = "(1+0.08*@0)*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                cumulative_jes_effect_with_btag,
                str(vbfRatioGGH),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            formula_VBF = "(1+0.07*@0)*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                cumulative_jes_effect_with_btag,
                str(vbfRatioVBF),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
        elif self.jetType == "merged" and self.cat == "untagged":
            formula_ggH = "(1-0.16*@0*{})*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioGGH),
                cumulative_jes_effect_with_btag,
                str(vbfRatioGGH),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            formula_VBF = "(1-0.2*@0*{})*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioVBF),
                cumulative_jes_effect_with_btag,
                str(vbfRatioVBF),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
        else:
            # FIXME: this category does not exits in main code. I added it for completeness
            formula_ggH = "(1-0.16*@0*{})*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioGGH),
                cumulative_jes_effect_with_btag,
                str(vbfRatioGGH),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            formula_VBF = "(1-0.2*@0*{})*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioVBF),
                cumulative_jes_effect_with_btag,
                str(vbfRatioVBF),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )

        return formula_ggH, formula_VBF

    # Example usage within the class
    # datacard = datacardClass()
    # frac_VBF, frac_ggH = datacard.setup_signal_fractions()
    # rfvSigRate_ggH, rfvSigRate_VBF = datacard.calculate_signal_rates(frac_VBF, frac_ggH)

    def calculate_signal_rates(self, signal_type):
        # Debugging output
        logger.debug("Calculating signal rates for {}".format(signal_type))

        # Open the ROOT file for the given signal type
        file_path = "SigEff/2l2q_Efficiency_spin0_{}_{}.root".format(signal_type, self.year)
        accxeff_file = ROOT.TFile(file_path)
        logger.debug("Opened file: {}".format(file_path))

        # Extract acceptance x efficiency for various tagging categories
        categories = ["vbf-tagged", "b-tagged", "untagged"]

        accxeff = {"{}_accxeff_{}".format(signal_type, cat): accxeff_file.Get("spin0_{}_{}_{}".format(signal_type, self.channel, cat)).GetListOfFunctions().First().Eval(self.mH) for cat in categories}
        logger.debug("Acc x Eff for {}: {}".format(signal_type, accxeff))

        # Calculate ratios
        vbf_ratio = accxeff[signal_type + "_accxeff_vbf-tagged"] / (accxeff[signal_type + "_accxeff_untagged"] + accxeff[signal_type + "_accxeff_b-tagged"])
        btag_ratio = (
            accxeff[signal_type + "_accxeff_b-tagged"] / accxeff[signal_type + "_accxeff_untagged"] if accxeff[signal_type + "_accxeff_untagged"] != 0 else 0
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

    def setup_zjets_background(self): # NOTUSED:
        """This function is not used in the current implementation. It is kept for reference purposes.
        """
        # Step 1: Load necessary inputs
        p0p0_cov_zjets = theInputs["p0p0_cov_zjets"]
        p0p1_cov_zjets = theInputs["p0p1_cov_zjets"]
        p0l0_cov_zjets = theInputs["p0l0_cov_zjets"]
        p0l1_cov_zjets = theInputs["p0l1_cov_zjets"]

        p1p0_cov_zjets = theInputs["p0p1_cov_zjets"]
        p1p1_cov_zjets = theInputs["p1p1_cov_zjets"]
        p1l0_cov_zjets = theInputs["l0p1_cov_zjets"]
        p1l1_cov_zjets = theInputs["p1l1_cov_zjets"]

        l0p0_cov_zjets = theInputs["p0l0_cov_zjets"]
        l0p1_cov_zjets = theInputs["l0p1_cov_zjets"]
        l0l0_cov_zjets = theInputs["l0l0_cov_zjets"]
        l0l1_cov_zjets = theInputs["l0l1_cov_zjets"]

        l1p0_cov_zjets = theInputs["p0l1_cov_zjets"]
        l1p1_cov_zjets = theInputs["p1l1_cov_zjets"]
        l1l0_cov_zjets = theInputs["l0l1_cov_zjets"]
        l1l1_cov_zjets = theInputs["l1l1_cov_zjets"]

        # Step 2: Setup covariance matrix based on the category and jet type
        if self.cat == "untagged" and self.jetType == "resolved":
            cov_elements = [p0p0_cov_zjets, p0l0_cov_zjets, p0p1_cov_zjets, p0l1_cov_zjets, l0p0_cov_zjets, l0l0_cov_zjets, l0p1_cov_zjets, l0l1_cov_zjets, p1p0_cov_zjets, p1l0_cov_zjets, p1p1_cov_zjets, p1l1_cov_zjets, l1p0_cov_zjets, l1l0_cov_zjets, l1p1_cov_zjets, l1l1_cov_zjets]
            n = 4
        else:
            cov_elements = [p0p0_cov_zjets, p0l0_cov_zjets, l0p0_cov_zjets, l0l0_cov_zjets]
            n = 2

        cov = ROOT.TMatrixDSym(n, array("d", cov_elements))

        # Step 3: Eigen decomposition
        eigen = ROOT.TMatrixDSymEigen(cov)
        vecs = eigen.GetEigenVectors()
        vals = eigen.GetEigenValues()

        # Step 4: Define nuisance parameters
        # nuisances without correlation that would control Z+jets spectrum (shape and normalization)
        eigVars = []
        for i in range(n):
            eigName = "eig{}_{}_{}_{}".format(i, self.jetType, self.cat, self.year)
            eigRooRealVar = ROOT.RooRealVar(eigName, eigName, 0, -3, 3)
            eigRooRealVar.setConstant(True)
            eigVars.append(eigRooRealVar)

    def calculate_background_rates_vz(self):
        """
        Calculate and return background rates for various processes based on the histograms provided in self.background_hists.
        """
        # Integral calculations for background histograms
        bkgRate_vz_Shape = {
            "untagged": self.background_hists["vz_untagged_template"].Integral(),
            "btagged": self.background_hists["vz_btagged_template"].Integral(),
            "vbftagged": self.background_hists["vz_vbftagged_template"].Integral(),
        }

        # Ratios for normalization
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

        # Determine the correct background rate and formula based on category and jet type
        cat_suffix = (
            self.cat_tree if self.cat_tree in ["untagged", "btagged", "vbftagged"] else "untagged"
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

        logger.debug("bkg_vz_norm: {}".format(rfvSigRate_vz.Print("v")))
        logger.debug("bkg_vz_norm: {}".format(rfvSigRate_vz.getVal()))
        # return rfvSigRate_vz


if __name__ == "__main__":
    try:
        year = 2018
        debug_mode = True
        datacard = datacardClass(year, DEBUG=debug_mode)
        mh = 1000  # Example Higgs mass
        is2D = True
        outputDir = "output"
        inputs ={'CMS_zz2l2q_mean_m_err': 0.001, 'all': False, 'useCMS_zz2l2q_sigma': False, 'p1l1_cov_zjets': 0.0, 'CMS_zz2l2q_sigma_e_err': -999.9, 'vzBTAGHigh': -999.9, 'useQCDscale_VV': False, 'useQCDscale_ggH': True, 'vbfBTAGLow': -999.9, 'usePdf_qqbar': True, 'useQCDscale_qqH': False, 'vzBTAGLow': -999.9, 'l1_alt_zjets': 0.01, 'usePdf_gg': True, 'useAk4SplitJEC': False, 'muonFullUnc': 0.04, 'useCMS_zz2lJ_sigma': True, 'p0p0_cov_zjets': 0.851754, 'useCMS_zz2l2q_sigMELA': True, 'useQCDscale_vz': True, 'gghJESHigh': -999.9, 'decayChannel': 'mumuqq_Merged', 'p1_alt_zjets': 0.0, 'CMS_zz2l2q_sigma_m_err': 0.2, 'p0_zjets': 4.15831, 'CMS_zz2l2q_mean_e_err': -999.9, 'lumiUnc': '1.015', 'p1p1_cov_zjets': 0.0, 'vbfBTAGHigh': -999.9, 'vzJESHigh': -999.9, 'RelBal': {'ttbar': '1.0602409638554218/0.963855421686747', 'ggH': '1.0092806138288908/0.9913513992992415', 'vz': '1.0296916634944804/0.9699276741530263', 'qqH': '1.0117738623567596/0.9891865933629198'}, 'l0p1_cov_zjets': 0.0, 'useAk8SplitJEC': True, 'EC2_year': {'ttbar': '1.0/1.0', 'ggH': '1.0/1.0', 'vz': '1.0/1.0', 'qqH': '1.0/1.0'}, 'BBEC1_year': {'ttbar': '1.0281124497991967/0.9678714859437751', 'ggH': '1.0091364704838781/0.9913957510977071', 'vz': '1.0177007993909402/0.977540921202893', 'qqH': '1.0117241836126383/0.9857090812744254'}, 'vbfJESHigh': -999.9, 'FlavQCD': {'ttbar': '1.0682730923694779/0.9357429718875502', 'ggH': '1.0099015390074066/0.9903867476826186', 'vz': '1.0285496764370003/0.9600304529881994', 'qqH': '1.0112605153341723/0.988408293038352'}, 'l1_zjets': 0.01, 'l1l1_cov_zjets': 0.0, 'p1_zjets': 0.0, 'CMS_zz2lJ_sigma_J_err': 0.1, 'lumi': 59.83, 'gghJESLow': -999.9, 'sqrts': 13.0, 'elecFullUnc': -999.9, 'useBRhiggs_hzz2l2q': True, 'zjets': True, 'BBEC1': {'ttbar': '1.0281124497991967/0.9678714859437751', 'ggH': '1.0091364704838781/0.9913957510977071', 'vz': '1.0177007993909402/0.977540921202893', 'qqH': '1.0117241836126383/0.9857090812744254'}, 'CMS_zz2l2q_sigma_j_err': -999.9, 'elecTrigUnc': -999.9, 'CMS_zz2l2q_mean_j_err': -999.9, 'EC2': {'ttbar': '1.0/1.0', 'ggH': '1.0/1.0', 'vz': '1.0/1.0', 'qqH': '1.0/1.0'}, 'zjetsAlphaHigh': 1.05, 'CMS_zz2lJ_mean_J_err': 0.01, 'p0_alt_zjets': 3.37123, 'cat': 'b_tagged', 'l0l1_cov_zjets': 0.0, 'l0_alt_zjets': 0.0031966, 'RelSample_year': {'ttbar': '1.0963855421686748/0.9236947791164658', 'ggH': '1.0159777353971704/0.9837672417616534', 'vz': '1.0622382946326607/0.9497525694708794', 'qqH': '1.0184308140690204/0.9786878187719414'}, 'p0l0_cov_zjets': 0.000850882, 'vbfJESLow': -999.9, 'p0p1_cov_zjets': 0.0, 'useCMS_zz2lJ_mean': True, 'Abs': {'ttbar': '1.0642570281124497/0.9477911646586346', 'ggH': '1.0194593515767065/0.9824034239588415', 'vz': '1.0439665017129807/0.950513894175866', 'qqH': '1.024706895409684/0.9730244419421077'}, 'useTheoryUncXS_HighMH': True, 'useCMS_zz2l2q_mean': False, 'vz': True, 'HF': {'ttbar': '1.0/1.0', 'ggH': '1.0/1.0', 'vz': '1.0/1.0', 'qqH': '1.0/1.0'}, 'usePdf_hzz2l2q_accept': True, 'useCMS_hzz2l2q_Zjets': True, 'useCMS_zz2l2q_bkgMELA': True, 'gghBTAGLow': -999.9, 'zjetsAlphaLow': 0.95, 'useLumiUnc': True, 'ttbar': True, 'l0_zjets': 0.0036055, 'muonTrigUnc': 0.0075, 'vzJESLow': -999.9, 'p0l1_cov_zjets': 0.0, 'l0l0_cov_zjets': 8.98777e-07, 'gghBTAGHigh': -999.9, 'Abs_year': {'ttbar': '1.0602409638554218/0.9477911646586346', 'ggH': '1.017241761653435/0.9844325187386348', 'vz': '1.042063189950514/0.9554625047582794', 'qqH': '1.0200867722063987/0.977727363052262'}, 'useCMS_eff': True, 'qqH': True, 'ggH': True, 'HF_year': {'ttbar': '1.0/1.0', 'ggH': '1.0/1.0', 'vz': '1.0/1.0', 'qqH': '1.0/1.0'}, 'model': 'SM'}
        category = "b_tagged"
        fracVBF = 0.1
        datacard.makeCardsWorkspaces(mh, is2D, outputDir, inputs, category, fracVBF, SanityCheckPlot=True)
    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
