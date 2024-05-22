#! /usr/bin/env python
import ROOT  # type: ignore

ROOT.gROOT.SetBatch(True)
import math
import sys
from array import array
from decimal import *
from subprocess import *

from inputReader import *
from systematicsClass import *
from utils import *

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

    def setup_parameters(self):
        # Parameters for the analysis
        self.low_M = 0
        self.high_M = 4000
        self.bins = int((self.high_M - self.low_M) / 10)
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

    def getTH1F(self, name, fs=None, category=None):
        histName = None
        if fs is None and category is None:
            histName = name
        else:
            histName = name + "_" + fs + "_" + category
        logger.debug("histName: {}".format(histName))
        hist = ROOT.TH1F(histName, histName, self.bins, self.low_M, self.high_M)
        return hist

    def save_hisograms(self, hist, template=None, output_file_name=None):
        c1 = ROOT.TCanvas("c1", "c1", 800, 800)
        hist.SetLineColor(ROOT.kRed)
        hist.SetMarkerColor(ROOT.kRed)
        hist.Draw()

        legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
        legend.AddEntry(hist, "smoothed", "l")

        if template is not None:
            template.SetLineColor(ROOT.kBlue)
            template.SetMarkerColor(ROOT.kBlue)
            template.Draw("same")
            legend.AddEntry(template, "template", "l")

        legend.Draw()
        if output_file_name is None:
            output_file_name = hist.GetName() + ".png"
        c1.SaveAs(output_file_name)

    def create_up_down_hist(self, hist):
        # list of histograms, one for each bin
        up_hist_list = []
        down_hist_list = []

        for i in range(0, hist.GetNbinsX()):
            if hist.GetBinContent(i) < 1:
                up_hist = hist.Clone()
                down_hist = hist.Clone()
                up_hist.SetName(hist.GetName() + "_" + str(i) + "_up")
                up_hist.SetTitle(hist.GetTitle() + "_" + str(i) + "_up")
                down_hist.SetName(hist.GetName() + "_" + str(i) + "_down")
                down_hist.SetTitle(hist.GetTitle() + "_" + str(i) + "_down")

                if hist.GetBinContent(i) == 0.0:
                    up_hist.SetBinContent(i, 0.000001)
                    down_hist.SetBinContent(i, 0)
                else:
                    up_hist.SetBinContent(
                        i, hist.GetBinContent(i) + hist.GetBinErrorUp(i)
                    )
                    down_hist.SetBinContent(
                        i, max(0.0, hist.GetBinContent(i) - hist.GetBinErrorLow(i))
                    )

                up_hist_list.append(up_hist)
                down_hist_list.append(down_hist)

        return up_hist_list, down_hist_list

    def plot_rooDataHist(self, data_list, mass_var):
        """
        Plot a list of RooDataHist objects on a frame and save the plot as a PNG and PDF file.

        Parameters:
        data_list (list): A list of RooDataHist objects to plot.
        mass_var (RooRealVar): The mass variable for the x-axis of the plot.
        """
        canvas = ROOT.TCanvas("canvas", "canvas", 800, 800)
        canvas.cd()
        legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)

        # Create a frame for the plot
        frame = mass_var.frame(ROOT.RooFit.Range(self.low_M, self.high_M))

        # Plot each data histogram on the frame and add it to the legend
        for i, data_hist in enumerate(data_list):
            data_hist.plotOn(
                frame,
                ROOT.RooFit.MarkerColor(i + 1),
                ROOT.RooFit.LineColor(i + 1),
                ROOT.RooFit.Name(data_hist.GetName()),
            )
            legend.AddEntry(data_hist, data_hist.GetName(), "l")

        frame.Draw()
        legend.Draw()

        # Save the plot as a PNG and PDF file
        fig_name = "{0}/figs/mzz_mH{1}_{2}_{3}".format(
            self.outputDir, self.mH, self.year, self.appendName
        )
        canvas.SaveAs(fig_name + ".png")
        canvas.SaveAs(fig_name + ".pdf")

        # Also save a logY version of the plot
        frame.SetMinimum(0.00001)
        canvas.SetLogy()
        canvas.SaveAs(fig_name + "_logY.png")
        canvas.SaveAs(fig_name + "_logY.pdf")
        del canvas

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
        self.mH = theMH
        self.lumi = theInputs["lumi"]
        self.sqrts = theInputs["sqrts"]
        self.channel = theInputs["decayChannel"]
        self.is2D = theis2D
        self.outputDir = theOutputDir
        self.sigMorph = True  # theInputs['useCMS_zz2l2q_sigMELA']
        self.bkgMorph = True  # theInputs['useCMS_zz2l2q_bkgMELA']
        self.cat = theCat
        self.FracVBF = theFracVBF
        self.SanityCheckPlot = SanityCheckPlot
        logger.debug("self.channel: {}".format(self.channel))
        logger.debug("is2D = {}".format(self.is2D))

        self.jetType = "resolved"
        if "Merged" in self.channel or "merged" in self.channel:
            self.jetType = "merged"

        logger.error(
            "channel: {}, cat: {}, jetType: {}".format(
                self.channel, self.cat, self.jetType
            )
        )
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

        fs = "2e"
        if self.channel == self.ID_2muResolved:
            fs = "2mu"
        if self.channel == self.ID_2muMerged:
            fs = "2mu"
        postfix = self.channel
        postfix = postfix + "_"
        postfix = postfix + self.cat
        self.appendName = postfix
        logger.debug("Appending name is channel + cat:  {}".format(postfix))

        self.cat_tree = "untagged"
        if self.cat == "b_tagged":
            self.cat_tree = "btagged"
        if self.cat == "vbf_tagged":
            self.cat_tree = "vbftagged"

        self.all_chan = theInputs["all"]
        self.ggH_chan = theInputs["ggH"]
        self.qqH_chan = theInputs["qqH"]
        self.vz_chan = theInputs["vz"]
        self.zjets_chan = theInputs["zjets"]
        self.ttbar_chan = theInputs["ttbar"]

        self.LUMI = ROOT.RooRealVar(
            "LUMI_{0:.0f}_{1}".format(self.sqrts, self.year),
            "LUMI_{0:.0f}_{1}".format(self.sqrts, self.year),
            self.lumi,
        )
        self.LUMI.setConstant(True)

        self.MH = ROOT.RooRealVar("MH", "MH", self.mH)
        self.MH.setConstant(True)

        ## ---------------- SET PLOTTING STYLE ---------------- ##
        ROOT.setTDRStyle(True)
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetPadLeftMargin(0.16)

        ## ------------------------- SYSTEMATICS CLASSES ----------------------------- ##

        ## systematic uncertainty for Xsec X BR, no uncertainies on signal PDF/QCD scale
        systematics = systematicsClass(
            self.mH, True, theInputs, self.year, self.DEBUG
        )  # the second argument is for the systematic unc. coming from XSxBR

        mzz_name = "zz2l2q_mass"
        zz2l2q_mass = ROOT.RooRealVar(mzz_name, mzz_name, self.low_M, self.high_M)
        zz2l2q_mass.setBins(self.bins)

        if self.jetType == "merged":
            zz2l2q_mass.SetName("zz2lJ_mass")
            zz2l2q_mass.SetTitle("zz2lJ_mass")

        # INFO: Set fullsignalrange as 25% of the mass window around the Higgs mass
        zz2l2q_mass.setRange("fullrange", self.low_M, self.high_M)
        zz2l2q_mass.setRange(
            "fullsignalrange", self.mH - 0.25 * self.mH, self.mH + 0.25 * self.mH
        )

        ## -------------------------- SIGNAL SHAPE ----------------------------------- ##

        ## -------- Variable Definitions -------- ##
        ## e
        name = "CMS_zz2l2q_mean_e_sig"
        mean_e_sig = ROOT.RooRealVar(name, "mzz_mean_e_sig", 0.0, -5.0, 5.0)
        mean_e_sig.setVal(0.0)
        ## resolution
        name = "CMS_zz2l2q_sigma_e_sig"
        sigma_e_sig = ROOT.RooRealVar(name, "mzz_sigma_e_sig", 0.0, -5.0, 5.0)
        sigma_e_sig.setVal(0.0)
        ## m
        name = "CMS_zz2l2q_mean_m_sig"
        mean_m_sig = ROOT.RooRealVar(name, "mzz_mean_m_sig", 0.0, -5.0, 5.0)
        mean_m_sig.setVal(0.0)
        ## resolution
        name = "CMS_zz2l2q_sigma_m_sig"
        sigma_m_sig = ROOT.RooRealVar(name, "mzz_sigma_m_sig", 0.0, -5.0, 5.0)
        sigma_m_sig.setVal(0.0)
        ## resolved jet JES JER
        name = "CMS_zz2l2q_mean_j_sig"
        mean_j_sig = ROOT.RooRealVar(name, "mzz_mean_j_sig", 0.0, -5.0, 5.0)
        mean_j_sig.setVal(0.0)
        ## resolution
        name = "CMS_zz2l2q_sigma_j_sig"
        sigma_j_sig = ROOT.RooRealVar(name, "mzz_sigma_j_sig", 0.0, -5.0, 5.0)
        sigma_j_sig.setVal(0.0)
        ## merged jet JEC JER
        name = "CMS_zz2lJ_mean_J_sig"
        mean_J_sig = ROOT.RooRealVar(name, "mzz_mean_J_sig", 0.0, -5.0, 5.0)
        mean_J_sig.setVal(0.0)
        ## resolution
        name = "CMS_zz2lJ_sigma_J_sig"
        sigma_J_sig = ROOT.RooRealVar(name, "mzz_sigma_J_sig", 0.0, -5.0, 5.0)
        sigma_J_sig.setVal(0.0)

        ########################
        ## JES lepton scale uncertainty
        name = "mean_m_err"
        mean_m_err = ROOT.RooRealVar(
            name, name, float(theInputs["CMS_zz2l2q_mean_m_err"])
        )
        name = "mean_e_err"
        mean_e_err = ROOT.RooRealVar(
            name, name, float(theInputs["CMS_zz2l2q_mean_e_err"])
        )
        name = "mean_j_err"
        mean_j_err = ROOT.RooRealVar(
            name, name, float(theInputs["CMS_zz2l2q_mean_j_err"])
        )
        name = "mean_J_err"
        mean_J_err = ROOT.RooRealVar(
            name, name, float(theInputs["CMS_zz2lJ_mean_J_err"])
        )
        ###
        ## resolution uncertainty
        name = "sigma_m_err"
        sigma_m_err = ROOT.RooRealVar(
            name, name, float(theInputs["CMS_zz2l2q_sigma_m_err"])
        )
        logger.debug("{}: {}".format(name, sigma_m_err.getVal()))
        name = "sigma_e_err"
        sigma_e_err = ROOT.RooRealVar(
            name, name, float(theInputs["CMS_zz2l2q_sigma_e_err"])
        )
        logger.debug("{}: {}".format(name, sigma_e_err.getVal()))
        name = "sigma_j_err"
        sigma_j_err = ROOT.RooRealVar(
            name, name, float(theInputs["CMS_zz2l2q_sigma_j_err"])
        )
        logger.debug("{}: {}".format(name, sigma_j_err.getVal()))
        name = "sigma_J_err"
        sigma_J_err = ROOT.RooRealVar(
            name, name, float(theInputs["CMS_zz2lJ_sigma_J_err"])
        )
        logger.debug("{}: {}".format(name, sigma_J_err.getVal()))

        logger.info(
            "Read signal parameters from file: {}".format(
                "Resolution/2l2q_resolution_" + self.jetType + "_" + self.year + ".root"
            )
        )
        ggHshape = ROOT.TFile(
            "Resolution/2l2q_resolution_" + self.jetType + "_" + self.year + ".root"
        )
        VBFshape = ROOT.TFile(
            "Resolution/2l2q_resolution_" + self.jetType + "_" + self.year + ".root"
        )

        # mean (bias) of DCB
        # MOREINFO: Did not understand why we get the bias from the mean of the gaussian then again obtain the mean of the DCB by adding the bias to the mean of the gaussian?
        name = "bias_ggH_" + (self.channel)
        bias_ggH = ROOT.RooRealVar(
            name,
            name,
            ggHshape.Get("mean").GetListOfFunctions().First().Eval(self.mH) - self.mH,
        )
        name = "mean_ggH_" + (self.channel)
        mean_ggH = ROOT.RooFormulaVar(name, "@0+@1", ROOT.RooArgList(self.MH, bias_ggH))

        name = "bias_VBF_" + (self.channel)
        bias_VBF = ROOT.RooRealVar(
            name,
            name,
            VBFshape.Get("mean").GetListOfFunctions().First().Eval(self.mH) - self.mH,
        )
        name = "mean_VBF_" + (self.channel)
        mean_VBF = ROOT.RooFormulaVar(name, "@0+@1", ROOT.RooArgList(self.MH, bias_VBF))

        mean_err = ROOT.RooFormulaVar()
        name = "mean_err_" + (self.channel)
        if self.channel == self.ID_2eResolved:
            mean_err = ROOT.RooFormulaVar(
                name,
                "(@0*@1*@3 + @0*@2*@4)/2",
                ROOT.RooArgList(
                    self.MH, mean_e_sig, mean_j_sig, mean_e_err, mean_j_err
                ),
            )
        elif self.channel == self.ID_2eMerged:
            mean_err = ROOT.RooFormulaVar(
                name,
                "(@0*@1*@3 + @0*@2*@4)/2",
                ROOT.RooArgList(
                    self.MH, mean_e_sig, mean_J_sig, mean_e_err, mean_J_err
                ),
            )
        elif self.channel == self.ID_2muResolved:
            mean_err = ROOT.RooFormulaVar(
                name,
                "(@0*@1*@3 + @0*@2*@4)/2",
                ROOT.RooArgList(
                    self.MH, mean_m_sig, mean_j_sig, mean_m_err, mean_j_err
                ),
            )
        elif self.channel == self.ID_2muMerged:
            mean_err = ROOT.RooFormulaVar(
                name,
                "(@0*@1*@3 + @0*@2*@4)/2",
                ROOT.RooArgList(
                    self.MH, mean_m_sig, mean_J_sig, mean_m_err, mean_J_err
                ),
            )
        logger.debug("{}: {}".format(name, mean_err.getVal()))

        name = "rfv_mean_ggH_" + (self.channel)
        rfv_mean_ggH = ROOT.RooFormulaVar(
            name, "@0+@1", ROOT.RooArgList(mean_ggH, mean_err)
        )
        name = "rfv_mean_VBF_" + (self.channel)
        rfv_mean_VBF = ROOT.RooFormulaVar(
            name, "@0+@1", ROOT.RooArgList(mean_VBF, mean_err)
        )
        logger.debug("{}: {}".format("Mean ggH", rfv_mean_ggH.getVal()))
        logger.debug("{}: {}".format("Mean VBF", rfv_mean_VBF.getVal()))

        # sigma of DCB
        name = "sigma_ggH_" + (self.channel)
        sigma_ggH = ROOT.RooRealVar(
            name,
            name,
            (ggHshape.Get("sigma")).GetListOfFunctions().First().Eval(self.mH),
        )
        name = "sigma_VBF_" + (self.channel)
        sigma_VBF = ROOT.RooRealVar(
            name,
            name,
            (VBFshape.Get("sigma")).GetListOfFunctions().First().Eval(self.mH),
        )

        rfv_sigma_SF = ROOT.RooFormulaVar()
        name = "sigma_SF_" + (self.channel)
        if self.channel == self.ID_2muResolved:  # FIXME: How we get the number 0.05?
            rfv_sigma_SF = ROOT.RooFormulaVar(
                name,
                "TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))",
                ROOT.RooArgList(sigma_m_sig, sigma_j_sig, sigma_m_err, sigma_j_err),
            )
        if self.channel == self.ID_2eResolved:
            rfv_sigma_SF = ROOT.RooFormulaVar(
                name,
                "TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))",
                ROOT.RooArgList(sigma_e_sig, sigma_j_sig, sigma_e_err, sigma_j_err),
            )
        if self.channel == self.ID_2muMerged:
            rfv_sigma_SF = ROOT.RooFormulaVar(
                name,
                "TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))",
                ROOT.RooArgList(sigma_m_sig, sigma_J_sig, sigma_m_err, sigma_J_err),
            )
        if self.channel == self.ID_2eMerged:
            rfv_sigma_SF = ROOT.RooFormulaVar(
                name,
                "TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))",
                ROOT.RooArgList(sigma_e_sig, sigma_J_sig, sigma_e_err, sigma_J_err),
            )

        logger.debug("{}: {}".format(name, rfv_sigma_SF.getVal()))

        ##################

        name = "rfv_sigma_ggH_" + (self.channel)
        rfv_sigma_ggH = ROOT.RooFormulaVar(
            name, "@0*@1", ROOT.RooArgList(sigma_ggH, rfv_sigma_SF)
        )
        name = "rfv_sigma_VBF_" + (self.channel)
        rfv_sigma_VBF = ROOT.RooFormulaVar(
            name, "@0*@1", ROOT.RooArgList(sigma_VBF, rfv_sigma_SF)
        )

        ## tail parameters
        name = "a1_ggH_" + (self.channel) + "_" + str(self.year)
        a1_ggH = ROOT.RooRealVar(
            name, name, (ggHshape.Get("a1")).GetListOfFunctions().First().Eval(self.mH)
        )
        name = "a2_ggH_" + (self.channel) + "_" + str(self.year)
        a2_ggH = ROOT.RooRealVar(
            name, name, (ggHshape.Get("a2")).GetListOfFunctions().First().Eval(self.mH)
        )
        name = "n1_ggH_" + (self.channel) + "_" + str(self.year)
        n1_ggH = ROOT.RooRealVar(
            name, name, (ggHshape.Get("n1")).GetListOfFunctions().First().Eval(self.mH)
        )
        name = "n2_ggH_" + (self.channel) + "_" + str(self.year)
        n2_ggH = ROOT.RooRealVar(
            name, name, (ggHshape.Get("n2")).GetListOfFunctions().First().Eval(self.mH)
        )
        ###
        name = "a1_VBF_" + (self.channel) + "_" + str(self.year)
        a1_VBF = ROOT.RooRealVar(
            name, name, (VBFshape.Get("a1")).GetListOfFunctions().First().Eval(self.mH)
        )
        name = "a2_VBF_" + (self.channel) + "_" + str(self.year)
        a2_VBF = ROOT.RooRealVar(
            name, name, (VBFshape.Get("a2")).GetListOfFunctions().First().Eval(self.mH)
        )
        name = "n1_VBF_" + (self.channel) + "_" + str(self.year)
        n1_VBF = ROOT.RooRealVar(
            name, name, (VBFshape.Get("n1")).GetListOfFunctions().First().Eval(self.mH)
        )
        name = "n2_VBF_" + (self.channel) + "_" + str(self.year)
        n2_VBF = ROOT.RooRealVar(
            name, name, (VBFshape.Get("n2")).GetListOfFunctions().First().Eval(self.mH)
        )
        logger.warning("a1_ggH: {}".format(a1_ggH.getValV()))
        logger.warning("a2_ggH: {}".format(a2_ggH.getValV()))
        logger.warning("n1_ggH: {}".format(n1_ggH.getValV()))
        logger.warning("n2_ggH: {}".format(n2_ggH.getValV()))
        logger.warning("a1_VBF: {}".format(a1_VBF.getValV()))
        logger.warning("a2_VBF: {}".format(a2_VBF.getValV()))
        logger.warning("n1_VBF: {}".format(n1_VBF.getValV()))
        logger.warning("n2_VBF: {}".format(n2_VBF.getValV()))

        ## --------------------- SHAPE FUNCTIONS ---------------------- ##

        name = "signalCB_ggH_" + (self.channel)
        logger.debug(
            "signalCB_ggH parameter: rfv_mean_ggH = {} rfv_sigma_ggH = {} a1_ggH = {} n1_ggH = {} a2_ggH = {} n2_ggH = {}".format(
                rfv_mean_ggH.getVal(),
                rfv_sigma_ggH.getVal(),
                a1_ggH.getVal(),
                n1_ggH.getVal(),
                a2_ggH.getVal(),
                n2_ggH.getVal(),
            )
        )
        signalCB_ggH = ROOT.RooDoubleCB(
            name,
            name,
            zz2l2q_mass,
            rfv_mean_ggH,
            rfv_sigma_ggH,
            a1_ggH,
            n1_ggH,
            a2_ggH,
            n2_ggH,
        )

        signalCB_ggH.Print("v")

        name = "signalCB_VBF_" + (self.channel)
        logger.debug(
            "signalCB_VBF parameter: rfv_mean_VBF = {} rfv_sigma_VBF = {} a1_VBF = {} n1_VBF = {} a2_VBF = {} n2_VBF = {}".format(
                rfv_mean_VBF.getVal(),
                rfv_sigma_VBF.getVal(),
                a1_VBF.getVal(),
                n1_VBF.getVal(),
                a2_VBF.getVal(),
                n2_VBF.getVal(),
            )
        )
        signalCB_VBF = ROOT.RooDoubleCB(
            name,
            name,
            zz2l2q_mass,
            rfv_mean_VBF,
            rfv_sigma_VBF,
            a1_VBF,
            n1_VBF,
            a2_VBF,
            n2_VBF,
        )
        signalCB_VBF.Print("v")
        logger.debug("signalCB_ggH name: {}".format(name))
        fullRangeSigRate = signalCB_ggH.createIntegral(
            ROOT.RooArgSet(zz2l2q_mass), ROOT.RooFit.Range("fullsignalrange")
        ).getVal()
        fullRangeSigRate_VBF = signalCB_VBF.createIntegral(
            ROOT.RooArgSet(zz2l2q_mass), ROOT.RooFit.Range("fullsignalrange")
        ).getVal()

        fullRangRate = signalCB_ggH.createIntegral(
            ROOT.RooArgSet(zz2l2q_mass), ROOT.RooFit.Range("fullrange")
        ).getVal()
        sigFraction = fullRangRate / fullRangeSigRate
        sigFraction = 1.0  # FIXME: Set to 1.0 for some checks
        logger.error("ggH Integral: {}".format(fullRangeSigRate))
        logger.error("VBF Integral: {}".format(fullRangeSigRate_VBF))

        logger.debug("fullRangRate: {}".format(fullRangRate))
        logger.debug("fullRangeSigRate: {}".format(fullRangeSigRate))
        # logger.warning("fraction of signal in the mass range is: {}".format(sigFraction))

        ## --------------------- BKG mZZ Templates ---------------------##

        vzTemplateMVV_Name = "hmass_"
        ttbarpluswwTemplateMVV_Name = "hmass_"
        zjetTemplateMVV_Name = "hmass_"  # add for zjet rate
        if self.jetType == "resolved" and self.cat == "vbf_tagged":
            vzTemplateMVV_Name = vzTemplateMVV_Name + "resolvedSR_VZ_perInvFb_Bin50GeV"
            ttbarpluswwTemplateMVV_Name = (
                ttbarpluswwTemplateMVV_Name + "resolvedSR_TTplusWW_perInvFb_Bin50GeV"
            )
            zjetTemplateMVV_Name = (
                zjetTemplateMVV_Name + "resolvedSR_Zjet_perInvFb_Bin50GeV"
            )  # add for zjet rate
        elif self.jetType == "resolved" and self.cat == "b_tagged":
            vzTemplateMVV_Name = vzTemplateMVV_Name + "resolvedSR_VZ_perInvFb_Bin50GeV"
            ttbarpluswwTemplateMVV_Name = (
                ttbarpluswwTemplateMVV_Name + "resolvedSR_TTplusWW_perInvFb_Bin50GeV"
            )
            zjetTemplateMVV_Name = (
                zjetTemplateMVV_Name + "resolvedSR_Zjet_perInvFb_Bin50GeV"
            )  # add for zjet rate
        elif self.jetType == "resolved" and self.cat == "untagged":
            vzTemplateMVV_Name = vzTemplateMVV_Name + "resolvedSR_VZ_perInvFb_Bin50GeV"
            ttbarpluswwTemplateMVV_Name = (
                ttbarpluswwTemplateMVV_Name + "resolvedSR_TTplusWW_perInvFb_Bin50GeV"
            )
            zjetTemplateMVV_Name = (
                zjetTemplateMVV_Name + "resolvedSR_Zjet_perInvFb_Bin50GeV"
            )  # add for zjet rate
        elif self.jetType == "merged":
            vzTemplateMVV_Name = vzTemplateMVV_Name + "mergedSR_VZ_perInvFb_Bin50GeV"
            ttbarpluswwTemplateMVV_Name = (
                ttbarpluswwTemplateMVV_Name + "mergedSR_TTplusWW_perInvFb_Bin50GeV"
            )
            zjetTemplateMVV_Name = (
                zjetTemplateMVV_Name + "mergedSR_Zjet_perInvFb_Bin50GeV"
            )  # add for zjet rate
        """
        # FIXME: # Why for merged category, we are not using the vbf-tagged, b-tagged and untagged templates?
        elif(self.jetType=='merged' and self.cat=='vbf_tagged') :
          vzTemplateMVV_Name = vzTemplateMVV_Name+"mergedSR_VZ_perInvFb_Bin50GeV"
          ttbarpluswwTemplateMVV_Name = ttbarpluswwTemplateMVV_Name+"mergedSR_TTplusWW_perInvFb_Bin50GeV"
        elif(self.jetType=='merged' and self.cat=='b_tagged') :
          vzTemplateMVV_Name = vzTemplateMVV_Name+"mergedSR_VZ_perInvFb_Bin50GeV"
          ttbarpluswwTemplateMVV_Name = ttbarpluswwTemplateMVV_Name+"mergedSR_TTplusWW_perInvFb_Bin50GeV"
        elif(self.jetType=='merged' and self.cat=='untagged') :
          vzTemplateMVV_Name = vzTemplateMVV_Name+"mergedSR_VZ_perInvFb_Bin50GeV"
          ttbarpluswwTemplateMVV_Name = ttbarpluswwTemplateMVV_Name+"mergedSR_TTplusWW_perInvFb_Bin50GeV"
        """
        # vz yields from a given fs
        logger.debug(
            "Name of Input ROOT file: templates1D/Template1D_spin0_"
            + fs
            + "_"
            + self.year
            + ".root"
        )
        TempFile_fs = ROOT.TFile(
            "templates1D/Template1D_spin0_" + fs + "_" + self.year + ".root", "READ"
        )
        # vz yields for all cats in a given channel
        logger.debug(
            "Histogram name to fetch: {}".format(
                "hmass_" + self.jetType + "SR_VZ_perInvFb_Bin50GeV"
            )
        )
        vzTemplateMVV_fs_untagged = TempFile_fs.Get(
            "hmass_" + self.jetType + "SR_VZ_perInvFb_Bin50GeV"
        )
        vzTemplateMVV_fs_btagged = TempFile_fs.Get(
            "hmass_" + self.jetType + "SRbtag_VZ_perInvFb_Bin50GeV"
        )
        vzTemplateMVV_fs_vbftagged = TempFile_fs.Get(
            "hmass_" + self.jetType + "SRvbf_VZ_perInvFb_Bin50GeV"
        )
        logger.debug(
            "vzTemplateMVV_fs_untagged.Integral() = {}".format(
                vzTemplateMVV_fs_untagged.Integral()
            )
        )
        logger.debug(
            "vzTemplateMVV_fs_btagged.Integral() = {}".format(
                vzTemplateMVV_fs_btagged.Integral()
            )
        )
        logger.debug(
            "vzTemplateMVV_fs_vbftagged.Integral() = {}".format(
                vzTemplateMVV_fs_vbftagged.Integral()
            )
        )

        ttbarTemplateMVV_fs_untagged = TempFile_fs.Get(
            "hmass_" + self.jetType + "SR_TTplusWW_perInvFb_Bin50GeV"
        )
        ttbarTemplateMVV_fs_btagged = TempFile_fs.Get(
            "hmass_" + self.jetType + "SRbtag_TTplusWW_perInvFb_Bin50GeV"
        )
        ttbarTemplateMVV_fs_vbftagged = TempFile_fs.Get(
            "hmass_" + self.jetType + "SRvbf_TTplusWW_perInvFb_Bin50GeV"
        )
        logger.debug(
            "ttbarTemplateMVV_fs_untagged.Integral() = {}".format(
                ttbarTemplateMVV_fs_untagged.Integral()
            )
        )
        logger.debug(
            "ttbarTemplateMVV_fs_btagged.Integral() = {}".format(
                ttbarTemplateMVV_fs_btagged.Integral()
            )
        )
        logger.debug(
            "ttbarTemplateMVV_fs_vbftagged.Integral() = {}".format(
                ttbarTemplateMVV_fs_vbftagged.Integral()
            )
        )

        # zjet yields for all cats in a given channel
        logger.debug("self.jetType: {}".format(self.jetType))
        zjetTemplateMVV_fs_untagged = TempFile_fs.Get(
            "hmass_" + self.jetType + "SR_Zjet_perInvFb_Bin50GeV"
        )
        zjetTemplateMVV_fs_btagged = TempFile_fs.Get(
            "hmass_" + self.jetType + "SRbtag_Zjet_perInvFb_Bin50GeV"
        )
        zjetTemplateMVV_fs_vbftagged = TempFile_fs.Get(
            "hmass_" + self.jetType + "SRvbf_Zjet_perInvFb_Bin50GeV"
        )
        logger.debug(
            "zjetTemplateMVV_fs_untagged.Integral() = {}".format(
                zjetTemplateMVV_fs_untagged.Integral()
            )
        )
        logger.debug(
            "zjetTemplateMVV_fs_btagged.Integral() = {}".format(
                zjetTemplateMVV_fs_btagged.Integral()
            )
        )
        logger.debug(
            "zjetTemplateMVV_fs_vbftagged.Integral() = {}".format(
                zjetTemplateMVV_fs_vbftagged.Integral()
            )
        )

        # smooth the templates
        vz_smooth_fs_untagged = self.getTH1F("vz", fs, "untagged")
        vz_smooth_fs_btagged = self.getTH1F("vz", fs, "btagged")
        vz_smooth_fs_vbftagged = self.getTH1F("vz", fs, "vbftagged")

        ttbar_smooth_fs_untagged = self.getTH1F("ttbar", fs, "untagged")
        ttbar_smooth_fs_btagged = self.getTH1F("ttbar", fs, "btagged")
        ttbar_smooth_fs_vbftagged = self.getTH1F("ttbar", fs, "vbftagged")

        zjet_smooth_fs_untagged = self.getTH1F("zjet", fs, "untagged")
        zjet_smooth_fs_btagged = self.getTH1F("zjet", fs, "btagged")
        zjet_smooth_fs_vbftagged = self.getTH1F("zjet", fs, "vbftagged")

        # shape from 2e+2mu
        TempFile = ROOT.TFile(
            "templates1D/Template1D_spin0_2l_{}.root".format(self.year), "READ"
        )
        logger.debug("VZ template name: {}".format(vzTemplateMVV_Name))
        logger.debug("ttbar template name: {}".format(ttbarpluswwTemplateMVV_Name))
        vzTemplateMVV = TempFile.Get(vzTemplateMVV_Name)
        ttbarTemplateMVV = TempFile.Get(ttbarpluswwTemplateMVV_Name)
        zjetTemplateMVV = TempFile.Get(zjetTemplateMVV_Name)  # add zjet template

        logger.error("zjetTemplateMVV_Name: {}".format(zjetTemplateMVV_Name))
        logger.error("zjetTemplateMVV: {}".format(zjetTemplateMVV))
        # exit()

        vzTemplateMVV_Stat_up_list, vzTemplateMVV_Stat_down_list = (
            self.create_up_down_hist(vzTemplateMVV)
        )
        # ttbarTemplateMVV_Stat_up_list, ttbarTemplateMVV_Stat_down_list =  self.create_up_down_hist(ttbarTemplateMVV)
        # zjetTemplateMVV_Stat_up_list, zjetTemplateMVV_Stat_down_list =  self.create_up_down_hist(zjetTemplateMVV)

        logger.debug(
            "Length of vzTemplateMVV_Stat_up_list: {}".format(
                len(vzTemplateMVV_Stat_up_list)
            )
        )
        # logger.debug("Length of ttbarTemplateMVV_Stat_up_list: {}".format(len(ttbarTemplateMVV_Stat_up_list)))
        # logger.debug("Length of zjetTemplateMVV_Stat_up_list: {}".format(len(zjetTemplateMVV_Stat_up_list)))

        vzTemplateName = "vz_" + self.appendName + "_" + str(self.year)
        vz_smooth = self.getTH1F(vzTemplateName)

        ttbarTemplateName = "ttbar_" + self.appendName + "_" + str(self.year)
        ttbar_smooth = self.getTH1F(ttbarTemplateName)

        zjetTemplateName = "zjet_" + self.appendName + "_" + str(self.year)
        zjet_smooth = self.getTH1F(zjetTemplateName)  # add zjet template

        # smooth the templates
        for i in range(0, self.bins):

            mVV_tmp = vz_smooth.GetBinCenter(i + 1)
            bin_width = vz_smooth.GetBinWidth(i + 1)
            logger.warning("\n\n\n")
            logger.warning("mVV_tmp: {}, bin_width: {}".format(mVV_tmp, bin_width))

            for j in range(0, vzTemplateMVV.GetXaxis().GetNbins()):

                mVV_tmp_low = vzTemplateMVV.GetXaxis().GetBinLowEdge(j + 1)
                mVV_tmp_up = vzTemplateMVV.GetXaxis().GetBinUpEdge(j + 1)
                bin_width_tmp = vzTemplateMVV.GetXaxis().GetBinWidth(j + 1)

                if mVV_tmp >= mVV_tmp_low and mVV_tmp < mVV_tmp_up:
                    logger.warning(
                        "mVV_tmp_low: {}, mVV_tmp_up: {}, bin_width_tmp: {},  (i, j): ({}, {})".format(
                            mVV_tmp_low, mVV_tmp_up, bin_width_tmp, i, j
                        )
                    )
                    logger.warning(
                        "bin width: {}, bin width tmp: {}".format(
                            bin_width, bin_width_tmp
                        )
                    )
                    logger.warning(
                        "content, scaled content: {}, {}".format(
                            vzTemplateMVV.GetBinContent(j + 1),
                            vzTemplateMVV.GetBinContent(j + 1)
                            * bin_width
                            / bin_width_tmp,
                        )
                    )

                    vz_smooth.SetBinContent(
                        i + 1,
                        vzTemplateMVV.GetBinContent(j + 1)
                        * bin_width
                        / bin_width_tmp,  # FIXME: Fix the scaling factor
                    )
                    vz_smooth.SetBinError(
                        i + 1,
                        vzTemplateMVV.GetBinError(j + 1) * bin_width / bin_width_tmp,
                    )

                    ########

                    vz_smooth_fs_untagged.SetBinContent(
                        i + 1,
                        vzTemplateMVV_fs_untagged.GetBinContent(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )
                    vz_smooth_fs_untagged.SetBinError(
                        i + 1,
                        vzTemplateMVV_fs_untagged.GetBinError(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )

                    vz_smooth_fs_btagged.SetBinContent(
                        i + 1,
                        vzTemplateMVV_fs_btagged.GetBinContent(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )
                    vz_smooth_fs_btagged.SetBinError(
                        i + 1,
                        vzTemplateMVV_fs_btagged.GetBinError(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )

                    vz_smooth_fs_vbftagged.SetBinContent(
                        i + 1,
                        vzTemplateMVV_fs_vbftagged.GetBinContent(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )
                    vz_smooth_fs_vbftagged.SetBinError(
                        i + 1,
                        vzTemplateMVV_fs_vbftagged.GetBinError(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )

                    break  # FIXME: is this break correct?
                    """
                    The break statement exits the inner loop once the corresponding bin in vzTemplateMVV is found
                    and its values are copied to vz_smooth.
                    This prevents further iterations of the inner loop, which is correct in this context
                    as each bin of vz_smooth should correspond to only one bin in vzTemplateMVV.
                    """

        ####### TTbar
        for i in range(0, self.bins):

            mVV_tmp = ttbar_smooth.GetBinCenter(i + 1)
            bin_width = ttbar_smooth.GetBinWidth(i + 1)

            for j in range(0, ttbarTemplateMVV.GetXaxis().GetNbins()):

                mVV_tmp_low = ttbarTemplateMVV.GetXaxis().GetBinLowEdge(j + 1)
                mVV_tmp_up = ttbarTemplateMVV.GetXaxis().GetBinUpEdge(j + 1)
                bin_width_tmp = ttbarTemplateMVV.GetXaxis().GetBinWidth(j + 1)

                if mVV_tmp >= mVV_tmp_low and mVV_tmp < mVV_tmp_up:
                    ttbar_smooth.SetBinContent(
                        i + 1,
                        ttbarTemplateMVV.GetBinContent(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )
                    ttbar_smooth.SetBinError(
                        i + 1,
                        ttbarTemplateMVV.GetBinError(j + 1) * bin_width / bin_width_tmp,
                    )

                    ttbar_smooth_fs_untagged.SetBinContent(
                        i + 1,
                        ttbarTemplateMVV_fs_untagged.GetBinContent(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )
                    ttbar_smooth_fs_untagged.SetBinError(
                        i + 1,
                        ttbarTemplateMVV_fs_untagged.GetBinError(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )

                    ttbar_smooth_fs_btagged.SetBinContent(
                        i + 1,
                        ttbarTemplateMVV_fs_btagged.GetBinContent(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )
                    ttbar_smooth_fs_btagged.SetBinError(
                        i + 1,
                        ttbarTemplateMVV_fs_btagged.GetBinError(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )

                    ttbar_smooth_fs_vbftagged.SetBinContent(
                        i + 1,
                        ttbarTemplateMVV_fs_vbftagged.GetBinContent(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )
                    ttbar_smooth_fs_vbftagged.SetBinError(
                        i + 1,
                        ttbarTemplateMVV_fs_vbftagged.GetBinError(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )

                    break

        ######## Zjet
        for i in range(0, self.bins):

            mVV_tmp = zjet_smooth.GetBinCenter(i + 1)
            bin_width = zjet_smooth.GetBinWidth(i + 1)

            for j in range(0, zjetTemplateMVV.GetXaxis().GetNbins()):

                mVV_tmp_low = zjetTemplateMVV.GetXaxis().GetBinLowEdge(j + 1)
                mVV_tmp_up = zjetTemplateMVV.GetXaxis().GetBinUpEdge(j + 1)
                bin_width_tmp = zjetTemplateMVV.GetXaxis().GetBinWidth(j + 1)

                if mVV_tmp >= mVV_tmp_low and mVV_tmp < mVV_tmp_up:
                    zjet_smooth.SetBinContent(
                        i + 1,
                        zjetTemplateMVV.GetBinContent(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )
                    zjet_smooth.SetBinError(
                        i + 1,
                        zjetTemplateMVV.GetBinError(j + 1) * bin_width / bin_width_tmp,
                    )

                    zjet_smooth_fs_untagged.SetBinContent(
                        i + 1,
                        zjetTemplateMVV_fs_untagged.GetBinContent(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )
                    zjet_smooth_fs_untagged.SetBinError(
                        i + 1,
                        zjetTemplateMVV_fs_untagged.GetBinError(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )

                    zjet_smooth_fs_btagged.SetBinContent(
                        i + 1,
                        zjetTemplateMVV_fs_btagged.GetBinContent(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )
                    zjet_smooth_fs_btagged.SetBinError(
                        i + 1,
                        zjetTemplateMVV_fs_btagged.GetBinError(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )

                    zjet_smooth_fs_vbftagged.SetBinContent(
                        i + 1,
                        zjetTemplateMVV_fs_vbftagged.GetBinContent(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )
                    zjet_smooth_fs_vbftagged.SetBinError(
                        i + 1,
                        zjetTemplateMVV_fs_vbftagged.GetBinError(j + 1)
                        * bin_width
                        / bin_width_tmp,
                    )

                    break
        # if option contains "R" smoothing is applied only to the bins defined in the X axis range (default is to smooth all bins) Bin contents are replaced by their smooth values. Errors (if any) are not modified. the smoothing procedure is repeated ntimes (default=1)
        # https://root.cern.ch/doc/v622/classTH1.html#a0d08651c37b622f4bcc0e1a0affefb33 information about smooth function
        vz_smooth.Smooth(300, "r")
        ttbar_smooth.Smooth(4000, "r")
        zjet_smooth.Smooth(4000, "r")
        if self.SanityCheckPlot:
            self.save_hisograms(
                vz_smooth,
                vzTemplateMVV,
                "{}/figs/vz_smoothed_{}_{}.png".format(
                    self.outputDir, self.channel, self.cat
                ),
            )
            self.save_hisograms(
                ttbar_smooth,
                ttbarTemplateMVV,
                "{}/figs/ttbar_smoothed_{}_{}.png".format(
                    self.outputDir, self.channel, self.cat
                ),
            )
            self.save_hisograms(
                zjet_smooth,
                zjetTemplateMVV,
                "{}/figs/zjet_smoothed_{}_{}.png".format(
                    self.outputDir, self.channel, self.cat
                ),
            )

        ## vz shape
        vzTempDataHistMVV = ROOT.RooDataHist(
            vzTemplateName,
            vzTemplateName,
            ROOT.RooArgList(zz2l2q_mass),
            vzTemplateMVV,  # Is there any benefit of using smooth vz_smooth instead of vzTemplateMVV?
            # This comment goes same for ttbar and zjet templates
        )

        logger.warning("====    vzTempDataHistMVV: {}    ====".format(vzTemplateName))
        vzTemplateMVV.Print("v")
        print("++++++++")
        vzTempDataHistMVV.Print("v")
        logger.warning("====    vzTempDataHistMVV: END    ====")

        bkg_vz = ROOT.RooHistPdf(
            vzTemplateName + "Pdf",
            vzTemplateName + "Pdf",
            ROOT.RooArgSet(zz2l2q_mass),
            vzTempDataHistMVV,
        )
        logger.warning("====    bkg_vz: {}    ====".format(vzTemplateName + "Pdf"))
        bkg_vz.Print("v")
        logger.warning("====    bkg_vz: END    ====")

        # create the RooHistPdf for the up and down variations availalbe in the list of up and down histograms
        bkg_vz_Stat_up_list = []
        bkg_vz_Stat_down_list = []
        for i, vzTemplateMVV_Stat_up in enumerate(vzTemplateMVV_Stat_up_list):
            vzTempDataHistMVV_Stat_up = ROOT.RooDataHist(
                vzTemplateName + "_Stat_up_Bin" + str(i),
                vzTemplateName + "_Stat_up_Bin" + str(i),
                ROOT.RooArgList(zz2l2q_mass),
                vzTemplateMVV_Stat_up,
            )
            bkg_vz_Stat_up = ROOT.RooHistPdf(
                vzTemplateName + "Pdf_Stat_up_Bin" + str(i),
                vzTemplateName + "Pdf_Stat_up_Bin" + str(i),
                ROOT.RooArgSet(zz2l2q_mass),
                vzTempDataHistMVV_Stat_up,
            )
            bkg_vz_Stat_up_list.append(bkg_vz_Stat_up)

        for i, vzTemplateMVV_Stat_down in enumerate(vzTemplateMVV_Stat_down_list):
            vzTempDataHistMVV_Stat_down = ROOT.RooDataHist(
                vzTemplateName + "_Stat_down_Bin" + str(i),
                vzTemplateName + "_Stat_down_Bin" + str(i),
                ROOT.RooArgList(zz2l2q_mass),
                vzTemplateMVV_Stat_down,
            )
            bkg_vz_Stat_down = ROOT.RooHistPdf(
                vzTemplateName + "Pdf_Stat_down_Bin" + str(i),
                vzTemplateName + "Pdf_Stat_down_Bin" + str(i),
                ROOT.RooArgSet(zz2l2q_mass),
                vzTempDataHistMVV_Stat_down,
            )
            bkg_vz_Stat_down_list.append(bkg_vz_Stat_down)

        ## ttbar shape
        ttbarTempDataHistMVV = ROOT.RooDataHist(
            ttbarTemplateName,
            ttbarTemplateName,
            ROOT.RooArgList(zz2l2q_mass),
            ttbarTemplateMVV,
        )
        bkg_ttbar = ROOT.RooHistPdf(
            ttbarTemplateName + "Pdf",
            ttbarTemplateName + "Pdf",
            ROOT.RooArgSet(zz2l2q_mass),
            ttbarTempDataHistMVV,
        )

        ## zjet shape
        zjetTempDataHistMVV = ROOT.RooDataHist(
            zjetTemplateName,
            zjetTemplateName,
            ROOT.RooArgList(zz2l2q_mass),
            zjetTemplateMVV,
        )
        bkg_zjet = ROOT.RooHistPdf(
            zjetTemplateName + "Pdf",
            zjetTemplateName + "Pdf",
            ROOT.RooArgSet(zz2l2q_mass),
            zjetTempDataHistMVV,
        )

        # JES TAG nuisances #FIXME: check if this is correct
        # JES = ROOT.RooRealVar("JES","JES",0,-3,3)
        # INFO: Update the inclusive JES with the split JES
        # Generate the nuisances based on the sources
        all_nuisances = []
        # nuisances for SplitSource
        for source in systematics.SplitSource:
            jetString = ""
            if self.jetType == "resolved":
                jetString = "j"
            elif self.jetType == "merged":
                jetString = "J"
            all_nuisances.append(
                ROOT.RooRealVar(
                    "CMS_scale_{}_{}".format(jetString, source),
                    "CMS_scale_j_{}".format(source),
                    0,
                    -2,
                    2,
                )
            )

        # nuisances for SplitSourceYears
        for source in systematics.SplitSourceYears:
            all_nuisances.append(
                ROOT.RooRealVar(
                    "CMS_scale_{}_{}_{}".format(jetString, source, self.year),
                    "CMS_scale_j_{}_{}".format(source, self.year),
                    0,
                    -2,
                    2,
                )
            )

        # Create a ROOT.RooArgList from all_nuisances
        arglist_all_JES = ROOT.RooArgList()
        for nuisance in all_nuisances:
            logger.debug(nuisance)
            arglist_all_JES.add(nuisance)

        num_jes_sources = len(arglist_all_JES)
        #  the cumulative effect of all JES sources
        cumulative_jes_effect = "+".join(
            "@{}".format(i) for i in range(num_jes_sources)
        )

        # BTAG TAG nuisance
        BTAG = ROOT.RooRealVar("BTAG_" + self.jetType, "BTAG_" + self.jetType, 0, -2, 2)
        logger.debug("BTAG roorealvar: {}".format(BTAG))
        # for lines where both JES and BTAG are used, the cumulative JES effect will start from @1 since @0 is reserved for BTAG. so add BTAG to the arglist first
        arglist_all_JES_BTAG = ROOT.RooArgList()
        arglist_all_JES_BTAG.add(BTAG)
        for nuisance in all_nuisances:
            logger.debug(nuisance.GetName())
            arglist_all_JES_BTAG.add(nuisance)

        cumulative_jes_effect_with_btag = "+".join(
            "@{}".format(i + 1) for i in range(num_jes_sources)
        )

        ## rates for vz
        # bkgRate_vz_Shape_untagged = vz_smooth_fs_untagged.Integral()*self.lumi
        # bkgRate_vz_Shape_btagged = vz_smooth_fs_btagged.Integral()*self.lumi
        # bkgRate_vz_Shape_vbftagged = vz_smooth_fs_vbftagged.Integral()*self.lumi
        bkgRate_vz_Shape_untagged = vz_smooth_fs_untagged.Integral()
        bkgRate_vz_Shape_btagged = vz_smooth_fs_btagged.Integral()
        bkgRate_vz_Shape_vbftagged = vz_smooth_fs_vbftagged.Integral()
        logger.error("bkgRate_vz_Shape_btagged: {}".format(bkgRate_vz_Shape_btagged))

        btagRatio = bkgRate_vz_Shape_btagged / bkgRate_vz_Shape_untagged
        vbfRatio = bkgRate_vz_Shape_vbftagged / (
            bkgRate_vz_Shape_untagged + bkgRate_vz_Shape_btagged
        )

        rfvSigRate_vz = ROOT.RooFormulaVar()
        bkgRate_vz_Shape = 0.0
        logger.error(
            "bkgRate_vz_Shape, bkgRate_vz_Shape_btagged: {}, {}".format(
                bkgRate_vz_Shape, bkgRate_vz_Shape_btagged
            )
        )
        if self.jetType == "resolved" and self.cat == "vbf_tagged":
            rfvSigRate_vz = ROOT.RooFormulaVar(
                "bkg_vz_norm",
                "(1+0.1*({}))".format(cumulative_jes_effect),
                arglist_all_JES,
            )
            bkgRate_vz_Shape = bkgRate_vz_Shape_vbftagged
        elif self.jetType == "resolved" and self.cat == "b_tagged":
            rfvSigRate_vz = ROOT.RooFormulaVar(
                "bkg_vz_norm",
                "(1+0.05*@0)*(1-0.1*({})*{})".format(
                    cumulative_jes_effect_with_btag, vbfRatio
                ),
                arglist_all_JES_BTAG,
            )
            bkgRate_vz_Shape = bkgRate_vz_Shape_btagged
        elif self.jetType == "resolved" and self.cat == "untagged":
            rfvSigRate_vz = ROOT.RooFormulaVar(
                "bkg_vz_norm",
                "(1-0.05*@0*{})*(1-0.1*({})*{})".format(
                    btagRatio, cumulative_jes_effect_with_btag, vbfRatio
                ),
                arglist_all_JES_BTAG,
            )
            bkgRate_vz_Shape = bkgRate_vz_Shape_untagged
        elif self.jetType == "merged" and self.cat == "vbf_tagged":
            rfvSigRate_vz = ROOT.RooFormulaVar(
                "bkg_vz_norm",
                "(1+0.1*({}))".format(cumulative_jes_effect),
                arglist_all_JES,
            )
            bkgRate_vz_Shape = bkgRate_vz_Shape_vbftagged
        elif self.jetType == "merged" and self.cat == "b_tagged":
            rfvSigRate_vz = ROOT.RooFormulaVar(
                "bkg_vz_norm",
                "(1+0.2*@0)*(1-0.1*({})*{})".format(
                    cumulative_jes_effect_with_btag, vbfRatio
                ),
                arglist_all_JES_BTAG,
            )
            bkgRate_vz_Shape = bkgRate_vz_Shape_btagged
        elif self.jetType == "merged" and self.cat == "untagged":
            rfvSigRate_vz = ROOT.RooFormulaVar(
                "bkg_vz_norm",
                "(1-0.2*@0*{})*(1-0.1*({})*{})".format(
                    btagRatio, cumulative_jes_effect_with_btag, vbfRatio
                ),
                arglist_all_JES_BTAG,
            )
            bkgRate_vz_Shape = bkgRate_vz_Shape_untagged

        logger.error(
            "bkgRate_vz_Shape, bkgRate_vz_Shape_btagged: {}, {}".format(
                bkgRate_vz_Shape, bkgRate_vz_Shape_btagged
            )
        )
        ## rates for zjet
        # bkgRate_zjet_Shape_untagged = zjet_smooth_fs_untagged.Integral()*self.lumi
        # bkgRate_zjet_Shape_btagged = zjet_smooth_fs_btagged.Integral()*self.lumi
        # bkgRate_zjet_Shape_vbftagged = zjet_smooth_fs_vbftagged.Integral()*self.lumi
        bkgRate_zjet_Shape_untagged = zjet_smooth_fs_untagged.Integral()
        bkgRate_zjet_Shape_btagged = zjet_smooth_fs_btagged.Integral()
        bkgRate_zjet_Shape_vbftagged = zjet_smooth_fs_vbftagged.Integral()

        if self.jetType == "resolved" and self.cat == "vbf_tagged":
            bkgRate_zjet_Shape = bkgRate_zjet_Shape_vbftagged
        elif self.jetType == "resolved" and self.cat == "b_tagged":
            bkgRate_zjet_Shape = bkgRate_zjet_Shape_btagged
        elif self.jetType == "resolved" and self.cat == "untagged":
            bkgRate_zjet_Shape = bkgRate_zjet_Shape_untagged
        elif self.jetType == "merged" and self.cat == "vbf_tagged":
            bkgRate_zjet_Shape = bkgRate_zjet_Shape_vbftagged
        elif self.jetType == "merged" and self.cat == "b_tagged":
            bkgRate_zjet_Shape = bkgRate_zjet_Shape_btagged
        elif self.jetType == "merged" and self.cat == "untagged":
            bkgRate_zjet_Shape = bkgRate_zjet_Shape_untagged

        if self.DEBUG:
            print("bkgRate_zjet_Shape = ", bkgRate_zjet_Shape)

        ## rates for ttbar+ww
        # bkgRate_ttbar_Shape_untagged = ttbar_smooth_fs_untagged.Integral()*self.lumi
        # bkgRate_ttbar_Shape_btagged = ttbar_smooth_fs_btagged.Integral()*self.lumi
        # bkgRate_ttbar_Shape_vbftagged = ttbar_smooth_fs_vbftagged.Integral()*self.lumi
        bkgRate_ttbar_Shape_untagged = ttbar_smooth_fs_untagged.Integral()
        bkgRate_ttbar_Shape_btagged = ttbar_smooth_fs_btagged.Integral()
        bkgRate_ttbar_Shape_vbftagged = ttbar_smooth_fs_vbftagged.Integral()
        if self.DEBUG:
            print("ttbar_smooth_fs_vbftagged = ", ttbar_smooth_fs_vbftagged.Integral())

        bkgRate_ttbar_Shape_mc = bkgRate_ttbar_Shape_untagged
        if self.cat == "b_tagged":
            bkgRate_ttbar_Shape_mc = bkgRate_ttbar_Shape_btagged
        if self.cat == "vbf_tagged":
            bkgRate_ttbar_Shape_mc = bkgRate_ttbar_Shape_vbftagged

        ttbar_MuEG_file = ROOT.TFile("CMSdata/alphaMethod_MuEG_Data_2016.root")
        channel_plus_cat = "resolvedSR"
        if self.channel == "eeqq_Resolved" or self.channel == "mumuqq_Resolved":
            channel_plus_cat = "resolvedSR"
        if self.channel == "eeqq_Merged" or self.channel == "mumuqq_Merged":
            channel_plus_cat = "mergedSR"
        if self.cat == "b_tagged":
            channel_plus_cat = channel_plus_cat + "btag"
        elif self.cat == "vbf_tagged":
            channel_plus_cat = channel_plus_cat + "vbf"

        # use emu data to get data-to-mc correction factor
        ttbar_MuEG_mc = ttbar_MuEG_file.Get(
            "hmass_" + channel_plus_cat + "_TTplusWW_emu_Bin50GeV"
        )
        ttbar_MuEG_data = ttbar_MuEG_file.Get(
            "hmass_" + channel_plus_cat + "_Data_emu_Bin50GeV"
        )
        ttbar_MuEG_WZ3LNu = ttbar_MuEG_file.Get(
            "hmass_" + channel_plus_cat + "_WZ3LNu_emu_Bin50GeV"
        )
        bkgRate_ttbar_Shape_DATAtoMC = (
            ttbar_MuEG_data.Integral("width") - ttbar_MuEG_WZ3LNu.Integral("width")
        ) / ttbar_MuEG_mc.Integral("width")

        # bkgRate_ttbar_Shape = bkgRate_ttbar_Shape_mc*bkgRate_ttbar_Shape_DATAtoMC
        bkgRate_ttbar_Shape = bkgRate_ttbar_Shape_mc
        if self.DEBUG:
            print("bkgRate_ttbar_Shape  = ", bkgRate_ttbar_Shape)

        ###################################################################
        ## Reducible backgrounds : Z+jets ################
        ###################################################################

        bkg_zjets = ROOT.RooGenericPdf()
        if self.DEBUG:
            print("zjets mass shape")

        ### cov matrix to account for shape+norm uncertainty
        p0p0_cov_zjets = theInputs["p0p0_cov_zjets"]
        p0l0_cov_zjets = theInputs["p0l0_cov_zjets"]
        p0p1_cov_zjets = theInputs["p0p1_cov_zjets"]
        p0l1_cov_zjets = theInputs["p0l1_cov_zjets"]
        l0p0_cov_zjets = theInputs["p0l0_cov_zjets"]
        p1p0_cov_zjets = theInputs["p0p1_cov_zjets"]
        l1p0_cov_zjets = theInputs["p0l1_cov_zjets"]
        ###
        l0l0_cov_zjets = theInputs["l0l0_cov_zjets"]
        l0p1_cov_zjets = theInputs["l0p1_cov_zjets"]
        l0l1_cov_zjets = theInputs["l0l1_cov_zjets"]
        p1l0_cov_zjets = theInputs["l0p1_cov_zjets"]
        l1l0_cov_zjets = theInputs["l0l1_cov_zjets"]
        ###
        p1p1_cov_zjets = theInputs["p1p1_cov_zjets"]
        p1l1_cov_zjets = theInputs["p1l1_cov_zjets"]
        l1p1_cov_zjets = theInputs["p1l1_cov_zjets"]
        ###
        l1l1_cov_zjets = theInputs["l1l1_cov_zjets"]

        ################################################################################################

        """
        xbins = [0,1,2,3,10]
        h_powheg[i] = TH1D("h_powheg_"+str(i),"h_powheg_"+str(i),len(xbins)-1,array('d',xbins))
        """
        n = 2  # only 4 parameters for resolved untagged cat
        cov_elements = []
        if self.cat == "untagged" and self.jetType == "resolved":
            cov_elements = [
                p0p0_cov_zjets,
                p0l0_cov_zjets,
                p0p1_cov_zjets,
                p0l1_cov_zjets,
                l0p0_cov_zjets,
                l0l0_cov_zjets,
                l0p1_cov_zjets,
                l0l1_cov_zjets,
                p1p0_cov_zjets,
                p1l0_cov_zjets,
                p1p1_cov_zjets,
                p1l1_cov_zjets,
                l1p0_cov_zjets,
                l1l0_cov_zjets,
                l1p1_cov_zjets,
                l1l1_cov_zjets,
            ]
            n = 4
        else:
            cov_elements = [
                p0p0_cov_zjets,
                p0l0_cov_zjets,
                l0p0_cov_zjets,
                l0l0_cov_zjets,
            ]
            n = 2

        cov = ROOT.TMatrixDSym(n, array("d", cov_elements))
        eigen = ROOT.TMatrixDSymEigen(cov)
        vecs = eigen.GetEigenVectors()
        vals = eigen.GetEigenValues()

        # nuisances without correlation that would control Z+jets spectrum (shape and normalization)
        eig0Name = "eig0_" + self.jetType + "_" + self.cat_tree + "_" + str(self.year)
        eig1Name = "eig1_" + self.jetType + "_" + self.cat_tree + "_" + str(self.year)
        eig2Name = "eig2_" + self.jetType + "_" + self.cat_tree + "_" + str(self.year)
        eig3Name = "eig3_" + self.jetType + "_" + self.cat_tree + "_" + str(self.year)

        eig0 = ROOT.RooRealVar(eig0Name, eig0Name, 0, -3, 3)
        eig1 = ROOT.RooRealVar(eig1Name, eig1Name, 0, -3, 3)
        eig2 = ROOT.RooRealVar(eig2Name, eig2Name, 0, -3, 3)
        eig3 = ROOT.RooRealVar(eig3Name, eig3Name, 0, -3, 3)

        eig0.setConstant(True)
        eig1.setConstant(True)
        eig2.setConstant(True)
        eig3.setConstant(True)

        eigCoeff0 = []
        eigCoeff1 = []
        eigCoeff2 = []
        eigCoeff3 = []

        if self.cat == "untagged" and self.jetType == "resolved":
            eigCoeff0 = [
                vecs(0, 0) * pow(vals(0), 0.5),
                vecs(0, 1) * pow(vals(1), 0.5),
                vecs(0, 2) * pow(vals(2), 0.5),
                vecs(0, 3) * pow(vals(3), 0.5),
            ]
            eigCoeff1 = [
                vecs(1, 0) * pow(vals(0), 0.5),
                vecs(1, 1) * pow(vals(1), 0.5),
                vecs(1, 2) * pow(vals(2), 0.5),
                vecs(1, 3) * pow(vals(3), 0.5),
            ]
            eigCoeff2 = [
                vecs(2, 0) * pow(vals(0), 0.5),
                vecs(2, 1) * pow(vals(1), 0.5),
                vecs(2, 2) * pow(vals(2), 0.5),
                vecs(2, 3) * pow(vals(3), 0.5),
            ]
            eigCoeff3 = [
                vecs(3, 0) * pow(vals(0), 0.5),
                vecs(3, 1) * pow(vals(1), 0.5),
                vecs(3, 2) * pow(vals(2), 0.5),
                vecs(3, 3) * pow(vals(3), 0.5),
            ]
        else:
            eigCoeff0 = [vecs(0, 0) * pow(vals(0), 0.5), vecs(0, 1) * pow(vals(1), 0.5)]
            eigCoeff1 = [vecs(1, 0) * pow(vals(0), 0.5), vecs(1, 1) * pow(vals(1), 0.5)]

        ###################################################

        p0_zjets = theInputs["p0_zjets"]
        l0_zjets = theInputs["l0_zjets"]
        p1_zjets = theInputs["p1_zjets"]
        l1_zjets = theInputs["l1_zjets"]

        p0_alt_zjets = theInputs["p0_alt_zjets"]
        l0_alt_zjets = theInputs["l0_alt_zjets"]
        p1_alt_zjets = theInputs["p1_alt_zjets"]
        l1_alt_zjets = theInputs["l1_alt_zjets"]

        ######
        p0_nominal_str = str(p0_zjets)
        l0_nominal_str = str(l0_zjets)
        p1_nominal_str = str(p1_zjets)
        l1_nominal_str = str(l1_zjets)

        p0_alt_nominal_str = str(p0_alt_zjets)
        l0_alt_nominal_str = str(l0_alt_zjets)
        p1_alt_nominal_str = str(p1_alt_zjets)
        l1_alt_nominal_str = str(l1_alt_zjets)

        ######
        p0_unc_str = ""
        l0_unc_str = ""
        p1_unc_str = ""
        l1_unc_str = ""

        if self.cat == "untagged" and self.jetType == "resolved":

            p0_unc_str = (
                "( ("
                + str(eigCoeff0[0])
                + ")*"
                + eig0Name
                + "+("
                + str(eigCoeff0[1])
                + ")*"
                + eig1Name
                + "+("
                + str(eigCoeff0[2])
                + ")*"
                + eig2Name
                + "+("
                + str(eigCoeff0[3])
                + ")*"
                + eig3Name
                + ")"
            )
            ######
            l0_unc_str = (
                "( ("
                + str(eigCoeff1[0])
                + ")*"
                + eig0Name
                + "+("
                + str(eigCoeff1[1])
                + ")*"
                + eig1Name
                + "+("
                + str(eigCoeff1[2])
                + ")*"
                + eig2Name
                + "+("
                + str(eigCoeff1[3])
                + ")*"
                + eig3Name
                + ")"
            )
            ######
            p1_unc_str = (
                "( ("
                + str(eigCoeff2[0])
                + ")*"
                + eig0Name
                + "+("
                + str(eigCoeff2[1])
                + ")*"
                + eig1Name
                + "+("
                + str(eigCoeff2[2])
                + ")*"
                + eig2Name
                + "+("
                + str(eigCoeff2[3])
                + ")*"
                + eig3Name
                + ")"
            )
            ######
            l1_unc_str = (
                "( ("
                + str(eigCoeff3[0])
                + ")*"
                + eig0Name
                + "+("
                + str(eigCoeff3[1])
                + ")*"
                + eig1Name
                + "+("
                + str(eigCoeff3[2])
                + ")*"
                + eig2Name
                + "+("
                + str(eigCoeff3[3])
                + ")*"
                + eig3Name
                + ")"
            )

        else:

            p0_unc_str = (
                "( ("
                + str(eigCoeff0[0])
                + ")*"
                + eig0Name
                + "+("
                + str(eigCoeff0[1])
                + ")*"
                + eig1Name
                + ")"
            )
            ######
            l0_unc_str = (
                "( ("
                + str(eigCoeff1[0])
                + ")*"
                + eig0Name
                + "+("
                + str(eigCoeff1[1])
                + ")*"
                + eig1Name
                + ")"
            )

        p0_str = "(" + p0_nominal_str + "+" + p0_unc_str + ")"
        ######
        l0_str = "(" + l0_nominal_str + "+" + l0_unc_str + ")"
        ######
        p1_str = "(" + p1_nominal_str + "+" + p1_unc_str + ")"
        ######
        l1_str = "(" + l1_nominal_str + "+" + l1_unc_str + ")"

        if self.DEBUG:
            print("p0 ", p0_str)
        if self.DEBUG:
            print("l0 ", l0_str)
        if self.DEBUG:
            print("p1 ", p1_str)
        if self.DEBUG:
            print("l1 ", l1_str)

        ##################################################

        cat = self.cat
        if self.cat == "b_tagged":
            cat = "btagged"
        if self.cat == "vbf_tagged":
            cat = "vbftagged"

        if self.DEBUG:
            print("cat ", cat)
        if self.DEBUG:
            print("jetType ", self.jetType)
        if self.cat == "untagged" and self.jetType == "resolved":
            bkg_zjets_TString = (
                "TMath::Exp("
                + p0_str
                + "-"
                + l0_str
                + "*zz2l2q_mass)+TMath::Exp("
                + p1_str
                + "-"
                + l1_str
                + "*zz2l2q_mass)"
            )
            bkg_zjets = ROOT.RooGenericPdf(
                "bkg_zjets_" + self.jetType + "_" + cat,
                bkg_zjets_TString,
                ROOT.RooArgList(zz2l2q_mass, eig0, eig1, eig2, eig3),
            )
        elif self.cat != "untagged" and self.jetType == "resolved":
            bkg_zjets_TString = "TMath::Exp(" + p0_str + "-" + l0_str + "*zz2l2q_mass)"
            bkg_zjets = ROOT.RooGenericPdf(
                "bkg_zjets_" + self.jetType + "_" + cat,
                bkg_zjets_TString,
                ROOT.RooArgList(zz2l2q_mass, eig0, eig1),
            )
        elif self.jetType == "merged":
            bkg_zjets_TString = "TMath::Exp(" + p0_str + "-" + l0_str + "*zz2lJ_mass)"
            bkg_zjets = ROOT.RooGenericPdf(
                "bkg_zjets_" + self.jetType + "_" + cat,
                bkg_zjets_TString,
                ROOT.RooArgList(zz2l2q_mass, eig0, eig1),
            )
        if self.DEBUG:
            print("bkg_zjets_TString ", bkg_zjets_TString)
        if self.DEBUG:
            print("bkg_zjets ", bkg_zjets)
        #########################################
        ## Zjets norm ################
        #########################################

        BrZee_zjets_Shape = 0.432581
        if self.jetType == "resolved" and self.cat == "untagged":
            BrZee_zjets_Shape = 0.4212420
        if self.jetType == "resolved" and self.cat == "b_tagged":
            BrZee_zjets_Shape = 0.3905356
        if self.jetType == "resolved" and self.cat == "vbf_tagged":
            BrZee_zjets_Shape = 0.4073305
        if self.jetType == "merged" and self.cat == "untagged":
            BrZee_zjets_Shape = 0.4272461
        if self.jetType == "merged" and self.cat == "b_tagged":
            BrZee_zjets_Shape = 0.4695593
        if self.jetType == "merged" and self.cat == "vbf_tagged":
            BrZee_zjets_Shape = 0.3931084
        #############################################
        BrZll_zjets_Shape = BrZee_zjets_Shape
        if self.channel == "mumuqq_Merged" or self.channel == "mumuqq_Resolved":
            BrZll_zjets_Shape = 1 - BrZll_zjets_Shape

        bkgRate_zjets_TString = ""
        if self.cat == "untagged" and self.jetType == "resolved":
            bkgRate_zjets_TString = (
                "( (1/"
                + l0_str
                + ")*(TMath::Exp("
                + p0_str
                + "-"
                + l0_str
                + "*"
                + str(self.low_M)
                + ")-TMath::Exp("
                + p0_str
                + "-"
                + l0_str
                + "*"
                + str(self.high_M)
                + ") ) + (1/"
                + l1_str
                + ")*(TMath::Exp("
                + p1_str
                + "-"
                + l1_str
                + "*"
                + str(self.low_M)
                + ")-TMath::Exp("
                + p1_str
                + "-"
                + l1_str
                + "*"
                + str(self.high_M)
                + ") ) )/50"
            )
        else:
            bkgRate_zjets_TString = (
                "( (1/"
                + l0_str
                + ")*(TMath::Exp("
                + p0_str
                + "-"
                + l0_str
                + "*"
                + str(self.low_M)
                + ")-TMath::Exp("
                + p0_str
                + "-"
                + l0_str
                + "*"
                + str(self.high_M)
                + ") ) )/50"
            )

        #### only for debug, make sure zjets rate is correct
        bkg_zjets_nomial_TF1_TString = ""
        if self.cat == "untagged" and self.jetType == "resolved":
            bkg_zjets_nomial_TF1_TString = (
                "exp("
                + str(p0_zjets)
                + "-"
                + str(l0_zjets)
                + "*x)/50 + exp("
                + str(p1_zjets)
                + "-"
                + str(l1_zjets)
                + "*x)/50"
            )
        else:
            bkg_zjets_nomial_TF1_TString = (
                "exp(" + str(p0_zjets) + "-" + str(l0_zjets) + "*x)/50"
            )

        #####
        bkgRate_zjets_TF1 = ROOT.TF1(
            "bkgRate_zjets_TF1",
            "(" + bkg_zjets_nomial_TF1_TString + ")",
            self.low_M,
            self.high_M,
        )
        bkgRate_zjets_Shape = bkgRate_zjets_TF1.Integral(self.low_M, self.high_M)

        rfvSigRate_zjets = ROOT.RooFormulaVar()
        if self.cat == "untagged" and self.jetType == "resolved":
            rfvSigRate_zjets = ROOT.RooFormulaVar(
                "bkg_zjets_norm",
                bkgRate_zjets_TString,
                ROOT.RooArgList(eig0, eig1, eig2, eig3),
            )
        else:
            rfvSigRate_zjets = ROOT.RooFormulaVar(
                "bkg_zjets_norm", bkgRate_zjets_TString, ROOT.RooArgList(eig0, eig1)
            )

        if self.DEBUG:
            print(
                "Debug rfvSigRate_zjets from TF1 ",
                bkgRate_zjets_Shape,
                " from Rfv ",
                rfvSigRate_zjets.getVal(),
            )

        ##### the final number for zjets rate into datacard
        bkgRate_zjets_Shape = BrZll_zjets_Shape
        bkgRate_zjets_Shape = bkgRate_zjet_Shape
        if self.DEBUG:
            print("Debug bkgRate_zjets_Shape ", bkgRate_zjets_Shape)

        ## --------------------------- MELA 2D PDFS ------------------------- ##

        discVarName = "Dspin0"  # To read from input file

        templateSigName = "templates2D/2l2q_spin0_template_{}.root".format(self.year)
        templateSigNameUp = "templates2D/2l2q_spin0_template_{}.root".format(self.year)
        templateSigNameDn = "templates2D/2l2q_spin0_template_{}.root".format(self.year)

        sigTempFile = ROOT.TFile(templateSigName)
        sigTempFileUp = ROOT.TFile(templateSigNameUp)
        sigTempFileDn = ROOT.TFile(templateSigNameDn)
        TString_sig = "sig_resolved"
        if self.channel == "mumuqq_Merged" or self.channel == "eeqq_Merged":
            TString_sig = "sig_merged"

        sigTemplate = sigTempFile.Get(TString_sig)
        sigTemplate_Up = sigTempFileUp.Get(TString_sig + "_up")
        sigTemplate_Down = sigTempFileDn.Get(TString_sig + "_dn")
        if self.DEBUG:
            print("templateSigName ", templateSigName)

        dBins = sigTemplate.GetYaxis().GetNbins()
        dLow = sigTemplate.GetYaxis().GetXmin()
        dHigh = sigTemplate.GetYaxis().GetXmax()
        D = ROOT.RooRealVar(discVarName, discVarName, dLow, dHigh)
        D.setBins(dBins)
        if self.DEBUG:
            print(
                "discVarName ",
                discVarName,
                " dLow ",
                dLow,
                " dHigh ",
                dHigh,
                " dBins ",
                dBins,
            )

        TemplateName = "sigTempDataHist_" + TString_sig + "_" + str(self.year)
        sigTempDataHist = ROOT.RooDataHist(
            TemplateName, TemplateName, ROOT.RooArgList(zz2l2q_mass, D), sigTemplate
        )
        TemplateName = "sigTempDataHist_" + TString_sig + "_Up" + "_" + str(self.year)
        sigTempDataHist_Up = ROOT.RooDataHist(
            TemplateName, TemplateName, ROOT.RooArgList(zz2l2q_mass, D), sigTemplate_Up
        )
        TemplateName = "sigTempDataHist_" + TString_sig + "_Down" + "_" + str(self.year)
        sigTempDataHist_Down = ROOT.RooDataHist(
            TemplateName,
            TemplateName,
            ROOT.RooArgList(zz2l2q_mass, D),
            sigTemplate_Down,
        )
        TemplateName = "sigTemplatePdf_ggH_" + TString_sig + "_" + str(self.year)
        sigTemplatePdf_ggH = ROOT.RooHistPdf(
            TemplateName, TemplateName, ROOT.RooArgSet(zz2l2q_mass, D), sigTempDataHist
        )
        TemplateName = (
            "sigTemplatePdf_ggH_" + TString_sig + "_Up" + "_" + str(self.year)
        )
        sigTemplatePdf_ggH_Up = ROOT.RooHistPdf(
            TemplateName,
            TemplateName,
            ROOT.RooArgSet(zz2l2q_mass, D),
            sigTempDataHist_Up,
        )
        TemplateName = (
            "sigTemplatePdf_ggH_" + TString_sig + "_Down" + "_" + str(self.year)
        )
        sigTemplatePdf_ggH_Down = ROOT.RooHistPdf(
            TemplateName,
            TemplateName,
            ROOT.RooArgSet(zz2l2q_mass, D),
            sigTempDataHist_Down,
        )

        TemplateName = "sigTemplatePdf_VBF_" + TString_sig + "_" + str(self.year)
        sigTemplatePdf_VBF = ROOT.RooHistPdf(
            TemplateName, TemplateName, ROOT.RooArgSet(zz2l2q_mass, D), sigTempDataHist
        )
        TemplateName = (
            "sigTemplatePdf_VBF_" + TString_sig + "_Up" + "_" + str(self.year)
        )
        sigTemplatePdf_VBF_Up = ROOT.RooHistPdf(
            TemplateName,
            TemplateName,
            ROOT.RooArgSet(zz2l2q_mass, D),
            sigTempDataHist_Up,
        )
        TemplateName = (
            "sigTemplatePdf_VBF_" + TString_sig + "_Down" + "_" + str(self.year)
        )
        sigTemplatePdf_VBF_Down = ROOT.RooHistPdf(
            TemplateName,
            TemplateName,
            ROOT.RooArgSet(zz2l2q_mass, D),
            sigTempDataHist_Down,
        )

        funcList_ggH = ROOT.RooArgList()
        funcList_VBF = ROOT.RooArgList()

        funcList_ggH.add(sigTemplatePdf_ggH)
        funcList_VBF.add(sigTemplatePdf_VBF)

        if self.sigMorph:
            funcList_ggH.add(sigTemplatePdf_ggH_Up)
            funcList_ggH.add(sigTemplatePdf_ggH_Down)
            funcList_VBF.add(sigTemplatePdf_VBF_Up)
            funcList_VBF.add(sigTemplatePdf_VBF_Down)

        # FIXME: Check if sig/bkg MELA should be correlated or uncorrelated
        morphSigVarName = "CMS_zz2l2q_sigMELA_" + self.jetType
        alphaMorphSig = ROOT.RooRealVar(morphSigVarName, morphSigVarName, 0, -2, 2)
        if self.sigMorph:
            alphaMorphSig.setConstant(False)
        else:
            alphaMorphSig.setConstant(True)

        morphVarListSig = ROOT.RooArgList()
        if self.sigMorph:
            morphVarListSig.add(
                alphaMorphSig
            )  ## just one morphing for all signal processes

        true = True
        TemplateName = "sigTemplateMorphPdf_ggH_" + TString_sig + "_" + str(self.year)
        sigTemplateMorphPdf_ggH = ROOT.FastVerticalInterpHistPdf2D(
            TemplateName,
            TemplateName,
            zz2l2q_mass,
            D,
            true,
            funcList_ggH,
            morphVarListSig,
            1.0,
            1,
        )
        sigTemplateMorphPdf_ggH.Print("v")

        TemplateName = "sigTemplateMorphPdf_VBF_" + TString_sig + "_" + str(self.year)
        sigTemplateMorphPdf_VBF = ROOT.FastVerticalInterpHistPdf2D(
            TemplateName,
            TemplateName,
            zz2l2q_mass,
            D,
            true,
            funcList_VBF,
            morphVarListSig,
            1.0,
            1,
        )

        ##### 2D -> mzz + Djet
        name = "sigCB2d_ggH" + "_" + str(self.year)
        print("ram===========")
        logger.error("Printing the signalCB_ggH")
        signalCB_ggH.Print("v")
        # signalCB_VBF.Print("v")

        logger.error("Printing the sigTemplateMorphPdf_ggH")
        sigTemplateMorphPdf_ggH.Print("v")

        logger.error("Printing the D")
        D.Print("v")

        sigCB2d_ggH = ROOT.RooProdPdf(
            name,
            name,
            ROOT.RooArgSet(signalCB_ggH),
            ROOT.RooFit.Conditional(
                ROOT.RooArgSet(sigTemplateMorphPdf_ggH), ROOT.RooArgSet(D)
            ),
        )
        logger.error("Printing the sigCB2d_ggH")
        sigCB2d_ggH.Print("v")
        name = "sigCB2d_qqH" + "_" + str(self.year)
        sigCB2d_VBF = ROOT.RooProdPdf(
            name,
            name,
            ROOT.RooArgSet(signalCB_VBF),
            ROOT.RooFit.Conditional(
                ROOT.RooArgSet(sigTemplateMorphPdf_VBF), ROOT.RooArgSet(D)
            ),
        )
        print("Archana===========")
        sigCB2d_ggH.Print("v")
        print("-----------------    VBF     -----------------")
        sigCB2d_VBF.Print("v")

        ## ----------------- 2D BACKGROUND SHAPES --------------- ##
        ##### Zjets KD

        templatezjetsBkgName = "templates2D/2l2q_spin0_template_{}.root".format(
            self.year
        )
        templatezjetsBkgNameUp = "templates2D/2l2q_spin0_template_{}.root".format(
            self.year
        )
        templatezjetsBkgNameDn = "templates2D/2l2q_spin0_template_{}.root".format(
            self.year
        )

        if self.DEBUG:
            print(templatezjetsBkgName, "file used for Zjets")

        TString_bkg = "DY_resolved"
        if self.channel == "mumuqq_Merged" or self.channel == "eeqq_Merged":
            TString_bkg = "DY_merged"

        zjetsTempFile = ROOT.TFile(templatezjetsBkgName)
        zjetsTempFileUp = ROOT.TFile(templatezjetsBkgNameUp)
        zjetsTempFileDn = ROOT.TFile(templatezjetsBkgNameDn)
        zjetsTemplate = zjetsTempFile.Get(TString_bkg)
        zjetsTemplate_Up = zjetsTempFile.Get(TString_bkg + "_up")
        zjetsTemplate_Down = zjetsTempFile.Get(TString_bkg + "_dn")

        TemplateName = "zjetsTempDataHist_" + TString_bkg + "_" + str(self.year)
        zjetsTempDataHist = ROOT.RooDataHist(
            TemplateName, TemplateName, ROOT.RooArgList(zz2l2q_mass, D), zjetsTemplate
        )
        TemplateName = "zjetsTempDataHist_" + TString_bkg + "_Up" + "_" + str(self.year)
        zjetsTempDataHist_Up = ROOT.RooDataHist(
            TemplateName,
            TemplateName,
            ROOT.RooArgList(zz2l2q_mass, D),
            zjetsTemplate_Up,
        )
        TemplateName = (
            "zjetsTempDataHist_" + TString_bkg + "_Down" + "_" + str(self.year)
        )
        zjetsTempDataHist_Down = ROOT.RooDataHist(
            TemplateName,
            TemplateName,
            ROOT.RooArgList(zz2l2q_mass, D),
            zjetsTemplate_Down,
        )

        TemplateName = "zjetsTemplatePdf_" + TString_bkg + "_" + str(self.year)
        bkgTemplatePdf_zjets = ROOT.RooHistPdf(
            TemplateName,
            TemplateName,
            ROOT.RooArgSet(zz2l2q_mass, D),
            zjetsTempDataHist,
        )
        TemplateName = "zjetsTemplatePdf_" + TString_bkg + "_Up" + "_" + str(self.year)

        bkgTemplatePdf_zjets_Up = ROOT.RooHistPdf(
            TemplateName,
            TemplateName,
            ROOT.RooArgSet(zz2l2q_mass, D),
            zjetsTempDataHist_Up,
        )
        TemplateName = (
            "zjetsTemplatePdf_" + TString_bkg + "_Down" + "_" + str(self.year)
        )
        bkgTemplatePdf_zjets_Down = ROOT.RooHistPdf(
            TemplateName,
            TemplateName,
            ROOT.RooArgSet(zz2l2q_mass, D),
            zjetsTempDataHist_Down,
        )

        ### TTbar KD
        TString_bkg = "TTbar_resolved"
        if self.channel == "mumuqq_Merged" or self.channel == "eeqq_Merged":
            TString_bkg = "TTbar_merged"

        ttbarTempFile = ROOT.TFile(templatezjetsBkgName)
        ttbarTempFileUp = ROOT.TFile(templatezjetsBkgNameUp)
        ttbarTempFileDn = ROOT.TFile(templatezjetsBkgNameDn)
        ttbarTemplate = ttbarTempFile.Get(TString_bkg)
        ttbarTemplate_Up = ttbarTempFileUp.Get(TString_bkg + "_up")
        ttbarTemplate_Down = ttbarTempFileDn.Get(TString_bkg + "_dn")

        TemplateName = "ttbarTempDataHist_" + TString_bkg + "_" + str(self.year)
        ttbarTempDataHist = ROOT.RooDataHist(
            TemplateName, TemplateName, ROOT.RooArgList(zz2l2q_mass, D), ttbarTemplate
        )
        TemplateName = "ttbarTempDataHist_" + TString_bkg + "_Up" + "_" + str(self.year)
        ttbarTempDataHist_Up = ROOT.RooDataHist(
            TemplateName,
            TemplateName,
            ROOT.RooArgList(zz2l2q_mass, D),
            ttbarTemplate_Up,
        )
        TemplateName = (
            "ttbarTempDataHist_" + TString_bkg + "_Down" + "_" + str(self.year)
        )
        ttbarTempDataHist_Down = ROOT.RooDataHist(
            TemplateName,
            TemplateName,
            ROOT.RooArgList(zz2l2q_mass, D),
            ttbarTemplate_Down,
        )

        TemplateName = "ttbarTemplatePdf_" + TString_bkg + "_" + str(self.year)
        bkgTemplatePdf_ttbar = ROOT.RooHistPdf(
            TemplateName,
            TemplateName,
            ROOT.RooArgSet(zz2l2q_mass, D),
            ttbarTempDataHist,
        )
        TemplateName = "ttbarTemplatePdf_" + TString_bkg + "_Up" + "_" + str(self.year)
        bkgTemplatePdf_ttbar_Up = ROOT.RooHistPdf(
            TemplateName,
            TemplateName,
            ROOT.RooArgSet(zz2l2q_mass, D),
            ttbarTempDataHist_Up,
        )
        TemplateName = (
            "ttbarTemplatePdf_" + TString_bkg + "_Down" + "_" + str(self.year)
        )
        bkgTemplatePdf_ttbar_Down = ROOT.RooHistPdf(
            TemplateName,
            TemplateName,
            ROOT.RooArgSet(zz2l2q_mass, D),
            ttbarTempDataHist_Down,
        )

        ### VZ KD
        TString_bkg = "Diboson_resolved"
        if self.channel == "mumuqq_Merged" or self.channel == "eeqq_Merged":
            TString_bkg = "Diboson_merged"

        vzTempFile = ROOT.TFile(templatezjetsBkgName)
        vzTempFileUp = ROOT.TFile(templatezjetsBkgNameUp)
        vzTempFileDn = ROOT.TFile(templatezjetsBkgNameDn)
        vzTemplate = vzTempFile.Get(TString_bkg)
        vzTemplate_Up = vzTempFileUp.Get(TString_bkg + "_up")
        vzTemplate_Down = vzTempFileDn.Get(TString_bkg + "_dn")

        TemplateName = "vzTempDataHist_" + TString_bkg + "_" + str(self.year)
        vzTempDataHist = ROOT.RooDataHist(
            TemplateName, TemplateName, ROOT.RooArgList(zz2l2q_mass, D), vzTemplate
        )
        TemplateName = "vzTempDataHist_" + TString_bkg + "_Up" + "_" + str(self.year)
        vzTempDataHist_Up = ROOT.RooDataHist(
            TemplateName, TemplateName, ROOT.RooArgList(zz2l2q_mass, D), vzTemplate_Up
        )
        TemplateName = "vzTempDataHist_" + TString_bkg + "_Down" + "_" + str(self.year)
        vzTempDataHist_Down = ROOT.RooDataHist(
            TemplateName, TemplateName, ROOT.RooArgList(zz2l2q_mass, D), vzTemplate_Down
        )

        TemplateName = "vzTemplatePdf_" + TString_bkg + "_" + str(self.year)
        bkgTemplatePdf_vz = ROOT.RooHistPdf(
            TemplateName, TemplateName, ROOT.RooArgSet(zz2l2q_mass, D), vzTempDataHist
        )
        TemplateName = "vzTemplatePdf_" + TString_bkg + "_Up" + "_" + str(self.year)
        bkgTemplatePdf_vz_Up = ROOT.RooHistPdf(
            TemplateName,
            TemplateName,
            ROOT.RooArgSet(zz2l2q_mass, D),
            vzTempDataHist_Up,
        )
        TemplateName = "vzTemplatePdf_" + TString_bkg + "_Down" + "_" + str(self.year)
        bkgTemplatePdf_vz_Down = ROOT.RooHistPdf(
            TemplateName,
            TemplateName,
            ROOT.RooArgSet(zz2l2q_mass, D),
            vzTempDataHist_Down,
        )

        ####
        # bkg morphing

        funcList_zjets = ROOT.RooArgList()
        funcList_ttbar = ROOT.RooArgList()
        funcList_vz = ROOT.RooArgList()
        morphBkgVarName = "CMS_zz2l2q_bkgMELA_" + self.jetType
        alphaMorphBkg = ROOT.RooRealVar(morphBkgVarName, morphBkgVarName, 0, -2, 2)
        morphVarListBkg = ROOT.RooArgList()

        if self.bkgMorph:
            funcList_zjets.add(bkgTemplatePdf_zjets)
            funcList_zjets.add(bkgTemplatePdf_zjets_Up)
            funcList_zjets.add(bkgTemplatePdf_zjets_Down)
            funcList_ttbar.add(bkgTemplatePdf_ttbar)
            funcList_ttbar.add(bkgTemplatePdf_ttbar_Up)
            funcList_ttbar.add(bkgTemplatePdf_ttbar_Down)
            funcList_vz.add(bkgTemplatePdf_vz)
            funcList_vz.add(bkgTemplatePdf_vz_Up)
            funcList_vz.add(bkgTemplatePdf_vz_Down)
            alphaMorphBkg.setConstant(False)
            morphVarListBkg.add(alphaMorphBkg)
        else:
            funcList_zjets.add(bkgTemplatePdf_zjets)
            alphaMorphBkg.setConstant(True)

        funcList_zjets.Print("v")
        TemplateName = (
            "bkgTemplateMorphPdf_zjets_" + self.jetType + "_" + str(self.year)
        )
        bkgTemplateMorphPdf_zjets = ROOT.FastVerticalInterpHistPdf2D(
            TemplateName,
            TemplateName,
            zz2l2q_mass,
            D,
            true,
            funcList_zjets,
            morphVarListBkg,
            1.0,
            1,
        )
        TemplateName = (
            "bkgTemplateMorphPdf_ttbar_" + self.jetType + "_" + str(self.year)
        )
        bkgTemplateMorphPdf_ttbar = ROOT.FastVerticalInterpHistPdf2D(
            TemplateName,
            TemplateName,
            zz2l2q_mass,
            D,
            true,
            funcList_zjets,
            morphVarListBkg,
            1.0,
            1,
        )
        TemplateName = "bkgTemplateMorphPdf_vz_" + self.jetType + "_" + str(self.year)
        bkgTemplateMorphPdf_vz = ROOT.FastVerticalInterpHistPdf2D(
            TemplateName,
            TemplateName,
            zz2l2q_mass,
            D,
            true,
            funcList_zjets,
            morphVarListBkg,
            1.0,
            1,
        )
        # get templates for stat unc
        bkgTemplateMorphPdf_vz_Stat_up_list = []
        bkgTemplateMorphPdf_vz_Stat_down_list = []
        for i in range(0, len(vzTemplateMVV_Stat_up_list)):
            name = (
                "bkgTemplateMorphPdf_vz_"
                + self.jetType
                + "_"
                + str(self.year)
                + "_Stat_up_bin{}".format(i)
            )
            bkgTemplateMorphPdf_vz_Stat_up_list.append(
                ROOT.FastVerticalInterpHistPdf2D(
                    name,
                    name,
                    zz2l2q_mass,
                    D,
                    true,
                    funcList_vz,
                    morphVarListBkg,
                    1.0,
                    1,
                )
            )
            name = (
                "bkgTemplateMorphPdf_vz_"
                + self.jetType
                + "_"
                + str(self.year)
                + "_Stat_down_bin{}".format(i)
            )
            bkgTemplateMorphPdf_vz_Stat_down_list.append(
                ROOT.FastVerticalInterpHistPdf2D(
                    name,
                    name,
                    zz2l2q_mass,
                    D,
                    true,
                    funcList_vz,
                    morphVarListBkg,
                    1.0,
                    1,
                )
            )

        #### bkg 2D : mzz + Djet;
        name = "bkg2d_zjets" + "_" + str(self.year)
        # bkg2d_zjets = ROOT.RooProdPdf(name,name,ROOT.RooArgSet(bkg_zjets),ROOT.RooFit.Conditional(ROOT.RooArgSet(bkgTemplateMorphPdf_zjets),ROOT.RooArgSet(D) ) )
        bkg2d_zjets = ROOT.RooProdPdf(
            name,
            name,
            ROOT.RooArgSet(bkg_zjet),
            ROOT.RooFit.Conditional(
                ROOT.RooArgSet(bkgTemplateMorphPdf_zjets), ROOT.RooArgSet(D)
            ),
        )  # change to bkg_zjet
        name = "bkg2d_ttbar" + "_" + str(self.year)
        bkg2d_ttbar = ROOT.RooProdPdf(
            name,
            name,
            ROOT.RooArgSet(bkg_ttbar),
            ROOT.RooFit.Conditional(
                ROOT.RooArgSet(bkgTemplateMorphPdf_ttbar), ROOT.RooArgSet(D)
            ),
        )
        name = "bkg2d_vz" + "_" + str(self.year)
        bkg2d_vz = ROOT.RooProdPdf(
            name,
            name,
            ROOT.RooArgSet(bkg_vz),
            ROOT.RooFit.Conditional(
                ROOT.RooArgSet(bkgTemplateMorphPdf_vz), ROOT.RooArgSet(D)
            ),
        )
        # bkg2d stat unctatinty using: bkg_vz_Stat_up_list, bkg_vz_Stat_down_list
        bkg2d_vz_Stat_up_list = []
        bkg2d_vz_Stat_down_list = []
        for i, bkg_vz_stat_unc_temp in enumerate(bkg_vz_Stat_up_list):
            name = "bkg2d_vz_Stat_up_bin{}_{}".format(i, self.year)
            bkg2d_vz_Stat_up_list.append(
                ROOT.RooProdPdf(
                    name,
                    name,
                    ROOT.RooArgSet(bkg_vz_stat_unc_temp),
                    ROOT.RooFit.Conditional(
                        ROOT.RooArgSet(bkgTemplateMorphPdf_vz_Stat_up_list[i]),
                        ROOT.RooArgSet(D),
                    ),
                )
            )
        for i, bkg_vz_stat_unc_temp in enumerate(bkg_vz_Stat_down_list):
            name = "bkg2d_vz_Stat_down_bin{}_{}".format(i, self.year)
            bkg2d_vz_Stat_down_list.append(
                ROOT.RooProdPdf(
                    name,
                    name,
                    ROOT.RooArgSet(bkg_vz_stat_unc_temp),
                    ROOT.RooFit.Conditional(
                        ROOT.RooArgSet(bkgTemplateMorphPdf_vz_Stat_up_list[i]),
                        ROOT.RooArgSet(D),
                    ),
                )
            )

        ## ----------------------- PLOTS FOR SANITY CHECKS -------------------------- ##
        if self.SanityCheckPlot:
            list_pdfs = {
                signalCB_ggH,
                signalCB_VBF,
                bkg_zjets,
                bkg_ttbar,
                bkg_vz,
            }
            self.plot_rooDataHist(list_pdfs, zz2l2q_mass)

        ## ----------------------- SIGNAL RATES ----------------------- ##

        sigRate_ggH_Shape = 1
        sigRate_VBF_Shape = 1

        ###########
        if self.DEBUG:
            print("signal rates")

        ggH_accxeff = ROOT.TFile(
            "SigEff/2l2q_Efficiency_spin0_ggH_{}.root".format(self.year)
        )
        VBF_accxeff = ROOT.TFile(
            "SigEff/2l2q_Efficiency_spin0_VBF_{}.root".format(self.year)
        )

        ggh_accxeff_vbf = (
            ggH_accxeff.Get("spin0_ggH_" + self.channel + "_vbf-tagged")
            .GetListOfFunctions()
            .First()
            .Eval(self.mH)
        )
        ggh_accxeff_btag = (
            ggH_accxeff.Get("spin0_ggH_" + self.channel + "_b-tagged")
            .GetListOfFunctions()
            .First()
            .Eval(self.mH)
        )
        ggh_accxeff_untag = (
            ggH_accxeff.Get("spin0_ggH_" + self.channel + "_untagged")
            .GetListOfFunctions()
            .First()
            .Eval(self.mH)
        )

        vbfRatioGGH = ggh_accxeff_vbf / (ggh_accxeff_untag + ggh_accxeff_btag)
        btagRatioGGH = (
            ggh_accxeff_btag / ggh_accxeff_untag
        )  # FIXME: Why this is not like vbf_accxeff_btag/(vbf_accxeff_untag+vbf_accxeff_btag)

        ########
        vbf_accxeff_vbf = (
            VBF_accxeff.Get("spin0_VBF_" + self.channel + "_vbf-tagged")
            .GetListOfFunctions()
            .First()
            .Eval(self.mH)
        )
        vbf_accxeff_btag = (
            VBF_accxeff.Get("spin0_VBF_" + self.channel + "_b-tagged")
            .GetListOfFunctions()
            .First()
            .Eval(self.mH)
        )
        vbf_accxeff_untag = (
            VBF_accxeff.Get("spin0_VBF_" + self.channel + "_untagged")
            .GetListOfFunctions()
            .First()
            .Eval(self.mH)
        )

        # Calculate VBF fraction, considering only untagged and b-tagged categories
        vbfRatioVBF = vbf_accxeff_vbf / (vbf_accxeff_untag + vbf_accxeff_btag)
        btagRatioVBF = vbf_accxeff_btag / vbf_accxeff_untag

        ####
        # the numbers written to the datacards
        logger.debug("self.appendName: {}".format(self.appendName))
        sigRate_ggH_Shape = (
            ggH_accxeff.Get(
                "spin0_ggH_"
                + (self.appendName)
                .replace("b_tagged", "b-tagged")
                .replace("vbf_tagged", "vbf-tagged")
            )
            .GetListOfFunctions()
            .First()
            .Eval(self.mH)
        )
        sigRate_VBF_Shape = (
            VBF_accxeff.Get(
                "spin0_VBF_"
                + (self.appendName)
                .replace("b_tagged", "b-tagged")
                .replace("vbf_tagged", "vbf-tagged")
            )
            .GetListOfFunctions()
            .First()
            .Eval(self.mH)
        )

        logger.debug("sigRate_ggH_Shape: {}".format(sigRate_ggH_Shape))
        logger.debug("sigFraction: {}".format(sigFraction))
        sigRate_ggH_Shape = sigRate_ggH_Shape * sigFraction
        sigRate_VBF_Shape = sigRate_VBF_Shape * sigFraction

        if sigRate_ggH_Shape < 0:
            sigRate_ggH_Shape = 0.0
        if sigRate_VBF_Shape < 0:
            sigRate_VBF_Shape = 0.0
        if self.DEBUG:
            print("sigFraction ", sigFraction)
        if self.DEBUG:
            print("sigRate_ggH_Shape ", sigRate_ggH_Shape)

        # VBF branching ratio
        if self.DEBUG:
            print("VBF/ggH ratio")
        # Define fraction of events coming from VBF process
        # if the self.FracVBF is -1, then set frac_VBF to float, otherwise set frac_VBF to self.FracVBF
        if self.FracVBF == -1:
            logger.info("self.FracVBF is -1, so set frac_VBF to float")
            frac_VBF = ROOT.RooRealVar("frac_VBF", "frac_VBF", vbfRatioVBF, 0.0, 1.0)
        else:
            logger.info(
                "self.FracVBF is not -1, so set frac_VBF to self.FracVBF  = {}".format(
                    self.FracVBF
                )
            )
            frac_VBF = ROOT.RooRealVar("frac_VBF", "frac_VBF", self.FracVBF, 0.0, 1.0)
            frac_VBF.setVal(self.FracVBF)
            frac_VBF.setConstant(True)

        # Define fraction of events coming from ggH process
        frac_ggH = ROOT.RooFormulaVar("frac_ggH", "(1-@0)", ROOT.RooArgList(frac_VBF))

        # Define branching ratio for ZZ->2l2q (l=e,mu) process without tau decays in signal MC
        # This value is calculated as the product of:
        # - 2: number of either Z-boson can decay to leptons or quarks and its indistinguishable partner
        # - 0.69911: branching ratio of each Z boson to decay into 2 quarks (q)
        # - 0.033662: branching ratio of Z boson to decay into 2 electrons
        # - 0.033662: branching ratio of Z boson to decay into 2 muons
        # - 2: as the Z boson can decay to either electrons or muons
        # - 1000: scaling factor used to convert the cross-section in femtobarns (fb) to the appropriate units for the analysis
        BR = ROOT.RooRealVar("BR", "BR", 2 * 0.69911 * 2 * 0.033662 * 1000)

        rfvSigRate_ggH = ROOT.RooFormulaVar()
        rfvSigRate_VBF = ROOT.RooFormulaVar()

        arglist_ggH = ROOT.RooArgList(arglist_all_JES)
        arglist_ggH.add(self.LUMI)
        arglist_ggH.add(frac_ggH)
        arglist_ggH.add(BR)

        arglist_VBF = ROOT.RooArgList(arglist_all_JES)
        arglist_VBF.add(self.LUMI)
        arglist_VBF.add(frac_VBF)
        arglist_VBF.add(BR)

        arglist_ggH_with_BTAG = ROOT.RooArgList(arglist_all_JES_BTAG)
        arglist_ggH_with_BTAG.add(self.LUMI)
        arglist_ggH_with_BTAG.add(frac_ggH)
        arglist_ggH_with_BTAG.add(BR)

        arglist_VBF_with_BTAG = ROOT.RooArgList(arglist_all_JES_BTAG)
        arglist_VBF_with_BTAG.add(self.LUMI)
        arglist_VBF_with_BTAG.add(frac_VBF)
        arglist_VBF_with_BTAG.add(BR)

        logger.debug("cumulative_jes_effect: {}".format(cumulative_jes_effect))
        logger.debug(
            "cumulative_jes_effect_with_btag: {}".format(
                cumulative_jes_effect_with_btag
            )
        )

        if self.cat == "vbf_tagged":
            formula_ggH = "(1+0.16*({}))*@{}*@{}*@{}".format(
                cumulative_jes_effect,
                num_jes_sources,
                num_jes_sources + 1,
                num_jes_sources + 2,
            )
            rfvSigRate_ggH = ROOT.RooFormulaVar(
                "ggH_hzz_norm", formula_ggH, arglist_ggH
            )

            formula_VBF = "(1+0.12*({}))*@{}*@{}*@{}".format(
                cumulative_jes_effect,
                num_jes_sources,
                num_jes_sources + 1,
                num_jes_sources + 2,
            )
            rfvSigRate_VBF = ROOT.RooFormulaVar(
                "qqH_hzz_norm", formula_VBF, arglist_VBF
            )

            # Print the RooFormulaVar using logger
            logger.debug("rfvSigRate_ggH: {}".format(rfvSigRate_ggH))
            logger.debug("rfvSigRate_VBF: {}".format(rfvSigRate_VBF))
        elif self.jetType == "resolved" and self.cat == "b_tagged":
            formula_ggH = "(1+0.04*@0)*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                cumulative_jes_effect_with_btag,
                str(vbfRatioGGH),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            rfvSigRate_ggH = ROOT.RooFormulaVar(
                "ggH_hzz_norm", formula_ggH, arglist_ggH_with_BTAG
            )

            formula_VBF = "(1+0.13*@0)*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                cumulative_jes_effect_with_btag,
                str(vbfRatioVBF),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            rfvSigRate_VBF = ROOT.RooFormulaVar(
                "qqH_hzz_norm", formula_VBF, arglist_VBF_with_BTAG
            )

            # Print the RooFormulaVar using logger
            logger.debug("rfvSigRate_ggH: {}".format(rfvSigRate_ggH))
            logger.debug("rfvSigRate_VBF: {}".format(rfvSigRate_VBF))
        elif self.jetType == "resolved" and self.cat == "untagged":
            formula_ggH = "(1-0.03*@0*{})*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioGGH),
                cumulative_jes_effect_with_btag,
                str(vbfRatioGGH),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            rfvSigRate_ggH = ROOT.RooFormulaVar(
                "ggH_hzz_norm", formula_ggH, arglist_ggH_with_BTAG
            )

            formula_VBF = "(1-0.11*@0*{})*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioVBF),
                cumulative_jes_effect_with_btag,
                str(vbfRatioVBF),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            rfvSigRate_VBF = ROOT.RooFormulaVar(
                "qqH_hzz_norm", formula_VBF, arglist_VBF_with_BTAG
            )

            # Print the RooFormulaVar using logger
            logger.debug("rfvSigRate_ggH: {}".format(rfvSigRate_ggH))
            logger.debug("rfvSigRate_VBF: {}".format(rfvSigRate_VBF))
        elif self.jetType == "merged" and self.cat == "b_tagged":
            formula_ggH = "(1+0.08*@0)*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                cumulative_jes_effect_with_btag,
                str(vbfRatioGGH),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            rfvSigRate_ggH = ROOT.RooFormulaVar(
                "ggH_hzz_norm", formula_ggH, arglist_ggH_with_BTAG
            )

            formula_VBF = "(1+0.07*@0)*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                cumulative_jes_effect_with_btag,
                str(vbfRatioVBF),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            rfvSigRate_VBF = ROOT.RooFormulaVar(
                "qqH_hzz_norm", formula_VBF, arglist_VBF_with_BTAG
            )

            # Print the RooFormulaVar using logger
            logger.debug("rfvSigRate_ggH: {}".format(rfvSigRate_ggH))
            logger.debug("rfvSigRate_VBF: {}".format(rfvSigRate_VBF))
        elif self.jetType == "merged" and self.cat == "untagged":
            formula_ggH = "(1-0.16*@0*{})*(1-0.1*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioGGH),
                cumulative_jes_effect_with_btag,
                str(vbfRatioGGH),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            rfvSigRate_ggH = ROOT.RooFormulaVar(
                "ggH_hzz_norm", formula_ggH, arglist_ggH_with_BTAG
            )

            formula_VBF = "(1-0.2*@0*{})*(1-0.05*({})*{})*@{}*@{}*@{}".format(
                str(btagRatioVBF),
                cumulative_jes_effect_with_btag,
                str(vbfRatioVBF),
                num_jes_sources + 1,
                num_jes_sources + 2,
                num_jes_sources + 3,
            )
            rfvSigRate_VBF = ROOT.RooFormulaVar(
                "qqH_hzz_norm", formula_VBF, arglist_VBF_with_BTAG
            )

            # Print the RooFormulaVar using logger
            logger.debug("rfvSigRate_ggH: {}".format(rfvSigRate_ggH))
            logger.debug("rfvSigRate_VBF: {}".format(rfvSigRate_VBF))

        if self.DEBUG:
            print(
                "Rates ggH ", rfvSigRate_ggH.getVal(), " VBF ", rfvSigRate_VBF.getVal()
            )

        logger.error(
            "channel: {}, cat: {}, jetType: {}".format(
                self.channel, self.cat, self.jetType
            )
        )
        logger.debug("Formula ggH: {}".format(formula_ggH))
        logger.debug("Formula VBF: {}".format(formula_VBF))
        for i in range(0, len(arglist_ggH_with_BTAG)):  # 0, 1, 2, 3, 4, 5
            logger.debug(
                "{:2}: arglist_ggH_with_BTAG: {}".format(
                    i, arglist_ggH_with_BTAG.at(i).GetName()
                )
            )
        for i in range(0, len(arglist_ggH_with_BTAG)):  # 0, 1, 2, 3, 4, 5
            logger.debug(
                "{:2}: arglist_ggH_with_BTAG: {}".format(
                    i, arglist_ggH_with_BTAG.at(i).GetName()
                )
            )
        for i in range(0, len(arglist_VBF)):  # 0, 1, 2, 3, 4, 5
            logger.debug("{:2}: arglist_VBF: {}".format(i, arglist_VBF.at(i).GetName()))
        for i in range(0, len(arglist_ggH)):  # 0, 1, 2, 3, 4, 5
            logger.debug("{:2}: arglist_ggH: {}".format(i, arglist_ggH.at(i).GetName()))

        ## ----------------------- BACKGROUND RATES ----------------------- ##

        # bkgRate_zjets_Shape = theInputs['zjets_rate']

        ## --------------------------- DATASET --------------------------- ##

        dataFileDir = "CMSdata"
        dataFileName = "{0}/Data_SR.root".format(dataFileDir)

        logger.debug("dataFileName: {}".format(dataFileName))
        data_obs_file = ROOT.TFile(dataFileName)

        treeName = ""
        if self.channel == "eeqq_Resolved" and self.cat == "vbf_tagged":
            treeName = "TreeSR0"
        if self.channel == "eeqq_Resolved" and self.cat == "b_tagged":
            treeName = "TreeSR1"
        if self.channel == "eeqq_Resolved" and self.cat == "untagged":
            treeName = "TreeSR2"
        if self.channel == "eeqq_Merged" and self.cat == "vbf_tagged":
            treeName = "TreeSR3"
        if self.channel == "eeqq_Merged" and self.cat == "b_tagged":
            treeName = "TreeSR4"
        if self.channel == "eeqq_Merged" and self.cat == "untagged":
            treeName = "TreeSR5"

        if self.channel == "mumuqq_Resolved" and self.cat == "vbf_tagged":
            treeName = "TreeSR6"
        if self.channel == "mumuqq_Resolved" and self.cat == "b_tagged":
            treeName = "TreeSR7"
        if self.channel == "mumuqq_Resolved" and self.cat == "untagged":
            treeName = "TreeSR8"
        if self.channel == "mumuqq_Merged" and self.cat == "vbf_tagged":
            treeName = "TreeSR9"
        if self.channel == "mumuqq_Merged" and self.cat == "b_tagged":
            treeName = "TreeSR10"
        if self.channel == "mumuqq_Merged" and self.cat == "untagged":
            treeName = "TreeSR11"

        logger.debug(
            "data_obs_file.Get(treeName): {}".format(data_obs_file.Get(treeName))
        )
        if not (data_obs_file.Get(treeName)):
            if self.DEBUG:
                print(
                    'File, "', dataFileName, '", or tree, "', treeName, '", not found'
                )
            if self.DEBUG:
                print("Exiting...")
            sys.exit()

        zz2lJ_mass_struct = zz2lJ_massStruct()
        tmpFile = ROOT.TFile(
            "tmpFile.root", "RECREATE"
        )  # This is a temporary fix. We don't need tempFile.root. But if its not there then it gives error
        data_obs_tree = (data_obs_file.Get(treeName)).CloneTree(0)
        data_obs_tree.Branch("zz2lJ_mass", zz2lJ_mass_struct, "zz2lJ_mass/D")
        logger.info("Data entries: {}".format(data_obs_file.Get(treeName).GetEntries()))
        logger.debug("zz2l2q_mass: {}".format(zz2l2q_mass))
        for i in range(0, data_obs_file.Get(treeName).GetEntries()):
            data_obs_file.Get(treeName).GetEntry(i)
            zz2lJ_mass_struct.zz2lJ_mass = data_obs_file.Get(treeName).zz2l2q_mass
            data_obs_tree.Fill()

        logger.info(
            "data_obs_tree entries for {channel}_{category}: {entries}".format(
                channel=self.channel,
                category=self.cat,
                entries=data_obs_tree.GetEntries(),
            )
        )

        data_obs = ROOT.RooDataSet()
        datasetName = "data_obs"

        if self.is2D == 0:
            data_obs = ROOT.RooDataSet(
                datasetName, datasetName, data_obs_tree, ROOT.RooArgSet(zz2l2q_mass)
            )
        if self.is2D == 1:
            data_obs = ROOT.RooDataSet(
                datasetName, datasetName, data_obs_tree, ROOT.RooArgSet(zz2l2q_mass, D)
            )

        logger.debug("data_obs: {}".format(data_obs))
        """
        print 'generate pseudo dataset'
        data_obs = ROOT.RooDataSet()
        if (self.is2D == 0):
         data_obs = signalCB_ggH.generate(ROOT.RooArgSet(zz2l2q_mass), int(bkgRate_zjets_Shape))
        if (self.is2D == 1):
         data_obs = sigCB2d_ggH.generate(ROOT.RooArgSet(zz2l2q_mass,D), int(bkgRate_zjets_Shape))
        """

        ## --------------------------- WORKSPACE -------------------------- ##
        logger.debug("prepare workspace")
        endsInP5 = False
        tmpMH = self.mH
        if math.fabs(math.floor(tmpMH) - self.mH) > 0.001:
            endsInP5 = True
        logger.debug("ENDS IN P5: {}".format(endsInP5))

        name_Shape = ""
        name_ShapeWS = ""
        name_ShapeWS2 = ""

        if endsInP5:
            name_Shape = "{0}/HCG/{1:.1f}/hzz2l2q_{2}_{3:.0f}TeV.txt".format(
                self.outputDir, self.mH, self.appendName, self.sqrts
            )
        else:
            name_Shape = "{0}/HCG/{1:.0f}/hzz2l2q_{2}_{3:.0f}TeV.txt".format(
                self.outputDir, self.mH, self.appendName, self.sqrts
            )

        if endsInP5:
            name_ShapeWS = "{0}/HCG/{1:.1f}/hzz2l2q_{2}_{3:.0f}TeV.input.root".format(
                self.outputDir, self.mH, self.appendName, self.sqrts
            )
        else:
            name_ShapeWS = "{0}/HCG/{1:.0f}/hzz2l2q_{2}_{3:.0f}TeV.input.root".format(
                self.outputDir, self.mH, self.appendName, self.sqrts
            )

        name_ShapeWS2 = "hzz2l2q_{0}_{1:.0f}TeV.input.root".format(
            self.appendName, self.sqrts
        )

        if self.DEBUG:
            print(name_Shape, "  ", name_ShapeWS2)

        w = ROOT.RooWorkspace("w", "w")
        w.importClassCode(ROOT.RooDoubleCB.Class(), True)
        w.importClassCode(ROOT.RooFormulaVar.Class(), True)
        # print everything in the workspace
        # print(w.Print("v"))
        getattr(w, "import")(
            data_obs, ROOT.RooFit.Rename("data_obs")
        )  ### Should this be renamed?
        w.Print("v")

        if self.is2D == 0:
            signalCB_ggH.SetNameTitle("ggH_hzz", "ggH_hzz")
            signalCB_VBF.SetNameTitle("qqH_hzz", "qqH_hzz")
            getattr(w, "import")(signalCB_ggH, ROOT.RooFit.RecycleConflictNodes())
            getattr(w, "import")(signalCB_VBF, ROOT.RooFit.RecycleConflictNodes())

        if self.is2D == 1:
            sigCB2d_ggH.SetNameTitle("ggH_hzz", "ggH_hzz")
            sigCB2d_VBF.SetNameTitle("qqH_hzz", "qqH_hzz")
            getattr(w, "import")(sigCB2d_ggH, ROOT.RooFit.RecycleConflictNodes())
            getattr(w, "import")(sigCB2d_VBF, ROOT.RooFit.RecycleConflictNodes())

        w.Print("v")

        if self.is2D == 0:
            bkg_vz.SetNameTitle("bkg_vz", "bkg_vz")
            bkg_ttbar.SetNameTitle("bkg_ttbar", "bkg_ttbar")
            # bkg_zjets.SetNameTitle("bkg_zjets","bkg_zjets") # FIXME: Check the difference between bkg_zjets and bkg_zjet and document it.
            bkg_zjet.SetNameTitle("bkg_zjets", "bkg_zjets")  # changed to zjet
            getattr(w, "import")(bkg_vz, ROOT.RooFit.RecycleConflictNodes())
            getattr(w, "import")(bkg_ttbar, ROOT.RooFit.RecycleConflictNodes())
            # getattr(w,'import')(bkg_zjets, ROOT.RooFit.RecycleConflictNodes())
            # print("bkg_zjet: ", bkg_zjet)
            getattr(w, "import")(bkg_zjet, ROOT.RooFit.RecycleConflictNodes())
            for i, bkg_vz_stat_temp_up in enumerate(bkg_vz_Stat_up_list):
                bkg_vz_stat_temp_up.SetNameTitle(
                    "bkg_vz_Stat_up_bin{}".format(i), "bkg_vz_Stat_up_bin{}".format(i)
                )
                getattr(w, "import")(
                    bkg_vz_stat_temp_up, ROOT.RooFit.RecycleConflictNodes()
                )
            for i, bkg_vz_stat_temp_dn in enumerate(bkg_vz_Stat_down_list):
                bkg_vz_stat_temp_dn.SetNameTitle(
                    "bkg_vz_Stat_down_bin{}".format(i),
                    "bkg_vz_Stat_down_bin{}".format(i),
                )
                getattr(w, "import")(
                    bkg_vz_stat_temp_dn, ROOT.RooFit.RecycleConflictNodes()
                )

        if self.is2D == 1:
            bkg2d_vz.SetNameTitle("bkg_vz", "bkg_vz")
            bkg2d_ttbar.SetNameTitle("bkg_ttbar", "bkg_ttbar")
            bkg2d_zjets.SetNameTitle("bkg_zjets", "bkg_zjets")
            getattr(w, "import")(bkg2d_vz, ROOT.RooFit.RecycleConflictNodes())
            getattr(w, "import")(bkg2d_ttbar, ROOT.RooFit.RecycleConflictNodes())
            getattr(w, "import")(bkg2d_zjets, ROOT.RooFit.RecycleConflictNodes())
            # print("type(bkg2d_vz)", type(bkg2d_vz))
            # print("type(bkg2d_vz_Stat_down_list[0])", type(bkg2d_vz_Stat_down_list[0]))
            # print("----------------- START PRINTING bkg2d_vz -----------------")
            # bkg2d_vz.Print("v")
            # # bkg2d_vz_Stat_down_list[0].SetNameTitle("bkg_vz_Stat_down_bin0", "bkg_vz_Stat_down_bin0")
            # # getattr(w, "import")(bkg2d_vz_Stat_down_list[0], ROOT.RooFit.RecycleConflictNodes())

        w.Print("v")
        # print(
        #     "----------------- START PRINTING bkg2d_vz_Stat_down_list -----------------"
        # )
        # # w.Print("v")
        # bkg2d_vz_Stat_down_list[0].Print("v")
        # print("----------------- END PRINTING -----------------")
        # for i, bkg_vz_stat_down in enumerate(bkg2d_vz_Stat_down_list):
        #     # bkg_vz_stat_down.Print("v") # Print the RooFormulaVar
        #     if bkg_vz_stat_down:
        #         # Checking if all components are valid
        #         components = bkg_vz_stat_down.getComponents()
        #         print("components: ", components)
        #         for comp in components:
        #             print("comp: ", comp)
        #             if not comp:  # Check if any component is None or invalid
        #                 print("Invalid component in {bkg_vz_stat_down}".format(bkg_vz_stat_down=bkg_vz_stat_down))
        #                 continue  # Skip importing this one or fix the issue before importing

        #         down_pdf_name = "bkg_vz_Stat_down_bin{i}".format(i=i)
        #         bkg_vz_stat_down.SetNameTitle(down_pdf_name, down_pdf_name)
        #         getattr(w, "import")(bkg_vz_stat_down, ROOT.RooFit.RecycleConflictNodes())
        #     else:
        #         print("Warning: Object at index {i} is None or invalid".format(i=i))
        #     exit()

        # Importing the PDF into the RooWorkspace
        # getattr(w, 'import')(bkg_vz_stat_down, ROOT.RooFit.RecycleConflictNodes())

        # print("bkg2d_vz_Stat_up_list: ", bkg2d_vz_Stat_up_list)
        # for i in range(len(bkg2d_vz_Stat_down_list)):
        # bkg2d_vz_Stat_down_list[i].SetNameTitle("bkg_vz_Stat_down_bin{}".format(i), "bkg_vz_Stat_down_bin{}".format(i))
        # getattr(w, "import")(bkg2d_vz_Stat_down_list[i], ROOT.RooFit.RecycleConflictNodes())
        # for i, bkg2d_vz_nbins in enumerate(bkg2d_vz_Stat_down_list):
        # bkg2d_vz_nbins.SetNameTitle("bkg_vz_Stat_down_bin{}".format(i), "bkg_vz_Stat_down_bin{}".format(i))
        # getattr(w, "import")(bkg2d_vz_nbins, ROOT.RooFit.RecycleConflictNodes())
        # for i, bkg2d_vz_stat_temp in enumerate(bkg2d_vz_Stat_up_list):
        #     bkg2d_vz_stat_temp.SetNameTitle("bkg_vz_Stat_up_bin{}".format(i), "bkg_vz_Stat_up_bin{}".format(i))
        #     getattr(w, "import")(bkg2d_vz_stat_temp, ROOT.RooFit.RecycleConflictNodes())
        # exit()
        # print("----------------- START PRINTING -----------------")
        # w.Print("v")
        # print("----------------- END PRINTING -----------------")

        getattr(w, "import")(rfvSigRate_ggH, ROOT.RooFit.RecycleConflictNodes())
        getattr(w, "import")(rfvSigRate_VBF, ROOT.RooFit.RecycleConflictNodes())
        # getattr(w,'import')(rfvSigRate_zjets, ROOT.RooFit.RecycleConflictNodes()) #changed to zjet
        getattr(w, "import")(rfvSigRate_vz, ROOT.RooFit.RecycleConflictNodes())
        logger.error("jetType: {}, cat: {}".format(self.jetType, self.cat))
        w.Print("v")

        zz2l2q_mass.setRange(self.low_M, self.high_M)

        w.writeToFile(name_ShapeWS)

        ## --------------------------- DATACARDS -------------------------- ##

        rates = {}
        rates["ggH"] = sigRate_ggH_Shape
        rates["qqH"] = sigRate_VBF_Shape

        rates["vz"] = bkgRate_vz_Shape
        rates["ttbar"] = bkgRate_ttbar_Shape
        rates["zjets"] = bkgRate_zjets_Shape

        logger.error(
            "Signal rates: ggH: {:.4f}, qqH: {:.4f}".format(
                sigRate_ggH_Shape, sigRate_VBF_Shape
            )
        )
        logger.error(
            "Background rates: VZ: {:.4f}, TTbar: {:.4f}, Zjets: {:.4f}\n\n".format(
                bkgRate_vz_Shape, bkgRate_ttbar_Shape, bkgRate_zjets_Shape
            )
        )
        # exit()

        ## If the channel is not declared in inputs, set rate = 0
        if not self.ggH_chan and not self.all_chan:
            sigRate_ggH_Shape = 0
        if not self.qqH_chan:
            sigRate_VBF_Shape = 0
        ## bkg
        if not self.vz_chan:
            bkgRate_vz_Shape = 0
        if not self.ttbar_chan:
            bkgRate_ttbar_Shape = 0
        if not self.zjets_chan:
            bkgRate_zjets_Shape = 0

        ## Write Datacards
        systematics.setSystematics(rates)

        fo = open(name_Shape, "wb")
        self.WriteDatacard(
            fo, theInputs, name_ShapeWS2, rates, data_obs.numEntries(), self.is2D
        )
        systematics.WriteSystematics(
            fo, theInputs, rates, int(ttbar_MuEG_data.Integral("width") / 50)
        )
        systematics.WriteShapeSystematics(fo, theInputs)
        fo.close()

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
        # channelName2D=['ggH_hzz','qqH_hzz','bkg2d_vz','bkg2d_ttbar','bkg2d_zjets']
        channelName2D = ["ggH_hzz", "qqH_hzz", "bkg_vz", "bkg_ttbar", "bkg_zjets"]
        # for i in range(0, len(bkg2d_vz_Stat_down_list)):
        #     channelName1D.append("bkg_vz_Stat_up_bin{}".format(i))
        #     channelName1D.append("bkg_vz_Stat_down_bin{}".format(i))
        #     channelName2D.append("bkg_vz_Stat_up_bin{}".format(i))
        #     channelName2D.append("bkg_vz_Stat_down_bin{}".format(i))

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

        if inputs["ggH"]:
            counter += 1
        if inputs["qqH"]:
            counter += 1

        return counter

    def numberOfBgChan(self, inputs):

        counter = 0

        if inputs["vz"]:
            counter += 1
        if inputs["zjets"]:
            counter += 1
        if inputs["ttbar"]:
            counter += 1

        return counter
