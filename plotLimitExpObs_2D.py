from ROOT import *
from utils import *
gROOT.SetBatch(True)
from tdrStyle import *
setTDRStyle()

import sys
import os
from array import array



start_mass = sys.argv[1]
end_val = sys.argv[2]
step_sizes = sys.argv[3]
year = sys.argv[4]
blind = sys.argv[5]
datacard = sys.argv[6]
SearchString4Datacard = sys.argv[7]
outputDir = sys.argv[8]

mass = array('d',[])
zeros = array('d',[])
exp_p2 = array('d',[])
exp_p1 = array('d',[])
exp = array('d',[])
obs = array('d',[])
exp_m1 = array('d',[])
exp_m2 = array('d',[])
exp1D = array('d',[])

logger.info('start_mass: {}'.format(start_mass))
logger.info('end_val: {}'.format(end_val))
logger.info('step_sizes: {}'.format(step_sizes))
logger.info('year: {}'.format(year))

GetZombieMassPointList = []

for current_mass in range(int(start_mass), int(end_val), int(step_sizes)):
        m = current_mass

        InputFile = "./datacards_HIG_23_001/cards_{year}/HCG/{mH}/higgsCombine.{name}.AsymptoticLimits.mH{mH}.root".format(year = year, mH = current_mass, name = SearchString4Datacard.replace("REPLACEMASS",str(current_mass)))

        # check if InputFile exists
        if not os.path.isfile(InputFile):
            logger.error("File does not exist: {}".format(InputFile))
            GetZombieMassPointList.append(current_mass)
            continue

        logger.info(InputFile)
        f = TFile(InputFile,"READ")

        # check if the input file is not zombie
        if f.IsZombie():
            logger.error("File is zombie: {}".format(InputFile))
            GetZombieMassPointList.append(current_mass)
            continue

        t = f.Get("limit")

        scale = 1.0

        mass.append(float(m))
        zeros.append(0.0)


        t.GetEntry(2)
        thisexp = t.limit*scale
        exp.append(thisexp)


        t.GetEntry(0)
        exp_m2.append(thisexp-t.limit*scale)

        t.GetEntry(1)
        exp_m1.append(thisexp-t.limit*scale)

        t.GetEntry(3)
        exp_p1.append(t.limit*scale-thisexp)

        t.GetEntry(4)
        exp_p2.append(t.limit*scale-thisexp)

logger.info('mass: {}'.format(mass))
logger.info('exp: {}'.format(exp))

v_mass = TVectorD(len(mass),mass)
v_zeros = TVectorD(len(zeros),zeros)
v_exp_p2 = TVectorD(len(exp_p2),exp_p2)
v_exp_p1 = TVectorD(len(exp_p1),exp_p1)
v_exp = TVectorD(len(exp),exp)
v_exp_m1 = TVectorD(len(exp_m1),exp_m1)
v_exp_m2 = TVectorD(len(exp_m2),exp_m2)

c = TCanvas("c","c",1000,800)
c.SetLogy()
c.SetGridx()
c.SetGridy()

c.SetRightMargin(0.06)
c.SetLeftMargin(0.15)

dummy = TH1D("dummy","dummy", 1, 400,3000)
dummy.SetBinContent(1,0.0)
dummy.GetXaxis().SetTitle('m(X)[GeV]')
dummy.GetYaxis().SetTitle('#sigma(pp#rightarrowX)#timesBR(X#rightarrowZZ) [pb]')
dummy.GetYaxis().SetTitleSize(0.05)
dummy.SetLineColor(0)
dummy.SetLineWidth(0)
dummy.SetFillColor(0)
if "Resolved" in SearchString4Datacard:
     dummy.SetMinimum(0.0001)
     dummy.SetMaximum(50.0)
else:
     dummy.SetMinimum(0.0001)
     dummy.SetMaximum(1)
dummy.GetXaxis().SetMoreLogLabels(kTRUE)
dummy.GetXaxis().SetNoExponent(kTRUE)
dummy.GetXaxis().SetTitleSize(0.05)
dummy.Draw()


gr_exp2 = TGraphAsymmErrors(v_mass,v_exp,v_zeros,v_zeros,v_exp_m2,v_exp_p2)
gr_exp2.SetLineColor(kYellow)
gr_exp2.SetFillColor(kYellow)
gr_exp2.Draw("e3same")

gr_exp1 = TGraphAsymmErrors(v_mass,v_exp,v_zeros,v_zeros,v_exp_m1,v_exp_p1)
gr_exp1.SetLineColor(kGreen)
gr_exp1.SetFillColor(kGreen)
gr_exp1.Draw("e3same")

gr_exp = TGraphAsymmErrors(v_mass,v_exp,v_zeros,v_zeros,v_zeros,v_zeros)
gr_exp.SetLineColor(1)
gr_exp.SetLineWidth(2)
gr_exp.SetLineStyle(2)
gr_exp.Draw("Csame")

latex2 = TLatex()
latex2.SetNDC()
latex2.SetTextSize(0.5*c.GetTopMargin())
latex2.SetTextFont(42)
latex2.SetTextAlign(31) # align right
#latex2.DrawLatex(0.87, 0.95,"12.9 fb^{-1} (13 TeV)")
if year == "2016": latex2.DrawLatex(0.87, 0.95,"35.9 fb^{-1} (13 TeV)")
elif year == "2017": latex2.DrawLatex(0.87, 0.95,"41.5 fb^{-1} (13 TeV)")
elif year == "2018": latex2.DrawLatex(0.87, 0.95,"59.7 fb^{-1} (13 TeV)")
elif year == "run2": latex2.DrawLatex(0.87, 0.95,"137.1 fb^{-1} (13 TeV)")
else: latex2.DrawLatex(0.87, 0.95,"xx fb^{-1} (xx TeV)")
latex2.SetTextSize(0.9*c.GetTopMargin())
latex2.SetTextFont(62)
latex2.SetTextAlign(11) # align right
latex2.DrawLatex(0.27, 0.85, "CMS")
latex2.SetTextSize(0.7*c.GetTopMargin())
latex2.SetTextFont(52)
latex2.SetTextAlign(11)
latex2.DrawLatex(0.25, 0.8, "Preliminary")

legend = TLegend(.60,.70,.90,.90)
#legend.AddEntry(gr_obs , "Observed 95% CL ", "l")
legend.AddEntry(gr_exp , "Expected 95% CL ", "l")
legend.AddEntry(gr_exp1 , "#pm 1#sigma", "f")
legend.AddEntry(gr_exp2 , "#pm 2#sigma", "f")
legend.SetShadowColor(0)
legend.SetFillColor(0)
legend.SetLineColor(0)
legend.Draw("same")

gPad.RedrawAxis()

outputDir = os.path.join(outputDir, 'figs')
OutputFileName = 'highMassLimit_spin0_2D_13TeV_{year}_{name}'.format(year = year, name = SearchString4Datacard.replace("_mHREPLACEMASS",""))

c.SaveAs(outputDir + '/' + OutputFileName+".pdf")
c.SaveAs(outputDir + '/' + OutputFileName+".png")
c.SaveAs(outputDir + '/' + OutputFileName+".C")
c.SaveAs(outputDir + '/' + OutputFileName+".root")

if len(GetZombieMassPointList) > 0:
    logger.error("Mass Point for which either combine root file does not exists or its zombie: {}".format(GetZombieMassPointList))
