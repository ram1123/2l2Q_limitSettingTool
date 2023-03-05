#! /usr/bin/env python
import math


## ------------------------------------
##  systematics class
## ------------------------------------

class systematicsClass:

    def __init__(self,theMass,theForXSxBR,theInputs, DEBUG):

        self.ID_2muResolved = 'mumuqq_Resolved'
        self.ID_2eResolved = 'eeqq_Resolved'
        self.ID_2muMerged = 'mumuqq_Merged'
        self.ID_2eMerged = 'eeqq_Merged'

        self.sqrts = theInputs['sqrts']
        self.decayChan = theInputs['decayChannel']
        self.cat = theInputs['cat']
        self.mH = theMass
        self.isForXSxBR = theForXSxBR
        self.model = theInputs['model']

        self.muSelError = 0.0
        self.eSelError = 0.0

        self.qqVV_scaleSys = 0.0
        self.qqVV_pdfSys = 0.0
        self.ggVV_scaleSys = 0.0
        self.ggVV_pdfSys = 0.0

        self.lumiUncertainty = theInputs['lumiUnc']
        self.sel_muontrig = theInputs['muonTrigUnc']
        self.sel_muonfull = theInputs['muonFullUnc']

        self.sel_eletrig = theInputs['elecTrigUnc']
        self.sel_elefull = theInputs['elecFullUnc']

        self.zjetsAlphaLow = theInputs['zjetsAlphaLow']
        self.zjetsAlphaHigh = theInputs['zjetsAlphaHigh']

        self.gghJESLow = theInputs['gghJESLow']
        self.gghJESHigh = theInputs['gghJESHigh']
        self.vbfJESLow = theInputs['vbfJESLow']
        self.vbfJESHigh = theInputs['vbfJESHigh']
        self.vzJESLow = theInputs['vzJESLow']
        self.vzJESHigh = theInputs['vzJESHigh']

        self.gghBTAGLow = theInputs['gghBTAGLow']
        self.gghBTAGHigh = theInputs['gghBTAGHigh']
        self.vbfBTAGLow = theInputs['vbfBTAGLow']
        self.vbfBTAGHigh = theInputs['vbfBTAGHigh']
        self.vzBTAGLow = theInputs['vzBTAGLow']
        self.vzBTAGHigh = theInputs['vzBTAGHigh']

        self.theoryHighMass = 1

        self.qqVV_scaleSys = 1. + 0.01*math.sqrt((self.mH - 20.)/13.)
        self.qqVV_pdfSys = 1. + 0.0035*math.sqrt(self.mH - 30.)
        self.DEBUG = DEBUG


    def setSystematics(self,rates):

        self.rateBkg_vz = rates['vz']
        self.rateBkg_ttbar = rates['ttbar']
        self.rateBkg_zjets = rates['zjets']

        self.muSelError = 1 + math.sqrt( self.sel_muonfull*self.sel_muonfull + self.sel_muontrig*self.sel_muontrig )
        self.eSelError = 1 + math.sqrt( self.sel_elefull*self.sel_elefull + self.sel_eletrig*self.sel_eletrig )

    def Write_Systematics_Line(self,systLine,theFile,theInputs):
        if self.DEBUG: print("~~~~~~~~~~~~~~~~~")
        channelList=['ggH','qqH','vz','ttbar','zjets']

        if theInputs["all"]:
            channelList=['ggH','qqH','vz','ttbar','zjets']

        for chan in channelList:
            if theInputs[chan] or (chan.startswith("ggH") and theInputs["all"]):
                if self.DEBUG: print(chan, systLine[chan])
                theFile.write(systLine[chan])

        theFile.write("\n")

    def Build_lumi(self,theFile,theInputs):
        if(self.sqrts == 7):
            theFile.write("lumi_7TeV lnN ")
        elif (self.sqrts == 8):
            theFile.write("lumi_8TeV lnN ")
        elif (self.sqrts == 13):
            theFile.write("lumi_13TeV lnN ")
        else:
            raise RuntimeError("Unknown sqrts in systematics!")

        systLine={'ggH':"{0} ".format(self.lumiUncertainty)}
        systLine['qqH']  = "{0} ".format(self.lumiUncertainty)
        systLine['zjets']= "- "
        systLine['ttbar']= "- "
        systLine['vz']  = "{0} ".format(self.lumiUncertainty)

        self.Write_Systematics_Line(systLine,theFile,theInputs)

    def Write_pdf_qqbar(self,theFile,theInputs):

        theFile.write("pdf_qqbar lnN ")

        if not self.isForXSxBR:
            systLine={'ggH':"- "}
            systLine['qqH']  = "1.021 "#"{0:.4f} ".format(1. + (self.CSpdfErrPlus_vbf-self.CSpdfErrMinus_vbf)/2.)
            systLine['zjets']= "- "
            systLine['ttbar']= "- "
            systLine['vz']  = "1.03 "
            self.Write_Systematics_Line(systLine,theFile,theInputs)

        elif self.isForXSxBR:
            systLine={'ggH':"- "}
            systLine['qqH']  = "- "
            systLine['zjets']= "- "
            systLine['ttbar']= "- "
            systLine['vz']  = "1.03 "
            self.Write_Systematics_Line(systLine,theFile,theInputs)

    def Write_pdf_gg(self,theFile,theInputs):

        if not self.isForXSxBR:

            theFile.write("pdf_gg lnN ")

            systLine={'ggH':"1.0252/0.9718 "}
            systLine['qqH']  = "- "
            systLine['zjets']= "- "
            systLine['ttbar']= "- "
            systLine['vz']  = "- "

            self.Write_Systematics_Line(systLine,theFile,theInputs)

    def Write_pdf_hzz2l2q_accept(self,theFile,theInputs):

        theFile.write("pdf_hzz2l2q_accept lnN ")
        systLine={'ggH':"1.02 "}
        systLine['qqH']  = "1.02 "
        systLine['zjets']= "- "
        systLine['ttbar']= "- "
        systLine['vz']  = "- "

        self.Write_Systematics_Line(systLine,theFile,theInputs)

    def Write_QCDscale_vz(self,theFile,theInputs):

        theFile.write("QCDscale_vz lnN ")
        systLine={'ggH':"- "}#"{0:.4f} ".format(1. + (self.CSscaleErrPlus_gg-self.CSscaleErrMinus_gg)/2.)}
        systLine['qqH']  = "- "
        systLine['zjets']= "- "
        systLine['ttbar']= "- "
        systLine['vz']  = "1.032 "

        self.Write_Systematics_Line(systLine,theFile,theInputs)

    def Write_QCDscale_ggH(self,theFile,theInputs):

        theFile.write("QCDscale_ggH lnN ")

        #systLine={'ggH':"1.1067/0.8874 "}#"{0:.4f} ".format(1. + (self.CSscaleErrPlus_gg-self.CSscaleErrMinus_gg)/2.)}
        systLine={'ggH':"1.039/0.961"}#"{0:.4f} ".format(1. + (self.CSscaleErrPlus_gg-self.CSscaleErrMinus_gg)/2.)}
        systLine['qqH']  = "- "
        systLine['zjets']= "- "
        systLine['ttbar']= "- "
        systLine['vz']  = "- "

        self.Write_Systematics_Line(systLine,theFile,theInputs)

    def Write_QCDscale_qqH(self,theFile,theInputs):

        theFile.write("QCDscale_qqH lnN ")

        systLine={'ggH':"- "}
        #systLine['qqH']  = "1.0065/0.9982 "#"{0:.4f} ".format(1. + (self.CSscaleErrPlus_vbf-self.CSscaleErrMinus_vbf)/2.)
        systLine['qqH']  = "1.004/0.997 "#"{0:.4f} ".format(1. + (self.CSscaleErrPlus_vbf-self.CSscaleErrMinus_vbf)/2.)
        systLine['zjets']= "- "
        systLine['ttbar']= "- "
        systLine['vz']  = "- "

        self.Write_Systematics_Line(systLine,theFile,theInputs)


    def Write_QCDscale_VV(self,theFile,theInputs):

        theFile.write("QCDscale_VV lnN ")

        systLine={'ggH':"- "}
        systLine['qqH']  = "- "
        systLine['vz'] = "1.032/0.958"
        systLine['zjets']= "- "
        systLine['ttbar']= "- "

        self.Write_Systematics_Line(systLine,theFile,theInputs)

    def Write_BRhiggs_hzz2l2q(self,theFile,theInputs):

        theFile.write("BRhiggs_hzz2l2q lnN ")

        systLine={'ggH':"1.02 "}
        systLine['qqH']  = "1.02 "
        systLine['zjets']= "- "
        systLine['ttbar']= "- "
        systLine['vz']  = "- "

        self.Write_Systematics_Line(systLine,theFile,theInputs)

    def Write_gamma_HVV(self,theFile,theInputs):

        theFile.write("gamma_HVV lnN ")

        systLine={'ggH':"{0:.4f} ".format(self.BRErr_HVV)}
        systLine['qqH']  = "{0:.4f} ".format(self.BRErr_HVV)
        systLine['zjets']= "- "
        systLine['ttbar']= "- "
        systLine['vz']  = "- "

        self.Write_Systematics_Line(systLine,theFile,theInputs)

    def Write_eff_e(self,theFile,theInputs):

        theFile.write("CMS_eff_e lnN ")

        #systLine={'ggH':"{0:.3f} ".format(self.eSelError)}
        #systLine['qqH']   = "{0:.3f} ".format(self.eSelError)
        #systLine['vz']  = "{0:.3f} ".format(self.eSelError)
        systLine={'ggH':"0.990549/1.00949 "}
        systLine['qqH']   = "0.990549/1.00949 "
        systLine['vz']  = "0.990549/1.00949 "
        systLine['zjets']= "- "
        systLine['ttbar']= "- "


        self.Write_Systematics_Line(systLine,theFile,theInputs)

    def Write_eff_m(self,theFile,theInputs):

        theFile.write("CMS_eff_m lnN ")
        systLine={'ggH':"{0:.3f} ".format(self.muSelError)}
        systLine['qqH']  = "{0:.3f} ".format(self.muSelError)
        systLine['zjets']= "- "
        systLine['ttbar']= "- "
        systLine['vz']  = "{0:.3f} ".format(self.muSelError)

        self.Write_Systematics_Line(systLine,theFile,theInputs)


    def Write_CMS_hzz2l2q_Zjets(self,theFile,theInputs):

        channel="resolved"
        if(self.decayChan=="eeqq_Merged" or self.decayChan=="mumuqq_Merged"):
          channel="merged"

        cat = self.cat
        if(self.cat=='vbf_tagged') :
          cat='vbftagged'
        elif(cat=='b_tagged') :
          cat='btagged'

        #changed by Jialin
        #if(channel=="resolved" and cat=="untagged" ) :
        #  theFile.write("eig0_{0}_{1} param  0  1  [-3,3]\n".format(channel,cat))
        #  theFile.write("eig1_{0}_{1} param  0  1  [-3,3]\n".format(channel,cat))
        #  theFile.write("eig2_{0}_{1} param  0  1  [-3,3]\n".format(channel,cat))
        #  theFile.write("eig3_{0}_{1} param  0  1  [-3,3]\n".format(channel,cat))
        #elif(channel=="resolved") :
        #  theFile.write("eig0_{0}_{1} param  0  1  [-3,3]\n".format(channel,cat))
        #  theFile.write("eig1_{0}_{1} param  0  1  [-3,3]\n".format(channel,cat))
        #elif(channel=="merged"):
        #  theFile.write("eig0_{0}_{1} param  0  1  [-3,3]\n".format(channel,cat))
        #  theFile.write("eig1_{0}_{1} param  0  1  [-3,3]\n".format(channel,cat))
        #elif(channel=="merged" and cat=="vbftagged" ):
        #  theFile.write("eig0_{0}_{1} param  0  2  [-3,3]\n".format(channel,cat))
        #  theFile.write("eig1_{0}_{1} param  0  2  [-3,3]\n".format(channel,cat))

        theFile.write("zjetsAlpha_{0}_{1} lnN ".format(channel, cat) )
        systLine={'ggH':"- "}
        systLine['qqH']  = "- "       # JER/JES quadrature alpha binning
        if(channel=="resolved" and cat=="untagged") :
           systLine['zjets']= "1.02 " # 0.02 quadrature per-mil
        if(channel=="resolved" and cat=="btagged") :
           systLine['zjets']= "1.03 " # 0.02 quadrature 0.025
        if(channel=="resolved" and cat=="vbftagged") :
           systLine['zjets']= "1.025 " # 0.02 quadrature 0.015
        ##########
        if(channel=="merged" and cat=="untagged") :
           systLine['zjets']= "1.03 " # 0.01 quadrature 0.0286
        if(channel=="merged" and cat=="btagged") :
           systLine['zjets']= "1.32 " # 0.05 quadrature 0.3175
        if(channel=="merged" and cat=="vbftagged") :
           systLine['zjets']= "1.04 " # 0.03 quadrature double the eigs uncertainty

        systLine['ttbar']= "- "
        systLine['vz']  = "- "
        self.Write_Systematics_Line(systLine,theFile,theInputs)

    def Write_CMS_hzz2l2q_TTbar(self,theFile,theInputs,bkgRate_ttbar_Shape,Nemu):

        channel="Resolved"
        if(self.decayChan=="eeqq_Merged" or self.decayChan=="mumuqq_Merged"):
          channel="Merged"

        cat = self.cat
        if(self.cat=='vbf_tagged') :
          cat='vbftagged'
        elif(cat=='b_tagged') :
          cat='btagged'

        #changed by Jialin
        theFile.write("gmTTbarWW_{0}_{1} gmN {2} ".format(channel,cat,int(Nemu)) )

        systLine={'ggH':"- "}
        systLine['qqH']  = "- "
        systLine['zjets']= "- "
        systLine['ttbar']= "{0} ".format(bkgRate_ttbar_Shape/int(Nemu))
        systLine['vz']  = "- "

        self.Write_Systematics_Line(systLine,theFile,theInputs)

    def Write_CMS_hzz2l2q_vz(self,theFile,theInputs):


        #changed by Jialin
        #theFile.write("Knnlo_nlo_vz lnN ")
