from ROOT import *
from tdrStyle import *
setTDRStyle()
        
import os,sys
from array import array

mass = array('d',[])
zeros = array('d',[])
mass_merge = array('d',[])
zeros_merge = array('d',[])
exp_p2 = array('d',[])
exp_p1 = array('d',[])
exp = array('d',[])
obs = array('d',[])
exp_m1 = array('d',[])
exp_m2 = array('d',[])

exp_Resolved_untagged = array('d',[])
obs_Resolved_untagged = array('d',[])
exp_Resolved_btagged = array('d',[])
obs_Resolved_btagged = array('d',[])
exp_Resolved_vbftagged = array('d',[])
obs_Resolved_vbftagged = array('d',[])

exp_Merged_untagged = array('d',[])
obs_Merged_untagged = array('d',[])
exp_Merged_btagged = array('d',[])
obs_Merged_btagged = array('d',[])
exp_Merged_vbftagged = array('d',[])
obs_Merged_vbftagged = array('d',[])

for i in range(0,30):

    m = int(550+i*50)

    fobs = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_obs.Asymptotic.mH"+str(m)+".root","READ")
    tobs = fobs.Get("limit")

    f = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_exp.Asymptotic.mH"+str(m)+".root","READ")
    t = f.Get("limit")

    scale = 1.0

    mass.append(float(m))
    zeros.append(0.0)
    
    tobs.GetEntry(5)
    thisobs = tobs.limit*scale
    obs.append(thisobs)

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

    fobs = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_Resolved_untagged_obs.Asymptotic.mH"+str(m)+".root","READ")
    tobs = fobs.Get("limit")

    f = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_Resolved_untagged_exp.Asymptotic.mH"+str(m)+".root","READ")
    t = f.Get("limit")

    tobs.GetEntry(5)
    thisobs = tobs.limit*scale
    obs_Resolved_untagged.append(thisobs)

    t.GetEntry(2)
    thisexp = t.limit*scale
    exp_Resolved_untagged.append(thisexp)

    fobs = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_Resolved_b-tagged_obs.Asymptotic.mH"+str(m)+".root","READ")
    tobs = fobs.Get("limit")

    f = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_Resolved_b-tagged_exp.Asymptotic.mH"+str(m)+".root","READ")
    t = f.Get("limit")

    tobs.GetEntry(5)
    thisobs = tobs.limit*scale
    obs_Resolved_btagged.append(thisobs)

    t.GetEntry(2)
    thisexp = t.limit*scale
    exp_Resolved_btagged.append(thisexp)

    fobs = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_Resolved_vbf-tagged_obs.Asymptotic.mH"+str(m)+".root","READ")
    tobs = fobs.Get("limit")

    f = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_Resolved_vbf-tagged_exp.Asymptotic.mH"+str(m)+".root","READ")
    t = f.Get("limit")

    tobs.GetEntry(5)
    thisobs = tobs.limit*scale
    obs_Resolved_vbftagged.append(thisobs)

    t.GetEntry(2)
    thisexp = t.limit*scale
    exp_Resolved_vbftagged.append(thisexp)

    ##############

for i in range(0,26):

    m = int(750+i*50)

    mass_merge.append(float(m))
    zeros_merge.append(0.0)

    fobs = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_Merged_untagged_obs.Asymptotic.mH"+str(m)+".root","READ")
    tobs = fobs.Get("limit")

    f = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_Merged_untagged_exp.Asymptotic.mH"+str(m)+".root","READ")
    t = f.Get("limit")

    tobs.GetEntry(5)
    thisobs = tobs.limit*scale
    obs_Merged_untagged.append(thisobs)

    t.GetEntry(2)
    thisexp = t.limit*scale
    exp_Merged_untagged.append(thisexp)

    fobs = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_Merged_b-tagged_obs.Asymptotic.mH"+str(m)+".root","READ")
    tobs = fobs.Get("limit")

    f = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_Merged_b-tagged_exp.Asymptotic.mH"+str(m)+".root","READ")
    t = f.Get("limit")

    tobs.GetEntry(5)
    thisobs = tobs.limit*scale
    obs_Merged_btagged.append(thisobs)

    t.GetEntry(2)
    thisexp = t.limit*scale
    exp_Merged_btagged.append(thisexp)

    fobs = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_Merged_vbf-tagged_obs.Asymptotic.mH"+str(m)+".root","READ")
    tobs = fobs.Get("limit")

    f = TFile("../cards_sm13_2D_12p9fb_fracVBF_0.001_floatFracVBF/HCG/"+str(m)+"/higgsCombinemH"+str(m)+"_Merged_vbf-tagged_exp.Asymptotic.mH"+str(m)+".root","READ")
    t = f.Get("limit")

    tobs.GetEntry(5)
    thisobs = tobs.limit*scale
    obs_Merged_vbftagged.append(thisobs)

    t.GetEntry(2)
    thisexp = t.limit*scale
    exp_Merged_vbftagged.append(thisexp)

