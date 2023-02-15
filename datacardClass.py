#! /usr/bin/env python
from scipy.special import erf
import ROOT
from array import array

import sys
from subprocess import *
import math
from decimal import *
from ROOT import *

from systematicsClass import *
from inputReader import *

from array import array

gROOT.ProcessLine(
   "struct zz2lJ_massStruct {\
   Double_t zz2lJ_mass;\
   };" );

from ROOT import zz2lJ_massStruct

## ------------------------------------
##  card and workspace class
## ------------------------------------

class datacardClass:

    def __init__(self,year):

        self.ID_2muResolved = 'mumuqq_Resolved'
        self.ID_2eResolved  = 'eeqq_Resolved'
        self.ID_2muMerged = 'mumuqq_Merged'
        self.ID_2eMerged  = 'eeqq_Merged'
        self.year = year

    def loadIncludes(self):

        ROOT.gSystem.AddIncludePath("-I$ROOFITSYS/include/")
        ROOT.gSystem.AddIncludePath("-Iinclude/")
        ROOT.gROOT.ProcessLine(".L include/tdrstyle.cc")
        ROOT.gSystem.Load("libRooFit")
        ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so")

    # main datacard and workspace function
    def makeCardsWorkspaces(self, theMH, theis2D, theOutputDir, theInputs, theCat, theFracVBF):

        ## --------------- SETTINGS AND DECLARATIONS --------------- ##
        DEBUG = False
        self.mH = theMH
        self.lumi = theInputs['lumi']
        self.sqrts = theInputs['sqrts']
        self.channel = theInputs['decayChannel']
        self.is2D = theis2D
        self.outputDir = theOutputDir
        self.sigMorph = True #theInputs['useCMS_zz2l2q_sigMELA']
        self.bkgMorph = True #theInputs['useCMS_zz2l2q_bkgMELA']
        self.cat = theCat
        self.FracVBF = theFracVBF

        fs="2e"
        if (self.channel == self.ID_2muResolved) :
          fs="2mu"
        if (self.channel == self.ID_2muMerged) :
          fs="2mu"
        postfix=self.channel
        postfix=postfix+'_'
        postfix=postfix+self.cat
        self.appendName = postfix
        print 'appendName is channel + cat ',postfix

        self.cat_tree = "untagged"
        if(self.cat=="b-tagged") :
          self.cat_tree = "btagged"
        if(self.cat=="vbf-tagged") :
          self.cat_tree = "vbftagged"

        self.all_chan = theInputs['all']
        self.ggH_chan = theInputs['ggH']
        self.qqH_chan = theInputs['qqH']
        self.vz_chan = theInputs['vz']
        self.zjets_chan = theInputs['zjets']
        self.ttbar_chan = theInputs['ttbar']

        self.LUMI = ROOT.RooRealVar("LUMI_{0:.0f}".format(self.sqrts),"LUMI_{0:.0f}".format(self.sqrts),self.lumi)
        self.LUMI.setConstant(True)

        self.MH = ROOT.RooRealVar("MH","MH",self.mH)
        self.MH.setConstant(True)

        self.jetType = "resolved"
        if('Merged' in self.channel or 'merged' in self.channel) :
          self.jetType = "merged"

        ## ---------------- SET PLOTTING STYLE ---------------- ##
        ROOT.setTDRStyle(True)
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetPadLeftMargin(0.16)

        ## ------------------------- SYSTEMATICS CLASSES ----------------------------- ##

        ## systematic uncertainty for Xsec X BR, no uncertainies on signal PDF/QCD scale
        systematics = systematicsClass( self.mH, True, theInputs)

        self.low_M = 300
        #if(self.channel=="eeqq_Merged" or self.channel=="mumuqq_Merged") : # if merge selected, start from 600GeV
        #if(self.jetType=="merged") :
        #  self.low_M = 700
        self.high_M = 4000
        bins = int((self.high_M-self.low_M)/10)
        mzz_name = "zz2l2q_mass"

        zz2l2q_mass = ROOT.RooRealVar(mzz_name,mzz_name,self.low_M,self.high_M)
        zz2l2q_mass.setBins(bins)

        if(self.jetType=="merged") :
          zz2l2q_mass.SetName("zz2lJ_mass")
          zz2l2q_mass.SetTitle("zz2lJ_mass")

        zz2l2q_mass.setRange("fullrange",self.low_M,self.high_M)
        zz2l2q_mass.setRange("fullsignalrange",300,4000)

        ## -------------------------- SIGNAL SHAPE ----------------------------------- ##

        ## -------- Variable Definitions -------- ##
        ## e
        name = "CMS_zz2l2q_mean_e_sig"
        mean_e_sig = ROOT.RooRealVar(name,"mzz_mean_e_sig",0.0,-5.0,5.0)
        mean_e_sig.setVal(0.0)
        ## resolution
        name = "CMS_zz2l2q_sigma_e_sig"
        sigma_e_sig = ROOT.RooRealVar(name,"mzz_sigma_e_sig",0.0,-5.0,5.0)
        sigma_e_sig.setVal(0.0)
        ## m
        name = "CMS_zz2l2q_mean_m_sig"
        mean_m_sig = ROOT.RooRealVar(name,"mzz_mean_m_sig",0.0,-5.0,5.0)
        mean_m_sig.setVal(0.0)
        ## resolution
        name = "CMS_zz2l2q_sigma_m_sig"
        sigma_m_sig = ROOT.RooRealVar(name,"mzz_sigma_m_sig",0.0,-5.0,5.0)
        sigma_m_sig.setVal(0.0)
        ## resolved jet JES JER
        name = "CMS_zz2l2q_mean_j_sig"
        mean_j_sig = ROOT.RooRealVar(name,"mzz_mean_j_sig",0.0,-5.0,5.0)
        mean_j_sig.setVal(0.0)
        ## resolution
        name = "CMS_zz2l2q_sigma_j_sig"
        sigma_j_sig = ROOT.RooRealVar(name,"mzz_sigma_j_sig",0.0,-5.0,5.0)
        sigma_j_sig.setVal(0.0)
        ## merged jet JEC JER
        name = "CMS_zz2lJ_mean_J_sig"
        mean_J_sig = ROOT.RooRealVar(name,"mzz_mean_J_sig",0.0,-5.0,5.0)
        mean_J_sig.setVal(0.0)
        ## resolution
        name = "CMS_zz2lJ_sigma_J_sig"
        sigma_J_sig = ROOT.RooRealVar(name,"mzz_sigma_J_sig",0.0,-5.0,5.0)
        sigma_J_sig.setVal(0.0)

        ########################
        ## JES lepton scale uncertainty
        name = "mean_m_err"
        mean_m_err = ROOT.RooRealVar(name,name,float(theInputs['CMS_zz2l2q_mean_m_err']))
        name = "mean_e_err"
        mean_e_err = ROOT.RooRealVar(name,name,float(theInputs['CMS_zz2l2q_mean_e_err']))
        name = "mean_j_err"
        mean_j_err = ROOT.RooRealVar(name,name,float(theInputs['CMS_zz2l2q_mean_j_err']))
        name = "mean_J_err"
        mean_J_err = ROOT.RooRealVar(name,name,float(theInputs['CMS_zz2lJ_mean_J_err']))
        ###
        ## resolution uncertainty
        name = "sigma_m_err"
        sigma_m_err = ROOT.RooRealVar(name,name,float(theInputs['CMS_zz2l2q_sigma_m_err']))
        print name,' ',sigma_m_err.getVal()
        name = "sigma_e_err"
        sigma_e_err = ROOT.RooRealVar(name,name,float(theInputs['CMS_zz2l2q_sigma_e_err']))
        print name,' ',sigma_e_err.getVal()
        name = "sigma_j_err"
        sigma_j_err = ROOT.RooRealVar(name,name,float(theInputs['CMS_zz2l2q_sigma_j_err']))
        print name,' ',sigma_j_err.getVal()
        name = "sigma_J_err"
        sigma_J_err = ROOT.RooRealVar(name,name,float(theInputs['CMS_zz2lJ_sigma_J_err']))
        print name,' ',sigma_J_err.getVal()

        print 'read signal parameters'
        ggHshape = TFile("Resolution/2l2q_resolution_"+self.jetType+"_"+self.year+".root")
        VBFshape = TFile("Resolution/2l2q_resolution_"+self.jetType+"_"+self.year+".root")

        #ggh_accxeff_vbf = ggH_accxeff.Get("spin0_ggH_"+self.channel+"_vbf-tagged").GetListOfFunctions().First().Eval(self.mH)

        # mean (bias) of DCB
        name = "bias_ggH_"+(self.channel)
        bias_ggH = ROOT.RooRealVar(name,name, ggHshape.Get("mean").GetListOfFunctions().First().Eval(self.mH)-self.mH)
        name = "mean_ggH_"+(self.channel)
        mean_ggH = ROOT.RooFormulaVar(name,"@0+@1",ROOT.RooArgList(self.MH,bias_ggH))

        name = "bias_VBF_"+(self.channel)
        bias_VBF = ROOT.RooRealVar(name,name, VBFshape.Get("mean").GetListOfFunctions().First().Eval(self.mH)-self.mH)
        name = "mean_VBF_"+(self.channel)
        mean_VBF = ROOT.RooFormulaVar(name,"@0+@1",ROOT.RooArgList(self.MH,bias_VBF))

        mean_err = ROOT.RooFormulaVar()
        name = "mean_err_"+(self.channel)
        if (self.channel == self.ID_2eResolved) :
             mean_err = ROOT.RooFormulaVar(name,"(@0*@1*@3 + @0*@2*@4)/2", ROOT.RooArgList(self.MH, mean_e_sig,mean_j_sig,mean_e_err,mean_j_err))
        elif (self.channel == self.ID_2eMerged) :
             mean_err = ROOT.RooFormulaVar(name,"(@0*@1*@3 + @0*@2*@4)/2", ROOT.RooArgList(self.MH, mean_e_sig,mean_J_sig,mean_e_err,mean_J_err))
        elif (self.channel == self.ID_2muResolved) :
             mean_err = ROOT.RooFormulaVar(name,"(@0*@1*@3 + @0*@2*@4)/2", ROOT.RooArgList(self.MH, mean_m_sig,mean_j_sig,mean_m_err,mean_j_err))
        elif (self.channel == self.ID_2muMerged) :
             mean_err = ROOT.RooFormulaVar(name,"(@0*@1*@3 + @0*@2*@4)/2", ROOT.RooArgList(self.MH, mean_m_sig,mean_J_sig,mean_m_err,mean_J_err))
        print 'mean error ', mean_err.getVal()

        name = "rfv_mean_ggH_"+self.channel
        rfv_mean_ggH = ROOT.RooFormulaVar(name,"@0+@1",ROOT.RooArgList(mean_ggH,mean_err))
        name = "rfv_mean_VBF_"+(self.channel)
        rfv_mean_VBF = ROOT.RooFormulaVar(name,"@0+@1",ROOT.RooArgList(mean_VBF,mean_err))
        print 'mean ggH ', rfv_mean_ggH.getVal(),'; mean VBF ',rfv_mean_VBF.getVal()

        # sigma of DCB
        name = "sigma_ggH_"+(self.channel)
        sigma_ggH = ROOT.RooRealVar(name,name, (ggHshape.Get("sigma")).GetListOfFunctions().First().Eval(self.mH))
        name = "sigma_VBF_"+(self.channel)
        sigma_VBF = ROOT.RooRealVar(name,name, (VBFshape.Get("sigma")).GetListOfFunctions().First().Eval(self.mH))

        rfv_sigma_SF = ROOT.RooFormulaVar()
        name = "sigma_SF_"+(self.channel)
        if (self.channel == self.ID_2muResolved) :
            rfv_sigma_SF = ROOT.RooFormulaVar(name,"TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))", ROOT.RooArgList(sigma_m_sig, sigma_j_sig, sigma_m_err,sigma_j_err))
        if (self.channel == self.ID_2eResolved) :
            rfv_sigma_SF = ROOT.RooFormulaVar(name,"TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))", ROOT.RooArgList(sigma_e_sig, sigma_j_sig, sigma_e_err,sigma_j_err))
        if (self.channel == self.ID_2muMerged) :
            rfv_sigma_SF = ROOT.RooFormulaVar(name,"TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))", ROOT.RooArgList(sigma_m_sig, sigma_J_sig, sigma_m_err,sigma_J_err))
        if (self.channel == self.ID_2eMerged) :
            rfv_sigma_SF = ROOT.RooFormulaVar(name,"TMath::Sqrt((1+0.05*@0*@2)*(1+@1*@3))", ROOT.RooArgList(sigma_e_sig, sigma_J_sig, sigma_e_err,sigma_J_err))

        print name,' ',rfv_sigma_SF.getVal()

        ##################

        name = "rfv_sigma_ggH_"+(self.channel)
        rfv_sigma_ggH = ROOT.RooFormulaVar(name,"@0*@1",ROOT.RooArgList(sigma_ggH,rfv_sigma_SF) )
        name = "rfv_sigma_VBF_"+(self.channel)
        rfv_sigma_VBF = ROOT.RooFormulaVar(name,"@0*@1",ROOT.RooArgList(sigma_VBF,rfv_sigma_SF) )

        ## tail parameters
        name = "a1_ggH_"+(self.channel)
        a1_ggH = ROOT.RooRealVar(name,name, (ggHshape.Get("a1")).GetListOfFunctions().First().Eval(self.mH))
        name = "a2_ggH_"+(self.channel)
        a2_ggH = ROOT.RooRealVar(name,name, (ggHshape.Get("a2")).GetListOfFunctions().First().Eval(self.mH))
        name = "n1_ggH_"+(self.channel)
        n1_ggH = ROOT.RooRealVar(name,name, (ggHshape.Get("n1")).GetListOfFunctions().First().Eval(self.mH))
        name = "n2_ggH_"+(self.channel)
        n2_ggH = ROOT.RooRealVar(name,name, (ggHshape.Get("n2")).GetListOfFunctions().First().Eval(self.mH))
        ###
        name = "a1_VBF_"+(self.channel)
        a1_VBF = ROOT.RooRealVar(name,name, (VBFshape.Get("a1")).GetListOfFunctions().First().Eval(self.mH))
        name = "a2_VBF_"+(self.channel)
        a2_VBF = ROOT.RooRealVar(name,name, (VBFshape.Get("a2")).GetListOfFunctions().First().Eval(self.mH))
        name = "n1_VBF_"+(self.channel)
        n1_VBF = ROOT.RooRealVar(name,name, (VBFshape.Get("n1")).GetListOfFunctions().First().Eval(self.mH))
        name = "n2_VBF_"+(self.channel)
        n2_VBF = ROOT.RooRealVar(name,name, (VBFshape.Get("n2")).GetListOfFunctions().First().Eval(self.mH))

        ## --------------------- SHAPE FUNCTIONS ---------------------- ##

        name = "signalCB_ggH_"+(self.channel)
        signalCB_ggH = ROOT.RooDoubleCB(name,name,zz2l2q_mass,rfv_mean_ggH,rfv_sigma_ggH,a1_ggH,n1_ggH,a2_ggH,n2_ggH)
        name = "signalCB_VBF_"+(self.channel)
        signalCB_VBF = ROOT.RooDoubleCB(name,name,zz2l2q_mass,rfv_mean_VBF,rfv_sigma_VBF,a1_VBF,n1_VBF,a2_VBF,n2_VBF)

        fullRangeSigRate = signalCB_ggH.createIntegral( ROOT.RooArgSet(zz2l2q_mass), ROOT.RooFit.Range("fullsignalrange") ).getVal()
        fullRangRate = signalCB_ggH.createIntegral( ROOT.RooArgSet(zz2l2q_mass), ROOT.RooFit.Range("fullrange") ).getVal()
        sigFraction = fullRangRate/fullRangeSigRate
        sigFraction = 1.0

        print 'fullRangRate ',fullRangRate
        print 'fullRangeSigRate ',fullRangeSigRate
        print 'fraction of signal in the mass range is ',sigFraction

        ## --------------------- BKG mZZ Templates ---------------------##

        vzTemplateMVV_Name = "hmass_"
        ttbarpluswwTemplateMVV_Name = "hmass_"
        if(self.jetType=='resolved' and self.cat=='vbf-tagged') :
          vzTemplateMVV_Name = vzTemplateMVV_Name+"resolvedSR_VZ_perInvFb_Bin50GeV"
          ttbarpluswwTemplateMVV_Name = ttbarpluswwTemplateMVV_Name+"resolvedSR_TTplusWW_perInvFb_Bin50GeV"
        elif(self.jetType=='resolved' and self.cat=='b-tagged') :
          vzTemplateMVV_Name = vzTemplateMVV_Name+"resolvedSR_VZ_perInvFb_Bin50GeV"
          ttbarpluswwTemplateMVV_Name = ttbarpluswwTemplateMVV_Name+"resolvedSR_TTplusWW_perInvFb_Bin50GeV"
        elif(self.jetType=='resolved' and self.cat=='untagged') :
          vzTemplateMVV_Name = vzTemplateMVV_Name+"resolvedSR_VZ_perInvFb_Bin50GeV"
          ttbarpluswwTemplateMVV_Name = ttbarpluswwTemplateMVV_Name+"resolvedSR_TTplusWW_perInvFb_Bin50GeV"
        elif(self.jetType=='merged') :
          vzTemplateMVV_Name = vzTemplateMVV_Name+"mergedSR_VZ_perInvFb_Bin50GeV"
          ttbarpluswwTemplateMVV_Name = ttbarpluswwTemplateMVV_Name+"mergedSR_TTplusWW_perInvFb_Bin50GeV"
        '''
        elif(self.jetType=='merged' and self.cat=='vbf-tagged') :
          vzTemplateMVV_Name = vzTemplateMVV_Name+"mergedSR_VZ_perInvFb_Bin50GeV"
          ttbarpluswwTemplateMVV_Name = ttbarpluswwTemplateMVV_Name+"mergedSR_TTplusWW_perInvFb_Bin50GeV"
        elif(self.jetType=='merged' and self.cat=='b-tagged') :
          vzTemplateMVV_Name = vzTemplateMVV_Name+"mergedSR_VZ_perInvFb_Bin50GeV"
          ttbarpluswwTemplateMVV_Name = ttbarpluswwTemplateMVV_Name+"mergedSR_TTplusWW_perInvFb_Bin50GeV"
        elif(self.jetType=='merged' and self.cat=='untagged') :
          vzTemplateMVV_Name = vzTemplateMVV_Name+"mergedSR_VZ_perInvFb_Bin50GeV"
          ttbarpluswwTemplateMVV_Name = ttbarpluswwTemplateMVV_Name+"mergedSR_TTplusWW_perInvFb_Bin50GeV"
        '''
        #vz yields from a given fs
        TempFile_fs = TFile("templates1D/Template1D_spin0_"+fs+"_"+self.year+".root","READ")
        #vz yields for all cats in a given channel
        vzTemplateMVV_fs_untagged = TempFile_fs.Get("hmass_"+self.jetType+"SR_VZ_perInvFb_Bin50GeV")
        vzTemplateMVV_fs_btagged = TempFile_fs.Get("hmass_"+self.jetType+"SRbtag_VZ_perInvFb_Bin50GeV")
        vzTemplateMVV_fs_vbftagged = TempFile_fs.Get("hmass_"+self.jetType+"SRvbf_VZ_perInvFb_Bin50GeV")

        ttbarTemplateMVV_fs_untagged = TempFile_fs.Get("hmass_"+self.jetType+"SR_TTplusWW_perInvFb_Bin50GeV")
        ttbarTemplateMVV_fs_btagged = TempFile_fs.Get("hmass_"+self.jetType+"SRbtag_TTplusWW_perInvFb_Bin50GeV")
        ttbarTemplateMVV_fs_vbftagged = TempFile_fs.Get("hmass_"+self.jetType+"SRvbf_TTplusWW_perInvFb_Bin50GeV")
        print "ttbarTemplateMVV_fs_vbftagged = ",ttbarTemplateMVV_fs_vbftagged.Integral()

        print "hmass_",self.jetType,"SRvbf_VZ_Bin50GeV_perInvFb"

        vz_smooth_fs_untagged = TH1F("vz_"+fs+"_untagged","vz_"+fs+"_untagged", int(self.high_M-self.low_M)/10,self.low_M,self.high_M)
        vz_smooth_fs_btagged = TH1F("vz_"+fs+"_btagged","vz_"+fs+"_btagged", int(self.high_M-self.low_M)/10,self.low_M,self.high_M)
        vz_smooth_fs_vbftagged = TH1F("vz_"+fs+"_vbftagged","vz_"+fs+"_vbftagged", int(self.high_M-self.low_M)/10,self.low_M,self.high_M)

        ttbar_smooth_fs_untagged = TH1F("ttbar_"+fs+"_untagged","vz_"+fs+"_untagged", int(self.high_M-self.low_M)/10,self.low_M,self.high_M)
        ttbar_smooth_fs_btagged = TH1F("ttbar_"+fs+"_btagged","vz_"+fs+"_btagged", int(self.high_M-self.low_M)/10,self.low_M,self.high_M)
        ttbar_smooth_fs_vbftagged = TH1F("ttbar_"+fs+"_vbftagged","vz_"+fs+"_vbftagged", int(self.high_M-self.low_M)/10,self.low_M,self.high_M)

        # shape from 2e+2mu
        TempFile = TFile("templates1D/Template1D_spin0_2l_{}.root".format(self.year),"READ")
        print 'vzTemplateMVV_Name ',vzTemplateMVV_Name
        print 'ttbarpluswwTemplateMVV_Name ',ttbarpluswwTemplateMVV_Name
        vzTemplateMVV = TempFile.Get(vzTemplateMVV_Name)
        ttbarTemplateMVV = TempFile.Get(ttbarpluswwTemplateMVV_Name)

        vzTemplateName="vz_"+self.appendName
        vz_smooth = TH1F(vzTemplateName,vzTemplateName, int(self.high_M-self.low_M)/10,self.low_M,self.high_M)
        ttbarTemplateName="ttbar_"+self.appendName
        ttbar_smooth = TH1F(ttbarTemplateName,ttbarTemplateName, int(self.high_M-self.low_M)/10,self.low_M,self.high_M)

        for i in range(0,int(self.high_M-self.low_M)/10) :

          mVV_tmp = vz_smooth.GetBinCenter(i+1)

          for j in range(0,vzTemplateMVV.GetXaxis().GetNbins()) :

            mVV_tmp_low = vzTemplateMVV.GetXaxis().GetBinLowEdge(j+1)
            mVV_tmp_up  = vzTemplateMVV.GetXaxis().GetBinUpEdge(j+1)

            if(mVV_tmp>=mVV_tmp_low and mVV_tmp<mVV_tmp_up) :

              vz_smooth.SetBinContent(i+1,vzTemplateMVV.GetBinContent(j+1)*10.0/50.0)
              vz_smooth.SetBinError(i+1,vzTemplateMVV.GetBinError(j+1)*10.0/50.0)

              ########

              vz_smooth_fs_untagged.SetBinContent(i+1,vzTemplateMVV_fs_untagged.GetBinContent(j+1)*10.0/50.0)
              vz_smooth_fs_untagged.SetBinError(i+1,vzTemplateMVV_fs_untagged.GetBinError(j+1)*10.0/50.0)

              vz_smooth_fs_btagged.SetBinContent(i+1,vzTemplateMVV_fs_btagged.GetBinContent(j+1)*10.0/50.0)
              vz_smooth_fs_btagged.SetBinError(i+1,vzTemplateMVV_fs_btagged.GetBinError(j+1)*10.0/50.0)

              vz_smooth_fs_vbftagged.SetBinContent(i+1,vzTemplateMVV_fs_vbftagged.GetBinContent(j+1)*10.0/50.0)
              vz_smooth_fs_vbftagged.SetBinError(i+1,vzTemplateMVV_fs_vbftagged.GetBinError(j+1)*10.0/50.0)

              break


        ####### TTbar
        for i in range(0,int(self.high_M-self.low_M)/10) :

         mVV_tmp = ttbar_smooth.GetBinCenter(i+1)

         for j in range(0,ttbarTemplateMVV.GetXaxis().GetNbins()) :

           mVV_tmp_low = ttbarTemplateMVV.GetXaxis().GetBinLowEdge(j+1)
           mVV_tmp_up  = ttbarTemplateMVV.GetXaxis().GetBinUpEdge(j+1)

           if(mVV_tmp>=mVV_tmp_low and mVV_tmp<mVV_tmp_up) :
             ttbar_smooth.SetBinContent(i+1,ttbarTemplateMVV.GetBinContent(j+1)*10.0/50.0)
             ttbar_smooth.SetBinError(i+1,ttbarTemplateMVV.GetBinError(j+1)*10.0/50.0)

             ttbar_smooth_fs_untagged.SetBinContent(i+1,ttbarTemplateMVV_fs_untagged.GetBinContent(j+1)*10.0/50.0)
             ttbar_smooth_fs_untagged.SetBinError(i+1,ttbarTemplateMVV_fs_untagged.GetBinError(j+1)*10.0/50.0)

             ttbar_smooth_fs_btagged.SetBinContent(i+1,ttbarTemplateMVV_fs_btagged.GetBinContent(j+1)*10.0/50.0)
             ttbar_smooth_fs_btagged.SetBinError(i+1,ttbarTemplateMVV_fs_btagged.GetBinError(j+1)*10.0/50.0)

             ttbar_smooth_fs_vbftagged.SetBinContent(i+1,ttbarTemplateMVV_fs_vbftagged.GetBinContent(j+1)*10.0/50.0)
             ttbar_smooth_fs_vbftagged.SetBinError(i+1,ttbarTemplateMVV_fs_vbftagged.GetBinError(j+1)*10.0/50.0)

             break

        vz_smooth.Smooth(300,'r')
        ttbar_smooth.Smooth(3000,'r')

        ## vz shape and ttbar+ww shape
        vzTempDataHistMVV = ROOT.RooDataHist(vzTemplateName,vzTemplateName,RooArgList(zz2l2q_mass),vz_smooth)
        ttbarTempDataHistMVV = ROOT.RooDataHist(ttbarTemplateName,ttbarTemplateName,RooArgList(zz2l2q_mass),ttbar_smooth)

        bkg_vz = ROOT.RooHistPdf(vzTemplateName+"Pdf",vzTemplateName+"Pdf",RooArgSet(zz2l2q_mass),vzTempDataHistMVV)
        bkg_ttbar = ROOT.RooHistPdf(ttbarTemplateName+"Pdf",ttbarTemplateName+"Pdf",RooArgSet(zz2l2q_mass),ttbarTempDataHistMVV)

        #JES TAG nuisances
        JES = ROOT.RooRealVar("JES","JES",0,-3,3)
        BTAG = ROOT.RooRealVar("BTAG_"+self.jetType,"BTAG_"+self.jetType,0, -10,10)

        ## rates for vz
        #bkgRate_vz_Shape_untagged = vz_smooth_fs_untagged.Integral()*self.lumi
        #bkgRate_vz_Shape_btagged = vz_smooth_fs_btagged.Integral()*self.lumi
        #bkgRate_vz_Shape_vbftagged = vz_smooth_fs_vbftagged.Integral()*self.lumi
        bkgRate_vz_Shape_untagged = vz_smooth_fs_untagged.Integral()
        bkgRate_vz_Shape_btagged = vz_smooth_fs_btagged.Integral()
        bkgRate_vz_Shape_vbftagged = vz_smooth_fs_vbftagged.Integral()

        btagRatio = bkgRate_vz_Shape_btagged/bkgRate_vz_Shape_untagged
        vbfRatio = bkgRate_vz_Shape_vbftagged/(bkgRate_vz_Shape_untagged+bkgRate_vz_Shape_btagged)

        rfvSigRate_vz = ROOT.RooFormulaVar()
        if(self.jetType=="resolved" and self.cat=='vbf-tagged') :
          rfvSigRate_vz = ROOT.RooFormulaVar("bkg_vz_norm","(1+0.1*@0)",ROOT.RooArgList(JES))
          bkgRate_vz_Shape = bkgRate_vz_Shape_vbftagged
        elif(self.jetType=="resolved" and self.cat=='b-tagged') :
          rfvSigRate_vz = ROOT.RooFormulaVar("bkg_vz_norm","(1+0.05*@0)*(1-0.1*@1*"+str(vbfRatio)+")",ROOT.RooArgList(BTAG,JES))
          bkgRate_vz_Shape = bkgRate_vz_Shape_btagged
        elif(self.jetType=="resolved" and self.cat=='untagged') :
          rfvSigRate_vz = ROOT.RooFormulaVar("bkg_vz_norm","(1-0.05*@0*"+str(btagRatio)+")*(1-0.1*@1*"+str(vbfRatio)+")",ROOT.RooArgList(BTAG,JES))
          bkgRate_vz_Shape = bkgRate_vz_Shape_untagged
        elif(self.jetType=="merged" and self.cat=='vbf-tagged') :
          rfvSigRate_vz = ROOT.RooFormulaVar("bkg_vz_norm","(1+0.1*@0)",ROOT.RooArgList(JES))
          bkgRate_vz_Shape = bkgRate_vz_Shape_vbftagged
        elif(self.jetType=="merged" and self.cat=='b-tagged') :
          rfvSigRate_vz = ROOT.RooFormulaVar("bkg_vz_norm","(1+0.2*@0)*(1-0.1*@1*"+str(vbfRatio)+")",ROOT.RooArgList(BTAG,JES))
          bkgRate_vz_Shape = bkgRate_vz_Shape_btagged
        elif(self.jetType=="merged" and self.cat=='untagged') :
          rfvSigRate_vz = ROOT.RooFormulaVar("bkg_vz_norm","(1-0.2*@0*"+str(btagRatio)+")*(1-0.1*@1*"+str(vbfRatio)+")",ROOT.RooArgList(BTAG,JES))
          bkgRate_vz_Shape = bkgRate_vz_Shape_untagged

        ## rates for ttbar+ww
        #bkgRate_ttbar_Shape_untagged = ttbar_smooth_fs_untagged.Integral()*self.lumi
        #bkgRate_ttbar_Shape_btagged = ttbar_smooth_fs_btagged.Integral()*self.lumi
        #bkgRate_ttbar_Shape_vbftagged = ttbar_smooth_fs_vbftagged.Integral()*self.lumi
        bkgRate_ttbar_Shape_untagged = ttbar_smooth_fs_untagged.Integral()
        bkgRate_ttbar_Shape_btagged = ttbar_smooth_fs_btagged.Integral()
        bkgRate_ttbar_Shape_vbftagged = ttbar_smooth_fs_vbftagged.Integral()
        print 'ttbar_smooth_fs_vbftagged = ',ttbar_smooth_fs_vbftagged.Integral()

        bkgRate_ttbar_Shape_mc = bkgRate_ttbar_Shape_untagged
        if(self.cat=="b-tagged") :
          bkgRate_ttbar_Shape_mc = bkgRate_ttbar_Shape_btagged
        if(self.cat=="vbf-tagged") :
          bkgRate_ttbar_Shape_mc = bkgRate_ttbar_Shape_vbftagged

        ttbar_MuEG_file = ROOT.TFile("CMSdata/alphaMethod_MuEG_Data_2016.root")
        channel_plus_cat = "resolvedSR"
        if(self.channel=="eeqq_Resolved" or self.channel=="mumuqq_Resolved") :
           channel_plus_cat = "resolvedSR"
        if(self.channel=="eeqq_Merged" or self.channel=="mumuqq_Merged") :
           channel_plus_cat = "mergedSR"
        if(self.cat=="b-tagged") :
           channel_plus_cat = channel_plus_cat+"btag"
        elif(self.cat=="vbf-tagged") :
           channel_plus_cat = channel_plus_cat+"vbf"

        # use emu data to get data-to-mc correction factor
        ttbar_MuEG_mc = ttbar_MuEG_file.Get("hmass_"+channel_plus_cat+"_TTplusWW_emu_Bin50GeV")
        ttbar_MuEG_data = ttbar_MuEG_file.Get("hmass_"+channel_plus_cat+"_Data_emu_Bin50GeV")
        ttbar_MuEG_WZ3LNu = ttbar_MuEG_file.Get("hmass_"+channel_plus_cat+"_WZ3LNu_emu_Bin50GeV")
        bkgRate_ttbar_Shape_DATAtoMC = (ttbar_MuEG_data.Integral("width")-ttbar_MuEG_WZ3LNu.Integral("width"))/ttbar_MuEG_mc.Integral("width")

        #bkgRate_ttbar_Shape = bkgRate_ttbar_Shape_mc*bkgRate_ttbar_Shape_DATAtoMC
        bkgRate_ttbar_Shape = bkgRate_ttbar_Shape_mc
        print "bkgRate_ttbar_Shape  = ",bkgRate_ttbar_Shape

        ###################################################################
        ## Reducible backgrounds : Z+jets ################
        ###################################################################

        bkg_zjets = ROOT.RooGenericPdf();
        print "zjets mass shape"

        ### cov matrix to account for shape+norm uncertainty
        p0p0_cov_zjets = theInputs['p0p0_cov_zjets']
        p0l0_cov_zjets = theInputs['p0l0_cov_zjets']
        p0p1_cov_zjets = theInputs['p0p1_cov_zjets']
        p0l1_cov_zjets = theInputs['p0l1_cov_zjets']
        l0p0_cov_zjets = theInputs['p0l0_cov_zjets']
        p1p0_cov_zjets = theInputs['p0p1_cov_zjets']
        l1p0_cov_zjets = theInputs['p0l1_cov_zjets']
        ###
        l0l0_cov_zjets = theInputs['l0l0_cov_zjets']
        l0p1_cov_zjets = theInputs['l0p1_cov_zjets']
        l0l1_cov_zjets = theInputs['l0l1_cov_zjets']
        p1l0_cov_zjets = theInputs['l0p1_cov_zjets']
        l1l0_cov_zjets = theInputs['l0l1_cov_zjets']
        ###
        p1p1_cov_zjets = theInputs['p1p1_cov_zjets']
        p1l1_cov_zjets = theInputs['p1l1_cov_zjets']
        l1p1_cov_zjets = theInputs['p1l1_cov_zjets']
        ###
        l1l1_cov_zjets = theInputs['l1l1_cov_zjets']

        ################################################################################################

        '''
        xbins = [0,1,2,3,10]
        h_powheg[i] = TH1D("h_powheg_"+str(i),"h_powheg_"+str(i),len(xbins)-1,array('d',xbins))
        '''
        n = 2 # only 4 parameters for resolved untagged cat
        cov_elements = []
        if(self.cat=="untagged" and self.jetType=="resolved") :
          cov_elements = [p0p0_cov_zjets,p0l0_cov_zjets,p0p1_cov_zjets,p0l1_cov_zjets,l0p0_cov_zjets,l0l0_cov_zjets,l0p1_cov_zjets,l0l1_cov_zjets,p1p0_cov_zjets,p1l0_cov_zjets,p1p1_cov_zjets,p1l1_cov_zjets,l1p0_cov_zjets,l1l0_cov_zjets,l1p1_cov_zjets,l1l1_cov_zjets]
          n = 4
        else :
          cov_elements = [p0p0_cov_zjets,p0l0_cov_zjets,l0p0_cov_zjets,l0l0_cov_zjets]
          n = 2

        cov = TMatrixDSym(n,array('d',cov_elements))
        eigen = TMatrixDSymEigen(cov)
        vecs = eigen.GetEigenVectors()
        vals  = eigen.GetEigenValues()

        # nuisances without correlation that would control Z+jets spectrum (shape and normalization)
        eig0Name = "eig0_"+self.jetType+"_"+self.cat_tree
        eig1Name = "eig1_"+self.jetType+"_"+self.cat_tree
        eig2Name = "eig2_"+self.jetType+"_"+self.cat_tree
        eig3Name = "eig3_"+self.jetType+"_"+self.cat_tree

        eig0 = RooRealVar(eig0Name,eig0Name,0,-3,3)
        eig1 = RooRealVar(eig1Name,eig1Name,0,-3,3)
        eig2 = RooRealVar(eig2Name,eig2Name,0,-3,3)
        eig3 = RooRealVar(eig3Name,eig3Name,0,-3,3)

        eig0.setConstant(True)
        eig1.setConstant(True)
        eig2.setConstant(True)
        eig3.setConstant(True)

        eigCoeff0 = []
        eigCoeff1 = []
        eigCoeff2 = []
        eigCoeff3 = []

        if(self.cat=="untagged" and self.jetType=="resolved") :
           eigCoeff0 = [vecs(0,0)*pow(vals(0),0.5),vecs(0,1)*pow(vals(1),0.5),vecs(0,2)*pow(vals(2),0.5),vecs(0,3)*pow(vals(3),0.5)]
           eigCoeff1 = [vecs(1,0)*pow(vals(0),0.5),vecs(1,1)*pow(vals(1),0.5),vecs(1,2)*pow(vals(2),0.5),vecs(1,3)*pow(vals(3),0.5)]
           eigCoeff2 = [vecs(2,0)*pow(vals(0),0.5),vecs(2,1)*pow(vals(1),0.5),vecs(2,2)*pow(vals(2),0.5),vecs(2,3)*pow(vals(3),0.5)]
           eigCoeff3 = [vecs(3,0)*pow(vals(0),0.5),vecs(3,1)*pow(vals(1),0.5),vecs(3,2)*pow(vals(2),0.5),vecs(3,3)*pow(vals(3),0.5)]
        else :
           eigCoeff0 = [vecs(0,0)*pow(vals(0),0.5),vecs(0,1)*pow(vals(1),0.5)]
           eigCoeff1 = [vecs(1,0)*pow(vals(0),0.5),vecs(1,1)*pow(vals(1),0.5)]

        ###################################################

        p0_zjets = theInputs['p0_zjets']
        l0_zjets = theInputs['l0_zjets']
        p1_zjets = theInputs['p1_zjets']
        l1_zjets = theInputs['l1_zjets']

        p0_alt_zjets = theInputs['p0_alt_zjets']
        l0_alt_zjets = theInputs['l0_alt_zjets']
        p1_alt_zjets = theInputs['p1_alt_zjets']
        l1_alt_zjets = theInputs['l1_alt_zjets']

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

        if(self.cat=="untagged" and self.jetType=="resolved") :

          p0_unc_str = "( ("+str(eigCoeff0[0])+")*"+eig0Name+"+("+str(eigCoeff0[1])+")*"+eig1Name+"+("+str(eigCoeff0[2])+")*"+eig2Name+"+("+str(eigCoeff0[3])+")*"+eig3Name+")"
          ######
          l0_unc_str = "( ("+str(eigCoeff1[0])+")*"+eig0Name+"+("+str(eigCoeff1[1])+")*"+eig1Name+"+("+str(eigCoeff1[2])+")*"+eig2Name+"+("+str(eigCoeff1[3])+")*"+eig3Name+")"
          ######
          p1_unc_str = "( ("+str(eigCoeff2[0])+")*"+eig0Name+"+("+str(eigCoeff2[1])+")*"+eig1Name+"+("+str(eigCoeff2[2])+")*"+eig2Name+"+("+str(eigCoeff2[3])+")*"+eig3Name+")"
          ######
          l1_unc_str = "( ("+str(eigCoeff3[0])+")*"+eig0Name+"+("+str(eigCoeff3[1])+")*"+eig1Name+"+("+str(eigCoeff3[2])+")*"+eig2Name+"+("+str(eigCoeff3[3])+")*"+eig3Name+")"

        else :

          p0_unc_str = "( ("+str(eigCoeff0[0])+")*"+eig0Name+"+("+str(eigCoeff0[1])+")*"+eig1Name+")"
          ######
          l0_unc_str = "( ("+str(eigCoeff1[0])+")*"+eig0Name+"+("+str(eigCoeff1[1])+")*"+eig1Name+")"

        p0_str = "("+p0_nominal_str+"+"+p0_unc_str+")"
        ######
        l0_str = "("+l0_nominal_str+"+"+l0_unc_str+")"
        ######
        p1_str = "("+p1_nominal_str+"+"+p1_unc_str+")"
        ######
        l1_str = "("+l1_nominal_str+"+"+l1_unc_str+")"

        print 'p0 ',p0_str
        print 'l0 ',l0_str
        print 'p1 ',p1_str
        print 'l1 ',l1_str

        ##################################################

        cat=self.cat
        if(self.cat=="b-tagged") :
          cat="btagged"
        if(self.cat=="vbf-tagged") :
          cat="vbftagged"

        if(self.cat=="untagged" and self.jetType=="resolved") :
          bkg_zjets_TString = "TMath::Exp("+p0_str+"-"+l0_str+"*zz2l2q_mass)+TMath::Exp("+p1_str+"-"+l1_str+"*zz2l2q_mass)"
          bkg_zjets = ROOT.RooGenericPdf("bkg_zjets_"+self.jetType+"_"+cat,bkg_zjets_TString,ROOT.RooArgList(zz2l2q_mass,eig0,eig1,eig2,eig3) )
        elif(self.cat!="untagged" and self.jetType=="resolved") :
          bkg_zjets_TString = "TMath::Exp("+p0_str+"-"+l0_str+"*zz2l2q_mass)"
          bkg_zjets = ROOT.RooGenericPdf("bkg_zjets_"+self.jetType+"_"+cat,bkg_zjets_TString,ROOT.RooArgList(zz2l2q_mass,eig0,eig1) )
        elif(self.jetType=="merged") :
          bkg_zjets_TString = "TMath::Exp("+p0_str+"-"+l0_str+"*zz2lJ_mass)"
          bkg_zjets = ROOT.RooGenericPdf("bkg_zjets_"+self.jetType+"_"+cat,bkg_zjets_TString,ROOT.RooArgList(zz2l2q_mass,eig0,eig1) )
        #########################################
        ## Zjets norm ################
        #########################################

        BrZee_zjets_Shape = 0.432581
        if(self.jetType=="resolved" and self.cat=="untagged") :
          BrZee_zjets_Shape = 0.4212420
        if(self.jetType=="resolved" and self.cat=="b-tagged") :
          BrZee_zjets_Shape = 0.3905356
        if(self.jetType=="resolved" and self.cat=="vbf-tagged") :
          BrZee_zjets_Shape = 0.4073305
        if(self.jetType=="merged" and self.cat=="untagged") :
          BrZee_zjets_Shape = 0.4272461
        if(self.jetType=="merged" and self.cat=="b-tagged") :
          BrZee_zjets_Shape = 0.4695593
        if(self.jetType=="merged" and self.cat=="vbf-tagged") :
          BrZee_zjets_Shape = 0.3931084
        #############################################
        BrZll_zjets_Shape = BrZee_zjets_Shape
        if(self.channel=="mumuqq_Merged" or self.channel=="mumuqq_Resolved") :
           BrZll_zjets_Shape = 1-BrZll_zjets_Shape

        bkgRate_zjets_TString = ""
        if(self.cat=="untagged" and self.jetType=="resolved") :
           bkgRate_zjets_TString = "( (1/"+l0_str+")*(TMath::Exp("+p0_str+"-"+l0_str+"*"+str(self.low_M)+")-TMath::Exp("+p0_str+"-"+l0_str+"*"+str(self.high_M)+") ) + (1/"+l1_str+")*(TMath::Exp("+p1_str+"-"+l1_str+"*"+str(self.low_M)+")-TMath::Exp("+p1_str+"-"+l1_str+"*"+str(self.high_M)+") ) )/50"
        else :
           bkgRate_zjets_TString = "( (1/"+l0_str+")*(TMath::Exp("+p0_str+"-"+l0_str+"*"+str(self.low_M)+")-TMath::Exp("+p0_str+"-"+l0_str+"*"+str(self.high_M)+") ) )/50"

        #### only for debug, make sure zjets rate is correct
        bkg_zjets_nomial_TF1_TString = ""
        if(self.cat=="untagged" and self.jetType=="resolved") :
           bkg_zjets_nomial_TF1_TString = "exp("+str(p0_zjets)+"-"+str(l0_zjets)+"*x)/50 + exp("+str(p1_zjets)+"-"+str(l1_zjets)+"*x)/50"
        else :
           bkg_zjets_nomial_TF1_TString = "exp("+str(p0_zjets)+"-"+str(l0_zjets)+"*x)/50"

        #####
        bkgRate_zjets_TF1 = TF1("bkgRate_zjets_TF1","("+bkg_zjets_nomial_TF1_TString+")",self.low_M,self.high_M)
        bkgRate_zjets_Shape = bkgRate_zjets_TF1.Integral(self.low_M,self.high_M)

        rfvSigRate_zjets = ROOT.RooFormulaVar()
        if(self.cat=="untagged" and self.jetType=="resolved") :
           rfvSigRate_zjets = ROOT.RooFormulaVar("bkg_zjets_norm",bkgRate_zjets_TString,ROOT.RooArgList(eig0,eig1,eig2,eig3) )
        else :
           rfvSigRate_zjets = ROOT.RooFormulaVar("bkg_zjets_norm",bkgRate_zjets_TString,ROOT.RooArgList(eig0,eig1) )

        print 'Debug rfvSigRate_zjets from TF1 ',bkgRate_zjets_Shape,' from Rfv ',rfvSigRate_zjets.getVal()

        ##### the final number for zjets rate into datacard
        bkgRate_zjets_Shape = BrZll_zjets_Shape

        ## --------------------------- MELA 2D PDFS ------------------------- ##

        discVarName = "Dspin0"

        templateSigName = "templates2D/2l2q_spin0_template_{}.root".format(self.year)
        templateSigNameUp = "templates2D/2l2q_spin0_template_{}.root".format(self.year)
        templateSigNameDn = "templates2D/2l2q_spin0_template_{}.root".format(self.year)

        sigTempFile = ROOT.TFile(templateSigName)
        sigTempFileUp = ROOT.TFile(templateSigNameUp)
        sigTempFileDn = ROOT.TFile(templateSigNameDn)
        TString_sig = "sig_resolved"
        if(self.channel=="mumuqq_Merged" or self.channel=="eeqq_Merged") :
          TString_sig = "sig_merged"

        sigTemplate = sigTempFile.Get(TString_sig)
        sigTemplate_Up = sigTempFileUp.Get(TString_sig+"_up")
        sigTemplate_Down = sigTempFileDn.Get(TString_sig+"_dn")
        print 'templateSigName ',templateSigName

        dBins = sigTemplate.GetYaxis().GetNbins()
        dLow = sigTemplate.GetYaxis().GetXmin()
        dHigh = sigTemplate.GetYaxis().GetXmax()
        D = ROOT.RooRealVar(discVarName,discVarName,dLow,dHigh)
        D.setBins(dBins)
        print "discVarName ", discVarName, " dLow ", dLow, " dHigh ", dHigh, " dBins ", dBins

        TemplateName = "sigTempDataHist_"+TString_sig
        sigTempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(zz2l2q_mass,D),sigTemplate)
        TemplateName = "sigTempDataHist_"+TString_sig+"_Up"
        sigTempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(zz2l2q_mass,D),sigTemplate_Up)
        TemplateName = "sigTempDataHist_"+TString_sig+"_Down"
        sigTempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(zz2l2q_mass,D),sigTemplate_Down)
        TemplateName = "sigTemplatePdf_ggH_"+TString_sig
        sigTemplatePdf_ggH = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),sigTempDataHist)
        TemplateName = "sigTemplatePdf_ggH_"+TString_sig+"_Up"
        sigTemplatePdf_ggH_Up = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),sigTempDataHist_Up)
        TemplateName = "sigTemplatePdf_ggH_"+TString_sig+"_Down"
        sigTemplatePdf_ggH_Down = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),sigTempDataHist_Down)

        TemplateName = "sigTemplatePdf_VBF_"+TString_sig
        sigTemplatePdf_VBF = ROOT.RooHistPdf(TemplateName,TemplateName,RooArgSet(zz2l2q_mass,D),sigTempDataHist)
        TemplateName = "sigTemplatePdf_VBF_"+TString_sig+"_Up"
        sigTemplatePdf_VBF_Up = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),sigTempDataHist_Up)
        TemplateName = "sigTemplatePdf_VBF_"+TString_sig+"Down"
        sigTemplatePdf_VBF_Down = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),sigTempDataHist_Down)

        funcList_ggH = ROOT.RooArgList()
        funcList_VBF = ROOT.RooArgList()

        funcList_ggH.add(sigTemplatePdf_ggH)
        funcList_VBF.add(sigTemplatePdf_VBF)

        if(self.sigMorph):
           funcList_ggH.add(sigTemplatePdf_ggH_Up)
           funcList_ggH.add(sigTemplatePdf_ggH_Down)
           funcList_VBF.add(sigTemplatePdf_VBF_Up)
           funcList_VBF.add(sigTemplatePdf_VBF_Down)

        morphSigVarName = "CMS_zz2l2q_sigMELA_"+self.jetType
        alphaMorphSig = ROOT.RooRealVar(morphSigVarName,morphSigVarName,0,-20,20)
        if(self.sigMorph): alphaMorphSig.setConstant(False)
        else: alphaMorphSig.setConstant(True)

        morphVarListSig = ROOT.RooArgList()
        if(self.sigMorph):
          morphVarListSig.add(alphaMorphSig)  ## just one morphing for all signal processes

        true=True
        TemplateName = "sigTemplateMorphPdf_ggH_"+TString_sig
        sigTemplateMorphPdf_ggH = ROOT.FastVerticalInterpHistPdf2D(TemplateName,TemplateName,zz2l2q_mass,D,true,funcList_ggH,morphVarListSig,1.0,1)

        TemplateName = "sigTemplateMorphPdf_VBF_"+TString_sig
        sigTemplateMorphPdf_VBF = ROOT.FastVerticalInterpHistPdf2D(TemplateName,TemplateName,zz2l2q_mass,D,true,funcList_VBF,morphVarListSig,1.0,1)

        ##### 2D -> mzz + Djet
        name = "sigCB2d_ggH"
        sigCB2d_ggH = ROOT.RooProdPdf(name,name,ROOT.RooArgSet(signalCB_ggH),ROOT.RooFit.Conditional(ROOT.RooArgSet(sigTemplateMorphPdf_ggH), ROOT.RooArgSet(D) ) )
        name = "sigCB2d_qqH"
        sigCB2d_VBF = ROOT.RooProdPdf(name,name,ROOT.RooArgSet(signalCB_VBF),ROOT.RooFit.Conditional(ROOT.RooArgSet(sigTemplateMorphPdf_VBF), ROOT.RooArgSet(D) ) )

        ## ----------------- 2D BACKGROUND SHAPES --------------- ##
        ##### Zjets KD

        templatezjetsBkgName = "templates2D/2l2q_spin0_template_{}.root".format(self.year)
        templatezjetsBkgNameUp = "templates2D/2l2q_spin0_template_{}.root".format(self.year)
        templatezjetsBkgNameDn = "templates2D/2l2q_spin0_template_{}.root".format(self.year)

        print templatezjetsBkgName, "file used for Zjets"

        TString_bkg = "DY_resolved"
        if(self.channel=="mumuqq_Merged" or self.channel=="eeqq_Merged") :
          TString_bkg = "DY_merged"

        zjetsTempFile = ROOT.TFile(templatezjetsBkgName)
        zjetsTempFileUp = ROOT.TFile(templatezjetsBkgNameUp)
        zjetsTempFileDn = ROOT.TFile(templatezjetsBkgNameDn)
        zjetsTemplate = zjetsTempFile.Get(TString_bkg)
        zjetsTemplate_Up = zjetsTempFile.Get(TString_bkg+"_up")
        zjetsTemplate_Down = zjetsTempFile.Get(TString_bkg+"_dn")

        TemplateName = "zjetsTempDataHist_"+TString_bkg
        zjetsTempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(zz2l2q_mass,D),zjetsTemplate)
        TemplateName = "zjetsTempDataHist_"+TString_bkg+"_Up"
        zjetsTempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(zz2l2q_mass,D),zjetsTemplate_Up)
        TemplateName = "zjetsTempDataHist_"+TString_bkg+"_Down"
        zjetsTempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(zz2l2q_mass,D),zjetsTemplate_Down)

        TemplateName = "zjetsTemplatePdf_"+TString_bkg
        bkgTemplatePdf_zjets = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),zjetsTempDataHist)
        TemplateName = "zjetsTemplatePdf_"+TString_bkg+"_Up"

        bkgTemplatePdf_zjets_Up = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),zjetsTempDataHist_Up)
        TemplateName = "zjetsTemplatePdf_"+TString_bkg+"_Down"
        bkgTemplatePdf_zjets_Down = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),zjetsTempDataHist_Down)

        ### TTbar KD
        TString_bkg = "TTbar_resolved"
        if(self.channel=="mumuqq_Merged" or self.channel=="eeqq_Merged") :
          TString_bkg = "TTbar_merged"

        ttbarTempFile = ROOT.TFile(templatezjetsBkgName)
        ttbarTempFileUp = ROOT.TFile(templatezjetsBkgNameUp)
        ttbarTempFileDn = ROOT.TFile(templatezjetsBkgNameDn)
        ttbarTemplate = ttbarTempFile.Get(TString_bkg)
        ttbarTemplate_Up = ttbarTempFileUp.Get(TString_bkg+"_up")
        ttbarTemplate_Down = ttbarTempFileDn.Get(TString_bkg+"_dn")

        TemplateName = "ttbarTempDataHist_"+TString_bkg
        ttbarTempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(zz2l2q_mass,D),ttbarTemplate)
        TemplateName = "ttbarTempDataHist_"+TString_bkg+"_Up"
        ttbarTempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(zz2l2q_mass,D),ttbarTemplate_Up)
        TemplateName = "ttbarTempDataHist_"+TString_bkg+"_Down"
        ttbarTempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(zz2l2q_mass,D),ttbarTemplate_Down)

        TemplateName = "ttbarTemplatePdf_"+TString_bkg
        bkgTemplatePdf_ttbar = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),ttbarTempDataHist)
        TemplateName = "ttbarTemplatePdf_"+TString_bkg+"_Up"
        bkgTemplatePdf_ttbar_Up = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),ttbarTempDataHist_Up)
        TemplateName = "ttbarTemplatePdf_"+TString_bkg+"_Down"
        bkgTemplatePdf_ttbar_Down = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),ttbarTempDataHist_Down)

        ### VZ KD
        TString_bkg = "Diboson_resolved"
        if(self.channel=="mumuqq_Merged" or self.channel=="eeqq_Merged") :
          TString_bkg = "Diboson_merged"

        vzTempFile = ROOT.TFile(templatezjetsBkgName)
        vzTempFileUp = ROOT.TFile(templatezjetsBkgNameUp)
        vzTempFileDn = ROOT.TFile(templatezjetsBkgNameDn)
        vzTemplate = vzTempFile.Get(TString_bkg)
        vzTemplate_Up = vzTempFileUp.Get(TString_bkg+"_up")
        vzTemplate_Down = vzTempFileDn.Get(TString_bkg+"_dn")

        TemplateName = "vzTempDataHist_"+TString_bkg
        vzTempDataHist = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(zz2l2q_mass,D),vzTemplate)
        TemplateName = "vzTempDataHist_"+TString_bkg+"_Up"
        vzTempDataHist_Up = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(zz2l2q_mass,D),vzTemplate_Up)
        TemplateName = "vzTempDataHist_"+TString_bkg+"_Down"
        vzTempDataHist_Down = ROOT.RooDataHist(TemplateName,TemplateName,ROOT.RooArgList(zz2l2q_mass,D),vzTemplate_Down)

        TemplateName = "vzTemplatePdf_"+TString_bkg
        bkgTemplatePdf_vz = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),vzTempDataHist)
        TemplateName = "vzTemplatePdf_"+TString_bkg+"_Up"
        bkgTemplatePdf_vz_Up = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),vzTempDataHist_Up)
        TemplateName = "vzTemplatePdf_"+TString_bkg+"_Down"
        bkgTemplatePdf_vz_Down = ROOT.RooHistPdf(TemplateName,TemplateName,ROOT.RooArgSet(zz2l2q_mass,D),vzTempDataHist_Down)

        ####
        # bkg morphing

        funcList_zjets = ROOT.RooArgList()
        funcList_ttbar = ROOT.RooArgList()
        funcList_vz = ROOT.RooArgList()
        morphBkgVarName = "CMS_zz2l2q_bkgMELA_"+self.jetType
        alphaMorphBkg = ROOT.RooRealVar(morphBkgVarName,morphBkgVarName,0,-20,20)
        morphVarListBkg = ROOT.RooArgList()

        if(self.bkgMorph):
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

        TemplateName = "bkgTemplateMorphPdf_zjets_"+self.jetType
        bkgTemplateMorphPdf_zjets = ROOT.FastVerticalInterpHistPdf2D(TemplateName,TemplateName,zz2l2q_mass,D,true,funcList_zjets,morphVarListBkg,1.0,1)
        TemplateName = "bkgTemplateMorphPdf_ttbar_"+self.jetType
        bkgTemplateMorphPdf_ttbar = ROOT.FastVerticalInterpHistPdf2D(TemplateName,TemplateName,zz2l2q_mass,D,true,funcList_zjets,morphVarListBkg,1.0,1)
        TemplateName = "bkgTemplateMorphPdf_vz_"+self.jetType
        bkgTemplateMorphPdf_vz = ROOT.FastVerticalInterpHistPdf2D(TemplateName,TemplateName,zz2l2q_mass,D,true,funcList_zjets,morphVarListBkg,1.0,1)

        #### bkg 2D : mzz + Djet;
        name = "bkg2d_zjets"
        bkg2d_zjets = ROOT.RooProdPdf(name,name,ROOT.RooArgSet(bkg_zjets),ROOT.RooFit.Conditional(ROOT.RooArgSet(bkgTemplateMorphPdf_zjets),ROOT.RooArgSet(D) ) )
        name = "bkg2d_ttbar"
        bkg2d_ttbar = ROOT.RooProdPdf(name,name,ROOT.RooArgSet(bkg_ttbar),ROOT.RooFit.Conditional(ROOT.RooArgSet(bkgTemplateMorphPdf_ttbar),ROOT.RooArgSet(D) ) )
        name = "bkg2d_vz"
        bkg2d_vz= ROOT.RooProdPdf(name,name,ROOT.RooArgSet(bkg_vz),ROOT.RooFit.Conditional(ROOT.RooArgSet(bkgTemplateMorphPdf_vz),ROOT.RooArgSet(D) ) )

        '''
        ## ----------------------- PLOTS FOR SANITY CHECKS -------------------------- ##
        canv_name = "czz_{0}_{1}".format(self.mH,self.appendName)
        czz = ROOT.TCanvas( canv_name, canv_name, 750, 700 )
        czz.cd()
        zzframe_s = zz2l2q_mass.frame(220)

        print 'plot signal'
        signalCB_ggH.plotOn(zzframe_s, ROOT.RooFit.LineStyle(1), ROOT.RooFit.LineColor(1) )
        signalCB_VBF.plotOn(zzframe_s, ROOT.RooFit.LineStyle(2), ROOT.RooFit.LineColor(1) )
        print 'plot zjets'
        bkg_zjets.plotOn(zzframe_s, ROOT.RooFit.LineStyle(1), ROOT.RooFit.LineColor(2) )
        print 'plot zv'
        bkg_vz.plotOn(zzframe_s, ROOT.RooFit.LineStyle(1), ROOT.RooFit.LineColor(3) )
        print 'plot ttbar'
        bkg_ttbar.plotOn(zzframe_s, ROOT.RooFit.LineStyle(1), ROOT.RooFit.LineColor(4) )
        zzframe_s.Draw()

        figName = "{0}/figs/mzz_{1}_{2}.png".format(self.outputDir, self.mH, self.appendName)
        czz.SaveAs(figName)
        del czz
        '''

        ## ----------------------- SIGNAL RATES ----------------------- ##

        sigRate_ggH_Shape = 1
        sigRate_VBF_Shape = 1

        ###########
        print 'signal rates'

        ggH_accxeff = ROOT.TFile("SigEff/2l2q_Efficiency_spin0_ggH_{}.root".format(self.year))
        VBF_accxeff = ROOT.TFile("SigEff/2l2q_Efficiency_spin0_VBF_{}.root".format(self.year))

        ggh_accxeff_vbf = ggH_accxeff.Get("spin0_ggH_"+self.channel+"_vbf-tagged").GetListOfFunctions().First().Eval(self.mH)
        ggh_accxeff_btag = ggH_accxeff.Get("spin0_ggH_"+self.channel+"_b-tagged").GetListOfFunctions().First().Eval(self.mH)
        ggh_accxeff_untag = ggH_accxeff.Get("spin0_ggH_"+self.channel+"_untagged").GetListOfFunctions().First().Eval(self.mH)

        vbfRatioGGH = ggh_accxeff_vbf/(ggh_accxeff_untag+ggh_accxeff_btag)
        btagRatioGGH = ggh_accxeff_btag/ggh_accxeff_untag

        ########
        vbf_accxeff_vbf = VBF_accxeff.Get("spin0_VBF_"+self.channel+"_vbf-tagged").GetListOfFunctions().First().Eval(self.mH)
        vbf_accxeff_btag = VBF_accxeff.Get("spin0_VBF_"+self.channel+"_b-tagged").GetListOfFunctions().First().Eval(self.mH)
        vbf_accxeff_untag = VBF_accxeff.Get("spin0_VBF_"+self.channel+"_untagged").GetListOfFunctions().First().Eval(self.mH)

        vbfRatioVBF = vbf_accxeff_vbf/(vbf_accxeff_untag+vbf_accxeff_btag)
        btagRatioVBF = vbf_accxeff_btag/vbf_accxeff_untag

        ####
        # the numbers written to the datacards
        sigRate_ggH_Shape = ggH_accxeff.Get("spin0_ggH_"+self.appendName).GetListOfFunctions().First().Eval(self.mH)
        sigRate_VBF_Shape = VBF_accxeff.Get("spin0_VBF_"+self.appendName).GetListOfFunctions().First().Eval(self.mH)

        sigRate_ggH_Shape = sigRate_ggH_Shape*sigFraction
        sigRate_VBF_Shape = sigRate_VBF_Shape*sigFraction

        if(sigRate_ggH_Shape<0):
          sigRate_ggH_Shape=0.0
        if(sigRate_VBF_Shape<0):
          sigRate_VBF_Shape=0.0
        print 'sigFraction ',sigFraction
        print 'sigRate_ggH_Shape ',sigRate_ggH_Shape


        # VBF branching ratio
        print 'VBF/ggH ratio'
        frac_VBF = ROOT.RooRealVar("frac_VBF","frac_VBF", theFracVBF, 0.0, 1.0)
        #frac_VBF.setConstant(True)
        frac_ggH = ROOT.RooFormulaVar("frac_ggH","(1-@0)",ROOT.RooArgList(frac_VBF))
        BR = ROOT.RooRealVar("BR","BR", 2*0.7*2*0.033*1000) # ZZ->2l2q (l = e,mu) no Z->taus in signal MC

        rfvSigRate_ggH = ROOT.RooFormulaVar()
        rfvSigRate_VBF = ROOT.RooFormulaVar()
        if(self.cat=='vbf-tagged') :
          rfvSigRate_ggH = ROOT.RooFormulaVar("ggH_hzz_norm","(1+0.1*@0)*@1*@2*@3",ROOT.RooArgList(JES,self.LUMI,frac_ggH,BR))
          rfvSigRate_VBF = ROOT.RooFormulaVar("qqH_hzz_norm","(1+0.05*@0)*@1*@2*@3",ROOT.RooArgList(JES,self.LUMI,frac_VBF,BR))
        elif(self.jetType=="resolved" and self.cat=='b-tagged') :
          rfvSigRate_ggH = ROOT.RooFormulaVar("ggH_hzz_norm","(1+0.05*@0)*(1-0.1*@1*"+str(vbfRatioGGH)+")*@2*@3*@4",ROOT.RooArgList(BTAG,JES,self.LUMI,frac_ggH,BR))
          rfvSigRate_VBF = ROOT.RooFormulaVar("qqH_hzz_norm","(1+0.05*@0)*(1-0.05*@1*"+str(vbfRatioVBF)+")*@2*@3*@4",ROOT.RooArgList(BTAG,JES,self.LUMI,frac_VBF,BR))
        elif(self.jetType=="resolved" and self.cat=='untagged') :
          rfvSigRate_ggH = ROOT.RooFormulaVar("ggH_hzz_norm","(1-0.05*@0*"+str(btagRatioGGH)+")*(1-0.1*@1*"+str(vbfRatioGGH)+")*@2*@3*@4",ROOT.RooArgList(BTAG,JES,self.LUMI,frac_ggH,BR))
          rfvSigRate_VBF = ROOT.RooFormulaVar("qqH_hzz_norm","(1-0.05*@0*"+str(btagRatioVBF)+")*(1-0.05*@1*"+str(vbfRatioVBF)+")*@2*@3*@4",ROOT.RooArgList(BTAG,JES,self.LUMI,frac_VBF,BR))
        elif(self.jetType=="merged" and self.cat=='b-tagged') :
          rfvSigRate_ggH = ROOT.RooFormulaVar("ggH_hzz_norm","(1+0.2*@0)*(1-0.1*@1*"+str(vbfRatioGGH)+")*@2*@3*@4",ROOT.RooArgList(BTAG,JES,self.LUMI,frac_ggH,BR))
          rfvSigRate_VBF = ROOT.RooFormulaVar("qqH_hzz_norm","(1+0.2*@0)*(1-0.05*@1*"+str(vbfRatioVBF)+")*@2*@3*@4",ROOT.RooArgList(BTAG,JES,self.LUMI,frac_VBF,BR))
        elif(self.jetType=="merged" and self.cat=='untagged') :
          rfvSigRate_ggH = ROOT.RooFormulaVar("ggH_hzz_norm","(1-0.2*@0*"+str(btagRatioGGH)+")*(1-0.1*@1*"+str(vbfRatioGGH)+")*@2*@3*@4",ROOT.RooArgList(BTAG,JES,self.LUMI,frac_ggH,BR))
          rfvSigRate_VBF = ROOT.RooFormulaVar("qqH_hzz_norm","(1-0.2*@0*"+str(btagRatioVBF)+")*(1-0.05*@1*"+str(vbfRatioVBF)+")*@2*@3*@4",ROOT.RooArgList(BTAG,JES,self.LUMI,frac_VBF,BR))

        print 'Rates ggH ',rfvSigRate_ggH.getVal(),' VBF ',rfvSigRate_VBF.getVal()

        ## ----------------------- BACKGROUND RATES ----------------------- ##

        #bkgRate_zjets_Shape = theInputs['zjets_rate']

        ## --------------------------- DATASET --------------------------- ##

        dataFileDir = "CMSdata"
        dataFileName = "{0}/Data_SR.root".format(dataFileDir)

        if (DEBUG): print dataFileName," ",dataTreeName
        data_obs_file = ROOT.TFile(dataFileName)

        treeName=""
        if(self.channel=="eeqq_Resolved" and self.cat=="vbf-tagged") :
          treeName="TreeSR0"
        if(self.channel=="eeqq_Resolved" and self.cat=="b-tagged") :
          treeName="TreeSR1"
        if(self.channel=="eeqq_Resolved" and self.cat=="untagged") :
          treeName="TreeSR2"
        if(self.channel=="eeqq_Merged" and self.cat=="vbf-tagged") :
          treeName="TreeSR3"
        if(self.channel=="eeqq_Merged" and self.cat=="b-tagged") :
          treeName="TreeSR4"
        if(self.channel=="eeqq_Merged" and self.cat=="untagged") :
          treeName="TreeSR5"

        if(self.channel=="mumuqq_Resolved" and self.cat=="vbf-tagged") :
          treeName="TreeSR6"
        if(self.channel=="mumuqq_Resolved" and self.cat=="b-tagged") :
          treeName="TreeSR7"
        if(self.channel=="mumuqq_Resolved" and self.cat=="untagged") :
          treeName="TreeSR8"
        if(self.channel=="mumuqq_Merged" and self.cat=="vbf-tagged") :
          treeName="TreeSR9"
        if(self.channel=="mumuqq_Merged" and self.cat=="b-tagged") :
          treeName="TreeSR10"
        if(self.channel=="mumuqq_Merged" and self.cat=="untagged") :
          treeName="TreeSR11"

        print data_obs_file.Get(treeName)

        if not (data_obs_file.Get(treeName)):
            print "File, \"",dataFileName,"\", or tree, \"",treeName,"\", not found"
            print "Exiting..."
            sys.exit()

        zz2lJ_mass_struct=zz2lJ_massStruct()
        tmpFile = TFile("tmpFile.root","RECREATE")
        data_obs_tree = (data_obs_file.Get(treeName)).CloneTree(0)
        data_obs_tree.Branch('zz2lJ_mass', zz2lJ_mass_struct, 'zz2lJ_mass/D')
        for i in range(0,data_obs_file.Get(treeName).GetEntries()) :
          data_obs_file.Get(treeName).GetEntry(i)
          zz2lJ_mass_struct.zz2lJ_mass = data_obs_file.Get(treeName).zz2l2q_mass
          data_obs_tree.Fill()

        data_obs = ROOT.RooDataSet()
        datasetName = "data_obs"

        if (self.is2D == 0):
            data_obs = ROOT.RooDataSet(datasetName,datasetName,data_obs_tree,ROOT.RooArgSet(zz2l2q_mass))
        if (self.is2D == 1):
            data_obs = ROOT.RooDataSet(datasetName,datasetName,data_obs_tree,ROOT.RooArgSet(zz2l2q_mass,D) )

        '''
        print 'generate pseudo dataset'
        data_obs = /OOT.RooDataSet()
        if (self.is2D == 0):
         data_obs = signalCB_ggH.generate(ROOT.RooArgSet(zz2l2q_mass), int(bkgRate_zjets_Shape))
        if (self.is2D == 1):
         data_obs = sigCB2d_ggH.generate(ROOT.RooArgSet(zz2l2q_mass,D), int(bkgRate_zjets_Shape))
        '''

        ## --------------------------- WORKSPACE -------------------------- ##
        print 'prepare workspace'
        endsInP5 = False
        tmpMH = self.mH
        if ( math.fabs(math.floor(tmpMH)-self.mH) > 0.001): endsInP5 = True
        if (DEBUG): print "ENDS IN P5  ",endsInP5

        name_Shape = ""
        name_ShapeWS = ""
        name_ShapeWS2 = ""

        if (endsInP5): name_Shape = "{0}/HCG/{1:.1f}/hzz2l2q_{2}_{3:.0f}TeV.txt".format(self.outputDir,self.mH,self.appendName,self.sqrts)
        else: name_Shape = "{0}/HCG/{1:.0f}/hzz2l2q_{2}_{3:.0f}TeV.txt".format(self.outputDir,self.mH,self.appendName,self.sqrts)

        if (endsInP5): name_ShapeWS = "{0}/HCG/{1:.1f}/hzz2l2q_{2}_{3:.0f}TeV.input.root".format(self.outputDir,self.mH,self.appendName,self.sqrts)
        else: name_ShapeWS = "{0}/HCG/{1:.0f}/hzz2l2q_{2}_{3:.0f}TeV.input.root".format(self.outputDir,self.mH,self.appendName,self.sqrts)

        name_ShapeWS2 = "hzz2l2q_{0}_{1:.0f}TeV.input.root".format(self.appendName,self.sqrts)

        if(DEBUG): print name_Shape,"  ",name_ShapeWS2

        w = ROOT.RooWorkspace("w","w")
        w.importClassCode(RooDoubleCB.Class(),True)
        w.importClassCode(RooFormulaVar.Class(),True)

        getattr(w,'import')(data_obs,ROOT.RooFit.Rename("data_obs")) ### Should this be renamed?

        if (self.is2D == 0):
                    signalCB_ggH.SetNameTitle("ggH_hzz","ggH_hzz")
                    signalCB_VBF.SetNameTitle("qqH_hzz","qqH_hzz")
                    getattr(w,'import')(signalCB_ggH, ROOT.RooFit.RecycleConflictNodes())
                    getattr(w,'import')(signalCB_VBF, ROOT.RooFit.RecycleConflictNodes())

        if (self.is2D == 1):
                    sigCB2d_ggH.SetNameTitle("ggH_hzz","ggH_hzz")
                    sigCB2d_VBF.SetNameTitle("qqH_hzz","qqH_hzz")
                    getattr(w,'import')(sigCB2d_ggH, ROOT.RooFit.RecycleConflictNodes())
                    getattr(w,'import')(sigCB2d_VBF, ROOT.RooFit.RecycleConflictNodes())

        if (self.is2D == 0):
		    bkg_vz.SetNameTitle("bkg_vz","bkg_vz")
		    bkg_ttbar.SetNameTitle("bkg_ttbar","bkg_ttbar")
		    bkg_zjets.SetNameTitle("bkg_zjets","bkg_zjets")
            	    getattr(w,'import')(bkg_vz, ROOT.RooFit.RecycleConflictNodes())
            	    getattr(w,'import')(bkg_ttbar, ROOT.RooFit.RecycleConflictNodes())
            	    getattr(w,'import')(bkg_zjets, ROOT.RooFit.RecycleConflictNodes())

        if (self.is2D == 1):
                    bkg2d_vz.SetNameTitle("bkg_vz","bkg_vz")
                    bkg2d_ttbar.SetNameTitle("bkg_ttbar","bkg_ttbar")
                    bkg2d_zjets.SetNameTitle("bkg_zjets","bkg_zjets")
                    getattr(w,'import')(bkg2d_vz,ROOT.RooFit.RecycleConflictNodes())
                    getattr(w,'import')(bkg2d_ttbar,ROOT.RooFit.RecycleConflictNodes())
                    getattr(w,'import')(bkg2d_zjets,ROOT.RooFit.RecycleConflictNodes())

        getattr(w,'import')(rfvSigRate_ggH, ROOT.RooFit.RecycleConflictNodes())
        getattr(w,'import')(rfvSigRate_VBF, ROOT.RooFit.RecycleConflictNodes())
        getattr(w,'import')(rfvSigRate_zjets, ROOT.RooFit.RecycleConflictNodes())
        getattr(w,'import')(rfvSigRate_vz, ROOT.RooFit.RecycleConflictNodes())

        zz2l2q_mass.setRange(self.low_M,self.high_M)

        w.writeToFile(name_ShapeWS)

        ## --------------------------- DATACARDS -------------------------- ##

        rates = {}
        rates['ggH'] = sigRate_ggH_Shape
        rates['qqH'] = sigRate_VBF_Shape

        rates['vz']  = bkgRate_vz_Shape
        rates['ttbar']  = bkgRate_ttbar_Shape
        rates['zjets'] = bkgRate_zjets_Shape

        ## If the channel is not declared in inputs, set rate = 0
        if not self.ggH_chan and not self.all_chan :  sigRate_ggH_Shape = 0
        if not self.qqH_chan:  sigRate_VBF_Shape = 0
        ## bkg
        if not self.vz_chan:  bkgRate_vz_Shape = 0
        if not self.ttbar_chan:  bkgRate_ttbar_Shape = 0
        if not self.zjets_chan: bkgRate_zjets_Shape = 0

        ## Write Datacards
        systematics.setSystematics(rates)

        fo = open( name_Shape, "wb")
        self.WriteDatacard(fo,theInputs, name_ShapeWS2, rates, data_obs.numEntries(), self.is2D )
        systematics.WriteSystematics(fo, theInputs, rates, int(ttbar_MuEG_data.Integral("width")/50) )
        systematics.WriteShapeSystematics(fo,theInputs)
        fo.close()


    def WriteDatacard(self,file,theInputs,nameWS,theRates,obsEvents,is2D):

        numberSig = self.numberOfSigChan(theInputs)
        numberBg  = self.numberOfBgChan(theInputs)

        file.write("imax 1\n")
        file.write("jmax {0}\n".format(numberSig+numberBg-1))
        file.write("kmax *\n")

        file.write("------------\n")
        file.write("shapes * * {0} w:$PROCESS \n".format(nameWS))
        file.write("------------\n")

        file.write("bin {0} \n".format(self.appendName))
        file.write("observation {0} \n".format(obsEvents))

        file.write("------------\n")
        file.write("## mass window [{0},{1}] \n".format(self.low_M,self.high_M))
        file.write("bin ")

        channelList=['ggH','qqH','vz','ttbar','zjets']
        channelName1D=['ggH_hzz','qqH_hzz','bkg_vz','bkg_ttbar','bkg_zjets']
        #channelName2D=['ggH_hzz','qqH_hzz','bkg2d_vz','bkg2d_ttbar','bkg2d_zjets']
        channelName2D=['ggH_hzz','qqH_hzz','bkg_vz','bkg_ttbar','bkg_zjets']

        for chan in channelList:
            if theInputs[chan]:
                file.write("{0} ".format(self.appendName))
            else:
                if chan.startswith("ggH") and theInputs["all"] :
                    file.write("{0} ".format(self.appendName))
        file.write("\n")

        file.write("process ")

        i=0
        if not (self.is2D == 1):
            for chan in channelList:
                if theInputs[chan]:
                    file.write("{0} ".format(channelName1D[i]))
                i+=1
        else:
            for chan in channelList:
                if theInputs[chan]:
                    file.write("{0} ".format(channelName2D[i]))
                    i+=1
                else:
                    if chan.startswith("ggH") and theInputs["all"] :
                        file.write("{0} ".format(channelName2D[i]))
                        i+=1

        file.write("\n")

        processLine = "process "

        for x in range(-numberSig+1,1):
            processLine += "{0} ".format(x)

        for y in range(1,numberBg+1):
            processLine += "{0} ".format(y)

        file.write(processLine)
        file.write("\n")

        file.write("rate ")
        for chan in channelList:
            if theInputs[chan] or (chan.startswith("ggH") and theInputs["all"]):
                file.write("{0:.4f} ".format(theRates[chan]))
        file.write("\n")
        file.write("------------\n")



    def numberOfSigChan(self,inputs):

        counter=0

        if inputs['ggH']: counter+=1
        if inputs['qqH']: counter+=1

        return counter

    def numberOfBgChan(self,inputs):

        counter=0

        if inputs['vz']:  counter+=1
        if inputs['zjets']: counter+=1
        if inputs['ttbar']: counter+=1

        return counter

