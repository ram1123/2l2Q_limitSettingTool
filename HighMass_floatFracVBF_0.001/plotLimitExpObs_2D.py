from ROOT import *
from tdrStyle import *
setTDRStyle()
        
import os,sys
from array import array

mass = array('d',[])
zeros = array('d',[])
exp_p2 = array('d',[])
exp_p1 = array('d',[])
exp = array('d',[])
obs = array('d',[])
exp_m1 = array('d',[])
exp_m2 = array('d',[])

exp1D = array('d',[])

mH=[550,600, 650,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000]

    
for i in range(0,30):

    m = int(550+i*50)

    #if (not os.path.isfile("higgsCombinetest.Asymptotic.mH"+str(int(m))+".root")): continue

    #higgsCombinemH600_obs.Asymptotic.mH600.root

    fobs = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_obs.Asymptotic.mH"+str(m)+".root","READ")
    tobs = fobs.Get("limit")

    f = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_exp.Asymptotic.mH"+str(m)+".root","READ")
    t = f.Get("limit")

    f1D = TFile("../cards_sm13_1D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_exp.Asymptotic.mH"+str(m)+".root","READ")
    t1D = f1D.Get("limit")

    scale = 1.0

    mass.append(float(m))
    zeros.append(0.0)
    
    tobs.GetEntry(5)
    thisobs = tobs.limit*scale
    obs.append(thisobs)

    t.GetEntry(2)
    thisexp = t.limit*scale
    exp.append(thisexp)
    
    t1D.GetEntry(2)
    thisexp1D = t1D.limit*scale
    exp1D.append((thisexp1D-thisexp)/thisexp1D)

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
print 'exp1D',exp1D
print 'obs',obs

v_mass = TVectorD(len(mass),mass)
v_zeros = TVectorD(len(zeros),zeros)
v_exp_p2 = TVectorD(len(exp_p2),exp_p2)
v_exp_p1 = TVectorD(len(exp_p1),exp_p1)
v_obs = TVectorD(len(obs),obs)
v_exp = TVectorD(len(exp),exp)
v_exp_m1 = TVectorD(len(exp_m1),exp_m1)
v_exp_m2 = TVectorD(len(exp_m2),exp_m2)

c = TCanvas("c","c",800, 800)
c.SetLogy()
#c.SetLogx()
c.SetGridx()
c.SetGridy()

c.SetRightMargin(0.06)
c.SetLeftMargin(0.2)

dummy = TH1D("dummy","dummy", 1, 550,2000)
dummy.SetBinContent(1,0.0)
dummy.GetXaxis().SetTitle('m(X)[GeV]')   
dummy.GetYaxis().SetTitle('#sigma(pp#rightarrowX)#timesBR(X#rightarrowZZ) [pb]')   
dummy.SetLineColor(0)
dummy.SetLineWidth(0)
dummy.SetFillColor(0)
dummy.SetMinimum(0.001)
dummy.SetMaximum(1)
dummy.GetXaxis().SetMoreLogLabels(kTRUE)
dummy.GetXaxis().SetNoExponent(kTRUE)
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

gr_obs = TGraphAsymmErrors(v_mass,v_obs,v_zeros,v_zeros,v_zeros,v_zeros)
gr_obs.SetLineColor(1)
gr_obs.SetLineWidth(2)
gr_obs.SetLineStyle(1)
gr_obs.Draw("Lsame")

gr_obs.SetMarkerColor(1)
gr_obs.SetMarkerStyle(20)

gr_obs.Draw("ep3same")

latex2 = TLatex()
latex2.SetNDC()
latex2.SetTextSize(0.5*c.GetTopMargin())
latex2.SetTextFont(42)
latex2.SetTextAlign(31) # align right
latex2.DrawLatex(0.87, 0.95,"12.9 fb^{-1} (13 TeV)")
latex2.SetTextSize(0.9*c.GetTopMargin())
latex2.SetTextFont(62)
latex2.SetTextAlign(11) # align right
latex2.DrawLatex(0.27, 0.85, "CMS")
latex2.SetTextSize(0.7*c.GetTopMargin())
latex2.SetTextFont(52)
latex2.SetTextAlign(11)
latex2.DrawLatex(0.25, 0.8, "Preliminary")

legend = TLegend(.60,.70,.90,.90)
legend.AddEntry(gr_obs , "Observed 95% CL ", "l")
legend.AddEntry(gr_exp , "Expected 95% CL ", "l")
legend.AddEntry(gr_exp1 , "#pm 1#sigma", "f")
legend.AddEntry(gr_exp2 , "#pm 2#sigma", "f")
legend.SetShadowColor(0)
legend.SetFillColor(0)
legend.SetLineColor(0)            
legend.Draw("same")
                                                            
gPad.RedrawAxis()

c.SaveAs("highmasslimit_spin0_2D_13TeV.pdf")
c.SaveAs("highmasslimit_spin0_2D_13TeV.png")
c.SaveAs("highmasslimit_spin0_2D_13TeV.C")
c.SaveAs("highmasslimit_spin0_2D_13TeV.root")