print 'mass',mass
print 'exp',exp
print 'obs',obs

v_mass = TVectorD(len(mass),mass)
v_zeros = TVectorD(len(zeros),zeros)
v_exp_p2 = TVectorD(len(exp_p2),exp_p2)
v_exp_p1 = TVectorD(len(exp_p1),exp_p1)
v_obs = TVectorD(len(obs),obs)
v_exp = TVectorD(len(exp),exp)
v_exp_m1 = TVectorD(len(exp_m1),exp_m1)
v_exp_m2 = TVectorD(len(exp_m2),exp_m2)

v_mass_merge = TVectorD(len(mass_merge),mass_merge)
v_zeros_merge = TVectorD(len(zeros_merge),zeros_merge)

v_obs_Resolved_untagged = TVectorD(len(obs_Resolved_untagged),obs_Resolved_untagged)
v_exp_Resolved_untagged = TVectorD(len(exp_Resolved_untagged),exp_Resolved_untagged)
v_obs_Resolved_btagged = TVectorD(len(obs_Resolved_btagged),obs_Resolved_btagged)
v_exp_Resolved_btagged = TVectorD(len(exp_Resolved_btagged),exp_Resolved_btagged)
v_obs_Resolved_vbftagged = TVectorD(len(obs_Resolved_vbftagged),obs_Resolved_vbftagged)
v_exp_Resolved_vbftagged = TVectorD(len(exp_Resolved_vbftagged),exp_Resolved_vbftagged)

v_obs_Merged_untagged = TVectorD(len(obs_Merged_untagged),obs_Merged_untagged)
v_exp_Merged_untagged = TVectorD(len(exp_Merged_untagged),exp_Merged_untagged)
v_obs_Merged_btagged = TVectorD(len(obs_Merged_btagged),obs_Merged_btagged)
v_exp_Merged_btagged = TVectorD(len(exp_Merged_btagged),exp_Merged_btagged)
v_obs_Merged_vbftagged = TVectorD(len(obs_Merged_vbftagged),obs_Merged_vbftagged)
v_exp_Merged_vbftagged = TVectorD(len(exp_Merged_vbftagged),exp_Merged_vbftagged)

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
dummy.SetMaximum(1000)
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
gr_exp.Draw("csame")

gr_obs = TGraphAsymmErrors(v_mass,v_obs,v_zeros,v_zeros,v_zeros,v_zeros)
gr_obs.SetLineColor(1)
gr_obs.SetLineWidth(2)
gr_obs.SetLineStyle(1)
gr_obs.Draw("Lsame")

gr_obs.SetMarkerColor(1)
gr_obs.SetMarkerStyle(20)
gr_obs.Draw("ep3same")

##########

gr_exp_Resolved_untagged = TGraphAsymmErrors(v_mass,v_exp_Resolved_untagged,v_zeros,v_zeros,v_zeros,v_zeros)
gr_exp_Resolved_untagged.SetLineColor(2)
gr_exp_Resolved_untagged.SetLineWidth(2)
gr_exp_Resolved_untagged.SetLineStyle(2)
gr_exp_Resolved_untagged.Draw("csame")

gr_obs_Resolved_untagged = TGraphAsymmErrors(v_mass,v_obs_Resolved_untagged,v_zeros,v_zeros,v_zeros,v_zeros)
gr_obs_Resolved_untagged.SetLineColor(2)
gr_obs_Resolved_untagged.SetLineWidth(2)
gr_obs_Resolved_untagged.SetLineStyle(1)
gr_obs_Resolved_untagged.Draw("Lsame")

gr_obs_Resolved_untagged.SetMarkerColor(2)
gr_obs_Resolved_untagged.SetMarkerStyle(20)
gr_obs_Resolved_untagged.Draw("ep3same")

