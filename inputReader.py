#!/usr/bin/python
import os

# from ROOT import *

## ---------------------------------------------------------------
## card reader class
## ---------------------------------------------------------------

class inputReader:

    def __init__(self, inputTextFile):

        if not os.path.exists(inputTextFile):
            raise RuntimeError("File {0} does not exist!!!".format(inputTextFile))


        # input file
        self.theInput = inputTextFile
        # model
        self.model = ""
        # decay channel
        self.decayChan = ""
        self.cat = ""
        # lumi
        self.lumi = -999.9
        # sqrts
        self.sqrts = -999.9
        # channels
        self.all_chan = False
        self.ggH_chan = False
        self.qqH_chan = False
        self.zjets_chan = False
        self.ttbar_chan = False
        self.vz_chan = False
        # rates
        self.zjets_lumi = -999.9
        self.ttbar_lumi = -999.9
        self.vz_lumi = -999.9
        # zjets shape
        self.p0_zjets = -999.9
        self.p1_zjets = -999.9
        self.l0_zjets = -999.9
        self.l1_zjets = -999.9

        self.p0_alt_zjets = -999.9
        self.p1_alt_zjets = -999.9
        self.l0_alt_zjets = -999.9
        self.l1_alt_zjets = -999.9

        # alpha method cov matrix elements
        self.p0p0_cov_zjets = 0
        self.p0l0_cov_zjets = 0
        self.p0p1_cov_zjets = 0
        self.p0l1_cov_zjets = 0
        self.l0l0_cov_zjets = 0
        self.l0p1_cov_zjets = 0
        self.l0l1_cov_zjets = 0
        self.p1p1_cov_zjets = 0
        self.p1l1_cov_zjets = 0
        self.l1l1_cov_zjets = 0

        # z+jets alpha method uncertainty
        self.zjetsAlphaLow = -999.9
        self.zjetsAlphaHigh = -999.9

        # systematics
        self.lumiUnc = -999.9
        #self.muonFullUnc = -999.9
        self.muonFullUnc = {}
        self.muonTrigUnc = -999.9
        #self.elecFullUnc = -999.9
        self.elecFullUnc = {}
        self.elecTrigUnc = -999.9

        self.CMS_zz2l2q_mean_m_err = -999.9
        self.CMS_zz2l2q_sigma_m_err = -999.9
        self.CMS_zz2l2q_mean_e_err = -999.9
        self.CMS_zz2l2q_sigma_e_err = -999.9
        ###
        self.CMS_zz2l2q_mean_j_err = -999.9
        self.CMS_zz2l2q_sigma_j_err = -999.9
        ###
        self.CMS_zz2lJ_mean_J_err = -999.9
        self.CMS_zz2lJ_sigma_J_err = -999.9

        self.useLumiUnc = False
        self.usePdf_gg = False
        self.usePdf_qqbar = False
        self.usePdf_hzz2l2q_accept = False
        self.useQCDscale_ggH = False
        self.useQCDscale_qqH = False
        self.useTheoryUncXS_HighMH = False
        self.useQCDscale_VV = False
        self.useBRhiggs_hzz2l2q = False
        self.useCMS_eff = False
        self.useCMS_hzz2l2q_Zjets = False
        self.useCMS_zz2l2q_bkgMELA = False
        self.useCMS_zz2l2q_sigMELA = False
        self.useCMS_zz2l2q_mean = False
        self.useCMS_zz2l2q_sigma = False
        self.useCMS_zz2lJ_mean = False
        self.useCMS_zz2lJ_sigma = False
        self.useQCDscale_vz = False
        self.useAk4SplitJEC = False
        self.useAk8SplitJEC = False
        self.usedeepjetsf = False
        self.usedeepjetsfcorrelated = False
        # --- VBFtag/Btag systematics

        self.gghJESLow = -999.9
        self.gghJESHigh = -999.9
        self.vbfJESLow = -999.9
        self.vbfJESHigh = -999.9
        self.vzJESLow = -999.9
        self.vzJESHigh = -999.9

        self.gghBTAGLow = -999.9
        self.gghBTAGHigh = -999.9
        self.vbfBTAGLow = -999.9
        self.vbfBTAGHigh = -999.9
        self.vzBTAGLow = -999.9
        self.vzBTAGHigh = -999.9

        ####split JEC systematics for ak4
        self.Abs = {}
        self.Abs_year = {}
        self.BBEC1 = {}
        self.BBEC1_year = {}
        self.EC2 = {}
        self.EC2_year = {}
        self.FlavQCD = {}
        self.HF = {}
        self.HF_year = {}
        self.RelBal = {}
        self.RelSample_year = {}
        self.splitproccess = ['ggH','qqH','ttbar','vz']
        self.SplitSource = ['Abs','BBEC1','EC2','FlavQCD', 'HF', 'RelBal','Abs_year','BBEC1_year','EC2_year','HF_year','RelSample_year']
        for process in self.splitproccess:
            self.Abs[process] = -999.9
            self.Abs_year[process] = -999.99
            self.BBEC1[process] = -999.99
            self.BBEC1_year[process] = -999.99
            self.EC2[process] = -999.99
            self.EC2_year[process] = -999.99
            self.FlavQCD[process] = -999.99
            self.HF[process] = -999.99
            self.HF_year[process] = -999.99
            self.RelBal[process] = -999.99
            self.RelSample_year[process] = -999.99

        ####deepjet systematics for ak4
        self.deepjetsf = {}
        self.deepjetsfcorrelated = {}
        self.splitproccess = ['ggH','qqH','ttbar','vz']
        for process in self.splitproccess:
            self.deepjetsf[process] = -999.9
            self.deepjetsfcorrelated[process] = -999.9

    def goodEntry(self,variable):
        if variable == -999.9:
            return False
        else:
            return True


    def parseBoolString(self,theString):
        return theString[0].upper()=='T'

    def readInputs(self):
        for line in open(self.theInput,'r'):
            f = line.split()
            if len(f) < 1: continue

            if f[0].startswith("#"): continue

            if f[0].lower().startswith("model"):

                if f[1].upper() == "SM": self.model = "SM"
                elif f[1].upper() == "SM4": self.model = "SM4"
                elif f[1].upper() == "FF" or f[1].upper() == "FP": self.model = "FF"
                else : raise RuntimeError("Unknow model {0}, choices are SM, SM4, FF".format(f[1].upper()))

            if f[0].lower().startswith("decay"):

                if f[1] == "mumuqq_Resolved": self.decayChan = f[1]
                elif f[1] == "eeqq_Resolved": self.decayChan = f[1]
                elif f[1] == "mumuqq_Merged": self.decayChan = f[1]
                elif f[1] == "eeqq_Merged": self.decayChan = f[1]
                else : raise RuntimeError("Unknown decay channel {0}".format(f[1]))

            if f[0].lower().startswith("cat"):
               self.cat = f[1]

            if f[0].lower().startswith("channels"):
                for chan in f:
                    if chan == f[0]: continue
                    if chan.lower().startswith("ggh"):     self.ggH_chan = True
                    elif chan.lower().startswith("qqh"):   self.qqH_chan = True
                    elif chan.lower().startswith("zjets"): self.zjets_chan = True
                    elif chan.lower().startswith("ttbar"): self.ttbar_chan = True
                    elif chan.lower().startswith("vz"):   self.vz_chan = True
                    elif chan.lower().startswith("all"):   self.all_chan = True
                    else : raise (RuntimeError, "Unknown channel {0}, choices are ggH, qqH, WH, ZH, ttH, qqZZ, ggZZ, zjets".format(chan))

            if f[0].lower().startswith("zjetsshape"):

                if f[1].lower().startswith("p0_zjets"):  self.p0_zjets = f[2]
                if f[1].lower().startswith("p1_zjets"): self.p1_zjets = f[2]
                if f[1].lower().startswith("l0_zjets"): self.l0_zjets = f[2]
                if f[1].lower().startswith("l1_zjets"):  self.l1_zjets = f[2]
                if f[1].lower().startswith("p0_alt_zjets"):  self.p0_alt_zjets = f[2]
                if f[1].lower().startswith("p1_alt_zjets"): self.p1_alt_zjets = f[2]
                if f[1].lower().startswith("l0_alt_zjets"): self.l0_alt_zjets = f[2]
                if f[1].lower().startswith("l1_alt_zjets"):  self.l1_alt_zjets = f[2]

                if f[1].lower().startswith("p0p0_cov_zjets"):  self.p0p0_cov_zjets = f[2]
                if f[1].lower().startswith("p0l0_cov_zjets"):  self.p0l0_cov_zjets = f[2]
                if f[1].lower().startswith("p0p1_cov_zjets"):  self.p0p1_cov_zjets = f[2]
                if f[1].lower().startswith("p0l1_cov_zjets"):  self.p0l1_cov_zjets = f[2]
                if f[1].lower().startswith("l0l0_cov_zjets"):  self.l0l0_cov_zjets = f[2]
                if f[1].lower().startswith("l0p1_cov_zjets"):  self.l0p1_cov_zjets = f[2]
                if f[1].lower().startswith("l0l1_cov_zjets"):  self.l0l1_cov_zjets = f[2]
                if f[1].lower().startswith("p1p1_cov_zjets"):  self.p1p1_cov_zjets = f[2]
                if f[1].lower().startswith("p1l1_cov_zjets"):  self.p1l1_cov_zjets = f[2]
                if f[1].lower().startswith("l1l1_cov_zjets"):  self.l1l1_cov_zjets = f[2]

            if f[0].lower().startswith("systematic"):
                if f[1].lower().startswith("zjet") and f[1].lower().find("alphalow") >= 0 :
                    self.zjetsAlphaLow = f[2]
                if f[1].lower().startswith("zjet") and f[1].lower().find("alphahigh") >= 0 :
                    self.zjetsAlphaHigh = f[2]
                if f[1].lower().startswith("lumiunc"):
                    self.lumiUnc = f[2]
                #if f[1].lower().startswith("muon_full") or f[1].lower().startswith("muonfull"):
                #    self.muonFullUnc = f[2]
                if f[1].lower().startswith("muon_full") or f[1].lower().startswith("muonfull"):
                    for process in ['ggH','qqH','ttbar','vz']:
                        if f[2] == process:
                            self.muonFullUnc[process] = f[3]
                if f[1].lower().startswith("muon_trig") or f[1].lower().startswith("muontrig"):
                    self.muonTrigUnc = f[2]
                #if f[1].lower().startswith("elec_full") or f[1].lower().startswith("elecfull"):
                #    self.elecFullUnc = f[2]
                if f[1].lower().startswith("elec_full") or f[1].lower().startswith("elecfull"):
                    for process in ['ggH','qqH','ttbar','vz']:
                        if f[2] == process:
                            self.elecFullUnc[process] = f[3]
                if f[1].lower().startswith("elec_trig") or f[1].lower().startswith("electrig"):
                    self.elecTrigUnc = f[2]
                if f[1].lower().startswith("param"):
                    if f[2].lower().startswith("cms_zz2l2q_mean_m_err"):
                        self.CMS_zz2l2q_mean_m_err = f[3]
                    if f[2].lower().startswith("cms_zz2l2q_sigma_m_err"):
                        self.CMS_zz2l2q_sigma_m_err = f[3]
                    if f[2].lower().startswith("cms_zz2l2q_mean_e_err"):
                        self.CMS_zz2l2q_mean_e_err = f[3]
                    if f[2].lower().startswith("cms_zz2l2q_sigma_e_err"):
                        self.CMS_zz2l2q_sigma_e_err = f[3]
                    if f[2].lower().startswith("cms_zz2l2q_mean_j_err"):
                        self.CMS_zz2l2q_mean_j_err = f[3]
                    if f[2].lower().startswith("cms_zz2l2q_sigma_j_err"):
                        self.CMS_zz2l2q_sigma_j_err = f[3]
                    if f[2].lower().startswith("cms_zz2lj_mean_j_err"):
                        self.CMS_zz2lJ_mean_J_err = f[3]
                    if f[2].lower().startswith("cms_zz2lj_sigma_j_err"):
                        self.CMS_zz2lJ_sigma_J_err = f[3]
                ###Split JEC uncertainty
                if f[1].lower().startswith('splitjec'):
                    for process in self.splitproccess:
                        if f[2] == process:
                            if f[3]=='Abs':
                                self.Abs[process] = f[4]
                            if f[3]=='Abs_year':
                                self.Abs_year[process] = f[4]
                            if f[3]=='BBEC1':
                                self.BBEC1[process] = f[4]
                            if f[3]=='BBEC1_year':
                                self.BBEC1_year[process] = f[4]
                            if f[3]=='EC2':
                                self.EC2[process] = f[4]
                            if f[3]=='EC2_year':
                                self.EC2_year[process] = f[4]
                            if f[3]=='FlavQCD':
                                self.FlavQCD[process] = f[4]
                            if f[3]=='HF':
                                self.HF[process] = f[4]
                            if f[3]=='HF_year':
                                self.HF_year[process] = f[4]
                            if f[3]=='RelBal':
                                self.RelBal[process] = f[4]
                            if f[3]=='RelSample_year':
                                self.RelSample_year[process] = f[4]
                ###deepjet sf
                if f[1].lower().startswith('deepjetsf'):
                    for process in self.splitproccess:
                        if f[2] == process:
                            self.deepjetsf[process] = f[3]
                if f[1].lower().startswith('deepjetsfcorrelated'):
                    for process in self.splitproccess:
                        if f[2] == process:
                            self.deepjetsfcorrelated[process] = f[3]

                if f[1].lower().startswith("luminosity"):
                    self.useLumiUnc = self.parseBoolString(f[2])
                if f[1].lower().startswith("qcdscale_ggh"):
                    self.useQCDscale_ggH = self.parseBoolString(f[2])
                if f[1].lower().startswith("qcdscale_qqh"):
                    self.useQCDscale_qqH = self.parseBoolString(f[2])
                if f[1].lower().startswith("pdf_hzz2l2q_accept"):
                    self.usePdf_hzz2l2q_accept = self.parseBoolString(f[2])
                if f[1].lower().startswith("qcdscale_vz"):
                    self.useQCDscale_vz = self.parseBoolString(f[2])
                if f[1].lower().startswith("brhiggs_hzz2l2q"):
                    self.useBRhiggs_hzz2l2q = self.parseBoolString(f[2])
                if f[1].lower().startswith("cms_eff"):
                    self.useCMS_eff = self.parseBoolString(f[2])
                if f[1].lower().startswith("cms_hzz2l2q_zjets"):
                    self.useCMS_hzz2l2q_Zjets = self.parseBoolString(f[2])
                if f[1].lower().startswith("cms_zz2l2q_sigmela"):
                    self.useCMS_zz2l2q_sigMELA = self.parseBoolString(f[2])
                if f[1].lower().startswith("cms_zz2l2q_bkgmela"):
                    self.useCMS_zz2l2q_bkgMELA = self.parseBoolString(f[2])
                if f[1].lower().startswith("cms_zz2l2q_mean"):
                    self.useCMS_zz2l2q_mean = self.parseBoolString(f[2])
                if f[1].lower().startswith("cms_zz2l2q_sigma"):
                    self.useCMS_zz2l2q_sigma = self.parseBoolString(f[2])
                if f[1].lower().startswith("cms_zz2lj_mean"):
                    self.useCMS_zz2lJ_mean = self.parseBoolString(f[2])
                if f[1].lower().startswith("cms_zz2lj_sigma"):
                    self.useCMS_zz2lJ_sigma = self.parseBoolString(f[2])
                ##JEC split
                if f[1].startswith("CMS_scale_j_split"):
                    self.useAk4SplitJEC = self.parseBoolString(f[2])
                if f[1].startswith("CMS_scale_J_split"):
                    self.useAk8SplitJEC = self.parseBoolString(f[2])
                ##deepjet sf
                if f[1].startswith("deepjetsf"):
                    self.usedeepjetsf = self.parseBoolString(f[2])
                if f[1].startswith("deepjetsfcorrelated"):
                    self.usedeepjetsfcorrelated = self.parseBoolString(f[2])


            if f[0].lower().startswith("lumi"):
                self.lumi = float(f[1])

            if f[0].lower().startswith("sqrts"):
                self.sqrts = float(f[1])


    def getInputs(self):

        dict = {}

        ## check settings ##
        if self.all_chan and ( self.qqH_chan or self.ggH_chan):
            raise (RuntimeError, "You cannot request to execute ALL signal channels and single channels at the same time. Check inputs!")
        if not self.goodEntry(self.sqrts): raise (RuntimeError, "{0} is not set.  Check inputs!".format("sqrts"))

        if not self.goodEntry(self.zjetsAlphaLow): raise (RuntimeError, "{0} is not set.  Check inputs!".format("self.zjetsAlphaLow"))
        if not self.goodEntry(self.zjetsAlphaHigh): raise (RuntimeError, "{0} is not set.  Check inputs!".format("self.zjetsAlphaHigh"))

        if not self.goodEntry(self.zjets_lumi): self.zjets_lumi = self.lumi
        if not self.goodEntry(self.vz_lumi):   self.vz_lumi = self.lumi
        if not self.goodEntry(self.ttbar_lumi): self.ttbar_lumi = self.lumi

      ## Set dictionary entries to be passed to datacard class ##
        dict['decayChannel'] = str(self.decayChan)
        dict['cat'] = str(self.cat)
        dict['model'] = str(self.model)
        dict['lumi'] = float(self.lumi)
        dict['sqrts'] = float(self.sqrts)

        dict['all'] = self.all_chan
        dict['ggH'] = self.ggH_chan
        dict['qqH'] = self.qqH_chan
        dict['zjets'] = self.zjets_chan
        dict['ttbar'] = self.ttbar_chan
        dict['vz'] = self.vz_chan

        dict['p0_zjets'] = float(self.p0_zjets)
        dict['p1_zjets'] = float(self.p1_zjets)
        dict['l0_zjets'] = float(self.l0_zjets)
        dict['l1_zjets'] = float(self.l1_zjets)

        dict['p0_alt_zjets'] = float(self.p0_alt_zjets)
        dict['p1_alt_zjets'] = float(self.p1_alt_zjets)
        dict['l0_alt_zjets'] = float(self.l0_alt_zjets)
        dict['l1_alt_zjets'] = float(self.l1_alt_zjets)

        dict['zjetsAlphaLow'] = float(self.zjetsAlphaLow)
        dict['zjetsAlphaHigh'] = float(self.zjetsAlphaHigh)

        # l1l1_cov_zjets
        dict['p0p0_cov_zjets'] = float(self.p0p0_cov_zjets)
        dict['p0l0_cov_zjets'] = float(self.p0l0_cov_zjets)
        dict['p0p1_cov_zjets'] = float(self.p0p1_cov_zjets)
        dict['p0l1_cov_zjets'] = float(self.p0l1_cov_zjets)
        dict['l0l0_cov_zjets'] = float(self.l0l0_cov_zjets)
        dict['l0p1_cov_zjets'] = float(self.l0p1_cov_zjets)
        dict['l0l1_cov_zjets'] = float(self.l0l1_cov_zjets)
        dict['p1p1_cov_zjets'] = float(self.p1p1_cov_zjets)
        dict['p1l1_cov_zjets'] = float(self.p1l1_cov_zjets)
        dict['l1l1_cov_zjets'] = float(self.l1l1_cov_zjets)

        dict['gghJESLow'] = float(self.gghJESLow)
        dict['gghJESHigh'] = float(self.gghJESHigh)
        dict['vbfJESLow'] = float(self.vbfJESLow)
        dict['vbfJESHigh'] = float(self.vbfJESHigh)
        dict['vzJESLow'] = float(self.vzJESLow)
        dict['vzJESHigh'] = float(self.vzJESHigh)

        dict['gghBTAGLow'] = float(self.gghBTAGLow)
        dict['gghBTAGHigh'] = float(self.gghBTAGHigh)
        dict['vbfBTAGLow'] = float(self.vbfBTAGLow)
        dict['vbfBTAGHigh'] = float(self.vbfBTAGHigh)
        dict['vzBTAGLow'] = float(self.vzBTAGLow)
        dict['vzBTAGHigh'] = float(self.vzBTAGHigh)

        dict['lumiUnc'] = self.lumiUnc
        #dict['muonFullUnc'] = float(self.muonFullUnc)
        #dict['elecFullUnc'] = float(self.elecFullUnc)

        dict['muonFullUnc'] = {}
        dict['elecFullUnc'] = {}
        #print('check elecFullUnc: {}'.format(self.elecFullUnc))
        #print('check muonFullUnc: {}'.format(self.muonFullUnc))
        
        for key in self.muonFullUnc:        
            dict['muonFullUnc'][key] = self.muonFullUnc[key]
        for key in self.elecFullUnc:
            dict['elecFullUnc'][key] = self.elecFullUnc[key]

        dict['muonTrigUnc'] = float(self.muonTrigUnc)
        dict['elecTrigUnc'] = float(self.elecTrigUnc)

        dict['useLumiUnc'] = self.useLumiUnc
        dict['usePdf_hzz2l2q_accept'] = self.usePdf_hzz2l2q_accept
        dict['useQCDscale_ggH'] = self.useQCDscale_ggH
        dict['useQCDscale_qqH'] = self.useQCDscale_qqH
        dict['useQCDscale_vz'] = self.useQCDscale_vz #changed by Jialin
        dict['useQCDscale_VV'] = self.useQCDscale_VV
        dict['useBRhiggs_hzz2l2q'] = self.useBRhiggs_hzz2l2q
        dict['useCMS_eff'] = self.useCMS_eff
        dict['useCMS_hzz2l2q_Zjets'] = self.useCMS_hzz2l2q_Zjets
        dict['useCMS_zz2l2q_bkgMELA'] = self.useCMS_zz2l2q_bkgMELA
        dict['useCMS_zz2l2q_sigMELA'] = self.useCMS_zz2l2q_sigMELA
        dict['useCMS_zz2l2q_mean'] = self.useCMS_zz2l2q_mean
        dict['useCMS_zz2l2q_sigma'] = self.useCMS_zz2l2q_sigma
        dict['useCMS_zz2lJ_mean'] = self.useCMS_zz2lJ_mean
        dict['useCMS_zz2lJ_sigma'] = self.useCMS_zz2lJ_sigma
        dict['usePdf_qqbar'] = True
        dict['usePdf_gg'] = True
        dict['useTheoryUncXS_HighMH'] = True
        ##JEC split
        dict['useAk4SplitJEC'] = self.useAk4SplitJEC
        dict['useAk8SplitJEC'] = self.useAk8SplitJEC
        ##deepjet sf
        dict['usedeepjetsf'] = self.usedeepjetsf
        dict['usedeepjetsfcorrelated'] = self.usedeepjetsfcorrelated

        dict['CMS_zz2l2q_mean_m_err'] = float(self.CMS_zz2l2q_mean_m_err)
        dict['CMS_zz2l2q_sigma_m_err'] = float(self.CMS_zz2l2q_sigma_m_err)
        dict['CMS_zz2l2q_mean_e_err'] = float(self.CMS_zz2l2q_mean_e_err)
        dict['CMS_zz2l2q_sigma_e_err'] = float(self.CMS_zz2l2q_sigma_e_err)
        dict['CMS_zz2l2q_mean_j_err'] = float(self.CMS_zz2l2q_mean_j_err)
        dict['CMS_zz2l2q_sigma_j_err'] = float(self.CMS_zz2l2q_sigma_j_err)
        dict['CMS_zz2lJ_mean_J_err'] = float(self.CMS_zz2lJ_mean_J_err)
        dict['CMS_zz2lJ_sigma_J_err'] = float(self.CMS_zz2lJ_sigma_J_err)

        ##JEC split and deepjet valus
        dict['deepjetsf'] = {}
        dict['deepjetsfcorrelated'] = {}
        for source in self.SplitSource:
            dict[source] = {}
        for process in self.splitproccess:
            dict['Abs'][process] =            (self.Abs[process])
            dict['Abs_year'][process] =       (self.Abs_year[process])
            dict['BBEC1'][process] =          (self.BBEC1[process])
            dict['BBEC1_year'][process] =     (self.BBEC1[process])
            dict['EC2'][process] =            (self.EC2[process])
            dict['EC2_year'][process] =       (self.EC2_year[process])
            dict['FlavQCD'][process] =        (self.FlavQCD[process])
            dict['HF'][process] =             (self.HF[process])
            dict['HF_year'][process] =        (self.HF_year[process])
            dict['RelBal'][process] =         (self.RelBal[process])
            dict['RelSample_year'][process] = (self.RelSample_year[process])
        
            ##deepjet sf value
            dict['deepjetsf'][process] = (self.deepjetsf[process])
            dict['deepjetsfcorrelated'][process] = (self.deepjetsfcorrelated[process])


        return dict