#
        #systLine={'ggH':"- "}
        #systLine['qqH']  = "- "
        #systLine['zjets']= "- "
        #systLine['ttbar']= "- "
        #systLine['vz']  = "1.1 "
#
        #self.Write_Systematics_Line(systLine,theFile,theInputs)

        if(self.decayChan=="eeqq_Merged" or self.decayChan=="mumuqq_Merged"):

            theFile.write("CMS_Vtagging lnN ")

            systLine2={'ggH':"0.972/1.028 "}
            systLine2['qqH']  = "0.972/1.028 "
            systLine2['zjets']= "- "
            systLine2['ttbar']= "- "
            systLine2['vz']  = "0.972/1.028 "

            self.Write_Systematics_Line(systLine2,theFile,theInputs)

    def Write_CMS_hzz2l2q_JES(self,theFile,theInputs):
        theFile.write("JES param  0  1  [-3,3]\n")

    def Write_CMS_hzz2l2q_BTAG(self,theFile,theInputs):
        channel="resolved"
        if(self.decayChan=="eeqq_Merged" or self.decayChan=="mumuqq_Merged"):
          channel="merged"

        theFile.write("BTAG_{0} param  0  1  [-3,3]\n".format(channel))

    def Write_CMS_zz2l2q_bkgMELA(self,theFile,theInputs):
        channel="resolved"
        if(self.decayChan=="eeqq_Merged" or self.decayChan=="mumuqq_Merged"):
          channel="merged"

        theFile.write("CMS_zz2l2q_bkgMELA_{0} param 0  1  [-3,3]\n".format(channel))

    def Write_CMS_zz2l2q_sigMELA(self,theFile,theInputs):
        channel="resolved"
        if(self.decayChan=="eeqq_Merged" or self.decayChan=="mumuqq_Merged"):
          channel="merged"

        theFile.write("CMS_zz2l2q_sigMELA_{0} param 0  1  [-3,3]\n".format(channel))

    def WriteSystematics(self,theFile,theInputs, rates, Nemu):

        if theInputs['useLumiUnc']:
            self.Build_lumi(theFile,theInputs)

        if theInputs['usePdf_gg']:
            self.Write_pdf_gg(theFile,theInputs)

        if theInputs['usePdf_qqbar']:
            self.Write_pdf_qqbar(theFile,theInputs)

        if theInputs['usePdf_hzz2l2q_accept']:
            self.Write_pdf_hzz2l2q_accept(theFile,theInputs)

        if theInputs['useQCDscale_VV']:
            self.Write_QCDscale_VV(theFile,theInputs)

        if theInputs['useQCDscale_vz']:
            self.Write_QCDscale_vz(theFile,theInputs)

        if not self.isForXSxBR:
            if theInputs['useQCDscale_ggH'] :
                self.Write_QCDscale_ggH(theFile,theInputs)

        if theInputs['useQCDscale_qqH'] :
                self.Write_QCDscale_qqH(theFile,theInputs)

    ## Higgs BR
        if theInputs['useBRhiggs_hzz2l2q'] and not self.isForXSxBR :
            self.Write_BRhiggs_hzz2l2q(theFile,theInputs)

    ##  ----------- SELECTION EFFICIENCIES ----------

        if(self.decayChan=="mumuqq_Resolved" or self.decayChan=="mumuqq_Merged"):
            self.Write_eff_m(theFile,theInputs)
        if(self.decayChan=="eeqq_Resolved" or self.decayChan=="eeqq_Merged"):
            self.Write_eff_e(theFile,theInputs)

        self.Write_CMS_hzz2l2q_Zjets(theFile,theInputs)

        # FIXME: Try to switch off from .txt file
        # bkgRate_ttbar_Shape=rates['ttbar']
        # self.Write_CMS_hzz2l2q_TTbar(theFile,theInputs,bkgRate_ttbar_Shape,Nemu)

        self.Write_CMS_hzz2l2q_vz(theFile,theInputs)

        if theInputs['useCMS_zz2l2q_bkgMELA']:
            self.Write_CMS_zz2l2q_bkgMELA(theFile,theInputs)
        if theInputs['useCMS_zz2l2q_sigMELA']:
            self.Write_CMS_zz2l2q_sigMELA(theFile,theInputs)

        self.Write_CMS_hzz2l2q_JES(theFile,theInputs)
        #changed by Jialin
        #self.Write_CMS_hzz2l2q_BTAG(theFile,theInputs)


    def WriteShapeSystematics(self,theFile,theInputs):

        meanCB_e_errPerCent = theInputs['CMS_zz2l2q_mean_e_err']
        sigmaCB_e_errPerCent = theInputs['CMS_zz2l2q_sigma_e_err']
        meanCB_m_errPerCent = theInputs['CMS_zz2l2q_mean_m_err']
        sigmaCB_m_errPerCent = theInputs['CMS_zz2l2q_sigma_m_err']
        meanCB_j_errPerCent = theInputs['CMS_zz2l2q_mean_j_err']
        sigmaCB_j_errPerCent = theInputs['CMS_zz2l2q_sigma_j_err']
        meanCB_J_errPerCent = theInputs['CMS_zz2lJ_mean_J_err']
        sigmaCB_J_errPerCent = theInputs['CMS_zz2lJ_sigma_J_err']

        if theInputs['useCMS_zz2l2q_mean']:
            theFile.write("CMS_zz2l2q_mean_j_sig param 0.0 1.0 \n")
            theFile.write("## CMS_zz2l2q_mean_j_err = {0} \n".format(meanCB_j_errPerCent))
        if theInputs['useCMS_zz2l2q_sigma']:
            theFile.write("CMS_zz2l2q_sigma_j_sig param 0.0 1.0 \n")
            theFile.write("## CMS_zz2l2q_sigma_j_err param {0} \n".format(sigmaCB_j_errPerCent))

        if theInputs['useCMS_zz2lJ_mean']:
            theFile.write("CMS_zz2lJ_mean_J_sig param 0.0 1.0 \n")
            theFile.write("## CMS_zz2lJ_mean_J_err = {0} \n".format(meanCB_J_errPerCent))
        if theInputs['useCMS_zz2lJ_sigma']:
            theFile.write("CMS_zz2lJ_sigma_J_sig param 0.0 1.0 \n")
            theFile.write("## CMS_zz2lJ_sigma_J_err param {0} \n".format(sigmaCB_J_errPerCent))

        if( self.decayChan == self.ID_2muResolved or self.decayChan == self.ID_2muMerged):
            theFile.write("CMS_zz2l2q_mean_m_sig param 0.0 1.0 \n")
            theFile.write("## CMS_zz2l2l_mean_m_err param {0} \n".format(meanCB_m_errPerCent))
            theFile.write("CMS_zz2l2q_sigma_m_sig param 0.0 1.0 \n")
            theFile.write("## CMS_zz2l2l_sigma_m_err param {0} \n".format(sigmaCB_m_errPerCent))

        if( self.decayChan == self.ID_2eResolved or self.decayChan == self.ID_2eMerged):
            theFile.write("CMS_zz2l2q_mean_e_sig param 0.0 1.0 \n")
            theFile.write("## CMS_zz2l2q_mean_e_err = {0} \n".format(meanCB_e_errPerCent))
            theFile.write("CMS_zz2l2q_sigma_e_sig param 0.0 1.0 \n")
            theFile.write("## CMS_zz2l2q_sigma_e_err = {0} \n".format(sigmaCB_e_errPerCent))