##########

gr_exp_Resolved_btagged = TGraphAsymmErrors(v_mass,v_exp_Resolved_btagged,v_zeros,v_zeros,v_zeros,v_zeros)
gr_exp_Resolved_btagged.SetLineColor(3)
gr_exp_Resolved_btagged.SetLineWidth(2)
gr_exp_Resolved_btagged.SetLineStyle(2)
gr_exp_Resolved_btagged.Draw("csame")

gr_obs_Resolved_btagged = TGraphAsymmErrors(v_mass,v_obs_Resolved_btagged,v_zeros,v_zeros,v_zeros,v_zeros)
gr_obs_Resolved_btagged.SetLineColor(3)
gr_obs_Resolved_btagged.SetLineWidth(2)
gr_obs_Resolved_btagged.SetLineStyle(1)
gr_obs_Resolved_btagged.Draw("Lsame")

gr_obs_Resolved_btagged.SetMarkerColor(3)
gr_obs_Resolved_btagged.SetMarkerStyle(20)
gr_obs_Resolved_btagged.Draw("ep3same")

##########

gr_exp_Resolved_vbftagged = TGraphAsymmErrors(v_mass,v_exp_Resolved_vbftagged,v_zeros,v_zeros,v_zeros,v_zeros)
gr_exp_Resolved_vbftagged.SetLineColor(4)
gr_exp_Resolved_vbftagged.SetLineWidth(2)
gr_exp_Resolved_vbftagged.SetLineStyle(2)
gr_exp_Resolved_vbftagged.Draw("csame")

gr_obs_Resolved_vbftagged = TGraphAsymmErrors(v_mass,v_obs_Resolved_vbftagged,v_zeros,v_zeros,v_zeros,v_zeros)
gr_obs_Resolved_vbftagged.SetLineColor(4)
gr_obs_Resolved_vbftagged.SetLineWidth(2)
gr_obs_Resolved_vbftagged.SetLineStyle(1)
gr_obs_Resolved_vbftagged.Draw("Lsame")

gr_obs_Resolved_vbftagged.SetMarkerColor(4)
gr_obs_Resolved_vbftagged.SetMarkerStyle(20)
gr_obs_Resolved_vbftagged.Draw("ep3same")

############

gr_exp_Merged_untagged = TGraphAsymmErrors(v_mass_merge,v_exp_Merged_untagged,v_zeros_merge,v_zeros_merge,v_zeros_merge,v_zeros_merge)
gr_exp_Merged_untagged.SetLineColor(6)
gr_exp_Merged_untagged.SetLineWidth(2)
gr_exp_Merged_untagged.SetLineStyle(2)
gr_exp_Merged_untagged.Draw("csame")

gr_obs_Merged_untagged = TGraphAsymmErrors(v_mass_merge,v_obs_Merged_untagged,v_zeros_merge,v_zeros_merge,v_zeros_merge,v_zeros_merge)
gr_obs_Merged_untagged.SetLineColor(6)
gr_obs_Merged_untagged.SetLineWidth(2)
gr_obs_Merged_untagged.SetLineStyle(1)
gr_obs_Merged_untagged.Draw("Lsame")

gr_obs_Merged_untagged.SetMarkerColor(6)
gr_obs_Merged_untagged.SetMarkerStyle(20)
gr_obs_Merged_untagged.Draw("ep3same")

############

gr_exp_Merged_btagged = TGraphAsymmErrors(v_mass_merge,v_exp_Merged_btagged,v_zeros_merge,v_zeros_merge,v_zeros_merge,v_zeros_merge)
gr_exp_Merged_btagged.SetLineColor(7)
gr_exp_Merged_btagged.SetLineWidth(2)
gr_exp_Merged_btagged.SetLineStyle(2)
gr_exp_Merged_btagged.Draw("csame")

gr_obs_Merged_btagged = TGraphAsymmErrors(v_mass_merge,v_obs_Merged_btagged,v_zeros_merge,v_zeros_merge,v_zeros_merge,v_zeros_merge)
gr_obs_Merged_btagged.SetLineColor(7)
gr_obs_Merged_btagged.SetLineWidth(2)
gr_obs_Merged_btagged.SetLineStyle(1)
gr_obs_Merged_btagged.Draw("Lsame")

gr_obs_Merged_btagged.SetMarkerColor(7)
gr_obs_Merged_btagged.SetMarkerStyle(20)
gr_obs_Merged_btagged.Draw("ep3same")

