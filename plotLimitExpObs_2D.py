from ROOT import *
#ROOT.SetBatch(True)
from tdrStyle import *
setTDRStyle()

import sys
from array import array

import common_strings_pars


start_mass = sys.argv[1]
end_val = sys.argv[2]
step_sizes = sys.argv[3]
year = sys.argv[4]

mass = array('d',[])
zeros = array('d',[])
exp_p2 = array('d',[])
exp_p1 = array('d',[])
exp = array('d',[])
obs = array('d',[])
exp_m1 = array('d',[])
exp_m2 = array('d',[])
exp1D = array('d',[])

print('start_mass: {}'.format(start_mass))
print('end_val: {}'.format(end_val))
print('step_sizes: {}'.format(step_sizes))
print('year: {}'.format(year))

# for i in range(1):
    # for j in range(int(end_val)):
for current_mass in range(int(start_mass), int(end_val), int(step_sizes)):
        m = current_mass

        f = TFile("./datacards_HIG_23_001/cards_"+str(year)+"/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_"+common_strings_pars.COMBINE_ASYMP_LIMIT.format(year = year, mH = current_mass)+".AsymptoticLimits.mH"+str(m)+".root","READ")
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

print 'mass',mass
print 'exp',exp

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

dummy = TH1D("dummy","dummy", 1, 550,3000)
dummy.SetBinContent(1,0.0)
dummy.GetXaxis().SetTitle('m(X)[GeV]')
dummy.GetYaxis().SetTitle('#sigma(pp#rightarrowX)#timesBR(X#rightarrowZZ) [pb]')
dummy.GetYaxis().SetTitleSize(0.05)
dummy.SetLineColor(0)
dummy.SetLineWidth(0)
dummy.SetFillColor(0)
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
latex2.DrawLatex(0.87, 0.95,"59.83 fb^{-1} (13 TeV)")
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

OutputFileName = 'highMassLimit_spin0_2D_13TeV_{year}'.format(year = year)

c.SaveAs(OutputFileName+".pdf")
c.SaveAs(OutputFileName+".png")
c.SaveAs(OutputFileName+".C")
c.SaveAs(OutputFileName+".root")