############

gr_exp_Merged_vbftagged = TGraphAsymmErrors(v_mass_merge,v_exp_Merged_vbftagged,v_zeros_merge,v_zeros_merge,v_zeros_merge,v_zeros_merge)
gr_exp_Merged_vbftagged.SetLineColor(8)
gr_exp_Merged_vbftagged.SetLineWidth(2)
gr_exp_Merged_vbftagged.SetLineStyle(2)
gr_exp_Merged_vbftagged.Draw("csame")

gr_obs_Merged_vbftagged = TGraphAsymmErrors(v_mass_merge,v_obs_Merged_vbftagged,v_zeros_merge,v_zeros_merge,v_zeros_merge,v_zeros_merge)
gr_obs_Merged_vbftagged.SetLineColor(8)
gr_obs_Merged_vbftagged.SetLineWidth(2)
gr_obs_Merged_vbftagged.SetLineStyle(1)
gr_obs_Merged_vbftagged.Draw("Lsame")

gr_obs_Merged_vbftagged.SetMarkerColor(8)
gr_obs_Merged_vbftagged.SetMarkerStyle(20)
gr_obs_Merged_vbftagged.Draw("ep3same")

############################################

latex2 = TLatex()
latex2.SetNDC()
latex2.SetTextSize(0.5*c.GetTopMargin())
latex2.SetTextFont(42)
latex2.SetTextAlign(31) # align right
latex2.DrawLatex(0.87, 0.95,"12.9 fb^{-1} (13 TeV)")
#latex2.SetTextSize(0.9*c.GetTopMargin())
#latex2.SetTextFont(62)
#latex2.SetTextAlign(11) # align right
#latex2.DrawLatex(0.27, 0.85, "CMS")
#latex2.SetTextSize(0.7*c.GetTopMargin())
#latex2.SetTextFont(52)
#latex2.SetTextAlign(11)
#latex2.DrawLatex(0.25, 0.8, "Preliminary")

legend = TLegend(.20,.70,.55,.90)
legend.AddEntry(gr_obs_Resolved_vbftagged , "Observed Resolved vbftagged 95% CL ", "l")
legend.AddEntry(gr_exp_Resolved_vbftagged , "Expected Resolved vbftagged 95% CL ", "l")
legend.AddEntry(gr_obs_Resolved_btagged , "Observed Resolved btagged 95% CL ", "l")
legend.AddEntry(gr_exp_Resolved_btagged , "Expected Resolved btagged 95% CL ", "l")
legend.AddEntry(gr_obs_Resolved_untagged , "Observed Resolved untagged 95% CL ", "l")
legend.AddEntry(gr_exp_Resolved_untagged , "Expected Resolved untagged 95% CL ", "l")
legend.SetShadowColor(0)
legend.SetFillColor(0)
legend.SetLineColor(0)
legend.Draw("same")
#########

legend2 = TLegend(.55,.70,.90,.90)
legend2.AddEntry(gr_obs_Merged_vbftagged , "Observed Merged vbftagged 95% CL ", "l")
legend2.AddEntry(gr_exp_Merged_vbftagged , "Expected Merged vbftagged 95% CL ", "l")
legend2.AddEntry(gr_obs_Merged_btagged , "Observed Merged btagged 95% CL ", "l")
legend2.AddEntry(gr_exp_Merged_btagged , "Expected Merged btagged 95% CL ", "l")
legend2.AddEntry(gr_obs_Merged_untagged , "Observed Merged untagged 95% CL ", "l")
legend2.AddEntry(gr_exp_Merged_untagged , "Expected Merged untagged 95% CL ", "l")

legend2.AddEntry(gr_obs , "Observed 95% CL ", "l")
legend2.AddEntry(gr_exp , "Expected 95% CL ", "l")
legend2.AddEntry(gr_exp1 , "#pm 1#sigma", "f")
legend2.AddEntry(gr_exp2 , "#pm 2#sigma", "f")

legend2.SetShadowColor(0)
legend2.SetFillColor(0)
legend2.SetLineColor(0)            
legend2.Draw("same")
                                                            
gPad.RedrawAxis()

c.SaveAs("highmasslimit_spin0_2D_13TeV_cats.pdf")
c.SaveAs("highmasslimit_spin0_2D_13TeV_cats.png")
