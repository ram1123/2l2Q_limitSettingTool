Singularity> python makeDCsandWSs.py -y 2018 -f -1 -setParameterRanges r=-1,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5   -mi 1000 -mf 1050 --allDatacard -s rc --log-level debug
[INFO] - [makeDCsandWSs.py:#990] - Setting log level to 10
+-----------------------+
|      Year = 2018      |
+-----------------------+
[DEBUG] - [utils.py:#90] - Directory datacards_HIG_23_001/cards_2018/HCG already exists. Exiting...
[DEBUG] - [utils.py:#90] - Directory datacards_HIG_23_001/cards_2018/figs already exists. Exiting...
[DEBUG] - [makeDCsandWSs.py:#863] - Current working directory: /afs/cern.ch/work/r/rasharma/h2l2Q/EL7_Container/Limit_Extraction_FW/CMSSW_11_3_4/src/2l2Q_limitSettingTool
[DEBUG] - [makeDCsandWSs.py:#872] - Running in serial mode
+-----------------------------------------------------+
|      Running step rc for mass 1000, year: 2018      |
+-----------------------------------------------------+
[DEBUG] - [makeDCsandWSs.py:#797] - Running step rc for mass 1000 in directory datacards_HIG_23_001/cards_2018/HCG/1000
[DEBUG] - [makeDCsandWSs.py:#284] - Datacard: ['hzz2l2q_13TeV_xs_NoNuisance.txt', 'hzz2l2q_Merged_13TeV_xs.txt', 'hzz2l2q_Resolved_13TeV_xs.txt', 'hzz2l2q_eeqq_Merged_13TeV.txt', 'hzz2l2q_eeqq_Resolved_13TeV.txt', 'hzz2l2q_mumuqq_Merged_13TeV.txt', 'hzz2l2q_mumuqq_Resolved_13TeV.txt']
[DEBUG] - [utils.py:#71] - ===================================================
[INFO] - [utils.py:#72] - COMMAND TO RUN: combine   -M AsymptoticLimits -d hzz2l2q_13TeV_xs_NoNuisance.txt -m 1000   -n .mH1000_2018_12may_blind_BkgOnlyHypothesis__NoNuisance  --rMin 0 --rMax 2 --rAbsAcc 0 --rRelAcc 0.0005  --run blind   --setParameterRanges r=-1,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  | tee mH1000_2018_12may_blind_BkgOnlyHypothesis__NoNuisance.log
[DEBUG] - [utils.py:#75] - Inside module RunCommand(command, dry_run=False):
 <<< Combine >>>
 <<< v9.2.1 >>>
>>> Random number generator seed is 123456
Will use a-priori instead of a-posteriori expected background.
>>> Method used is AsymptoticLimits
PDF didn't factorize!
Set Range of Parameter r To : (-1,2)
Set Range of Parameter CMS_scale_J_Abs_2018 To : (-10,10)
Set Range of Parameter CMS_zz2l2q_sigMELA_merged To : (-10,10)
Set Range of Parameter BTAG_resolved To : (-10,10)
Set Range of Parameter BTAG_merged To : (-5,5)
Parameters:
  1) RooRealVar::                                                                          BR = 94.1338
  2) RooRealVar::                                                                 BTAG_merged = 0
  3) RooRealVar::                                                               BTAG_resolved = 0
  4) RooRealVar::                                                             CMS_scale_J_Abs = 0
  5) RooRealVar::                                                        CMS_scale_J_Abs_2018 = 0
  6) RooRealVar::                                                           CMS_scale_J_BBEC1 = 0
  7) RooRealVar::                                                      CMS_scale_J_BBEC1_2018 = 0
  8) RooRealVar::                                                             CMS_scale_J_EC2 = 0
  9) RooRealVar::                                                        CMS_scale_J_EC2_2018 = 0
 10) RooRealVar::                                                         CMS_scale_J_FlavQCD = 0
 11) RooRealVar::                                                              CMS_scale_J_HF = 0
 12) RooRealVar::                                                         CMS_scale_J_HF_2018 = 0
 13) RooRealVar::                                                          CMS_scale_J_RelBal = 0
 14) RooRealVar::                                                  CMS_scale_J_RelSample_2018 = 0
 15) RooRealVar::                                                             CMS_scale_j_Abs = 0
 16) RooRealVar::                                                        CMS_scale_j_Abs_2018 = 0
 17) RooRealVar::                                                           CMS_scale_j_BBEC1 = 0
 18) RooRealVar::                                                      CMS_scale_j_BBEC1_2018 = 0
 19) RooRealVar::                                                             CMS_scale_j_EC2 = 0
 20) RooRealVar::                                                        CMS_scale_j_EC2_2018 = 0
 21) RooRealVar::                                                         CMS_scale_j_FlavQCD = 0
 22) RooRealVar::                                                              CMS_scale_j_HF = 0
 23) RooRealVar::                                                         CMS_scale_j_HF_2018 = 0
 24) RooRealVar::                                                          CMS_scale_j_RelBal = 0
 25) RooRealVar::                                                  CMS_scale_j_RelSample_2018 = 0
 26) RooRealVar::                                                   CMS_zz2l2q_bkgMELA_merged = 0
 27) RooRealVar::                                                 CMS_zz2l2q_bkgMELA_resolved = 0
 28) RooRealVar::                                                       CMS_zz2l2q_mean_e_sig = 0
 29) RooRealVar::                                                       CMS_zz2l2q_mean_j_sig = 0
 30) RooRealVar::                                                       CMS_zz2l2q_mean_m_sig = 0
 31) RooRealVar::                                                   CMS_zz2l2q_sigMELA_merged = 0
 32) RooRealVar::                                                 CMS_zz2l2q_sigMELA_resolved = 0
 33) RooRealVar::                                                      CMS_zz2l2q_sigma_e_sig = 0
 34) RooRealVar::                                                      CMS_zz2l2q_sigma_j_sig = 0
 35) RooRealVar::                                                      CMS_zz2l2q_sigma_m_sig = 0
 36) RooRealVar::                                                        CMS_zz2lJ_mean_J_sig = 0
 37) RooRealVar::                                                       CMS_zz2lJ_sigma_J_sig = 0
 38) RooRealVar::                                                                LUMI_13_2018 = 59.83
 39) RooRealVar::                                                                          MH = 1000
 40) RooRealVar::                                                     a1_VBF_eeqq_Merged_2018 = 0.889967
 41) RooRealVar::                                                   a1_VBF_eeqq_Resolved_2018 = 1.32263
 42) RooRealVar::                                                   a1_VBF_mumuqq_Merged_2018 = 0.889967
 43) RooRealVar::                                                 a1_VBF_mumuqq_Resolved_2018 = 1.32263
 44) RooRealVar::                                                     a1_ggH_eeqq_Merged_2018 = 0.889967
 45) RooRealVar::                                                   a1_ggH_eeqq_Resolved_2018 = 1.32263
 46) RooRealVar::                                                   a1_ggH_mumuqq_Merged_2018 = 0.889967
 47) RooRealVar::                                                 a1_ggH_mumuqq_Resolved_2018 = 1.32263
 48) RooRealVar::                                                     a2_VBF_eeqq_Merged_2018 = 2.89216
 49) RooRealVar::                                                   a2_VBF_eeqq_Resolved_2018 = 2.26471
 50) RooRealVar::                                                   a2_VBF_mumuqq_Merged_2018 = 2.89216
 51) RooRealVar::                                                 a2_VBF_mumuqq_Resolved_2018 = 2.26471
 52) RooRealVar::                                                     a2_ggH_eeqq_Merged_2018 = 2.89216
 53) RooRealVar::                                                   a2_ggH_eeqq_Resolved_2018 = 2.26471
 54) RooRealVar::                                                   a2_ggH_mumuqq_Merged_2018 = 2.89216
 55) RooRealVar::                                                 a2_ggH_mumuqq_Resolved_2018 = 2.26471
 56) RooRealVar::                                                        bias_VBF_eeqq_Merged = 7.30255
 57) RooRealVar::                                                      bias_VBF_eeqq_Resolved = -3.30291
 58) RooRealVar::                                                      bias_VBF_mumuqq_Merged = 7.30255
 59) RooRealVar::                                                    bias_VBF_mumuqq_Resolved = -3.30291
 60) RooRealVar::                                                        bias_ggH_eeqq_Merged = 7.30255
 61) RooRealVar::                                                      bias_ggH_eeqq_Resolved = -3.30291
 62) RooRealVar::                                                      bias_ggH_mumuqq_Merged = 7.30255
 63) RooRealVar::                                                    bias_ggH_mumuqq_Resolved = -3.30291
 64) RooRealVar::                                                                    frac_VBF = 0.815306
 65) RooRealVar::                                                                  mean_J_err = 0.01
 66) RooRealVar::                                                                  mean_e_err = 0.003
 67) RooRealVar::                                                                  mean_j_err = 0.01
 68) RooRealVar::                                                                  mean_m_err = 0.001
 69) RooRealVar::                                                     n1_VBF_eeqq_Merged_2018 = 21.8271
 70) RooRealVar::                                                   n1_VBF_eeqq_Resolved_2018 = 2.47339
 71) RooRealVar::                                                   n1_VBF_mumuqq_Merged_2018 = 21.8271
 72) RooRealVar::                                                 n1_VBF_mumuqq_Resolved_2018 = 2.47339
 73) RooRealVar::                                                     n1_ggH_eeqq_Merged_2018 = 21.8271
 74) RooRealVar::                                                   n1_ggH_eeqq_Resolved_2018 = 2.47339
 75) RooRealVar::                                                   n1_ggH_mumuqq_Merged_2018 = 21.8271
 76) RooRealVar::                                                 n1_ggH_mumuqq_Resolved_2018 = 2.47339
 77) RooRealVar::                                                     n2_VBF_eeqq_Merged_2018 = 2.48714
 78) RooRealVar::                                                   n2_VBF_eeqq_Resolved_2018 = 2
 79) RooRealVar::                                                   n2_VBF_mumuqq_Merged_2018 = 2.48714
 80) RooRealVar::                                                 n2_VBF_mumuqq_Resolved_2018 = 2
 81) RooRealVar::                                                     n2_ggH_eeqq_Merged_2018 = 2.48714
 82) RooRealVar::                                                   n2_ggH_eeqq_Resolved_2018 = 2
 83) RooRealVar::                                                   n2_ggH_mumuqq_Merged_2018 = 2.48714
 84) RooRealVar::                                                 n2_ggH_mumuqq_Resolved_2018 = 2
 85) RooRealVar::             n_exp_binMerged_eeqq_Merged_eeqq_Merged_b_tagged_proc_bkg_ttbar = 12.7876
 86) RooRealVar::                n_exp_binMerged_eeqq_Merged_eeqq_Merged_b_tagged_proc_bkg_vz = 22.7554
 87) RooRealVar::             n_exp_binMerged_eeqq_Merged_eeqq_Merged_b_tagged_proc_bkg_zjets = 137.738
 88) RooRealVar::             n_exp_binMerged_eeqq_Merged_eeqq_Merged_untagged_proc_bkg_ttbar = 11.8249
 89) RooRealVar::                n_exp_binMerged_eeqq_Merged_eeqq_Merged_untagged_proc_bkg_vz = 197.179
 90) RooRealVar::             n_exp_binMerged_eeqq_Merged_eeqq_Merged_untagged_proc_bkg_zjets = 648.986
 91) RooRealVar::           n_exp_binMerged_eeqq_Merged_eeqq_Merged_vbf_tagged_proc_bkg_ttbar = 3.6489
 92) RooRealVar::              n_exp_binMerged_eeqq_Merged_eeqq_Merged_vbf_tagged_proc_bkg_vz = 12.7472
 93) RooRealVar::           n_exp_binMerged_eeqq_Merged_eeqq_Merged_vbf_tagged_proc_bkg_zjets = 71.8298
 94) RooRealVar::         n_exp_binMerged_mumuqq_Merged_mumuqq_Merged_b_tagged_proc_bkg_ttbar = 16.0362
 95) RooRealVar::            n_exp_binMerged_mumuqq_Merged_mumuqq_Merged_b_tagged_proc_bkg_vz = 29.175
 96) RooRealVar::         n_exp_binMerged_mumuqq_Merged_mumuqq_Merged_b_tagged_proc_bkg_zjets = 172.731
 97) RooRealVar::         n_exp_binMerged_mumuqq_Merged_mumuqq_Merged_untagged_proc_bkg_ttbar = 14.644
 98) RooRealVar::            n_exp_binMerged_mumuqq_Merged_mumuqq_Merged_untagged_proc_bkg_vz = 241.781
 99) RooRealVar::         n_exp_binMerged_mumuqq_Merged_mumuqq_Merged_untagged_proc_bkg_zjets = 902.646
100) RooRealVar::       n_exp_binMerged_mumuqq_Merged_mumuqq_Merged_vbf_tagged_proc_bkg_ttbar = 4.1588
101) RooRealVar::          n_exp_binMerged_mumuqq_Merged_mumuqq_Merged_vbf_tagged_proc_bkg_vz = 14.7386
102) RooRealVar::       n_exp_binMerged_mumuqq_Merged_mumuqq_Merged_vbf_tagged_proc_bkg_zjets = 92.7133
103) RooRealVar::       n_exp_binResolved_eeqq_Resolved_eeqq_Resolved_b_tagged_proc_bkg_ttbar = 619.177
104) RooRealVar::          n_exp_binResolved_eeqq_Resolved_eeqq_Resolved_b_tagged_proc_bkg_vz = 105.858
105) RooRealVar::       n_exp_binResolved_eeqq_Resolved_eeqq_Resolved_b_tagged_proc_bkg_zjets = 270.817
106) RooRealVar::       n_exp_binResolved_eeqq_Resolved_eeqq_Resolved_untagged_proc_bkg_ttbar = 855.35
107) RooRealVar::          n_exp_binResolved_eeqq_Resolved_eeqq_Resolved_untagged_proc_bkg_vz = 1222.66
108) RooRealVar::       n_exp_binResolved_eeqq_Resolved_eeqq_Resolved_untagged_proc_bkg_zjets = 21478.8
109) RooRealVar::     n_exp_binResolved_eeqq_Resolved_eeqq_Resolved_vbf_tagged_proc_bkg_ttbar = 102.015
110) RooRealVar::        n_exp_binResolved_eeqq_Resolved_eeqq_Resolved_vbf_tagged_proc_bkg_vz = 69.2043
111) RooRealVar::   n_exp_binResolved_mumuqq_Resolved_mumuqq_Resolved_b_tagged_proc_bkg_ttbar = 343.98
112) RooRealVar::      n_exp_binResolved_mumuqq_Resolved_mumuqq_Resolved_b_tagged_proc_bkg_vz = 57.9829
113) RooRealVar::   n_exp_binResolved_mumuqq_Resolved_mumuqq_Resolved_b_tagged_proc_bkg_zjets = 197.519
114) RooRealVar::   n_exp_binResolved_mumuqq_Resolved_mumuqq_Resolved_untagged_proc_bkg_ttbar = 1044.27
115) RooRealVar::      n_exp_binResolved_mumuqq_Resolved_mumuqq_Resolved_untagged_proc_bkg_vz = 1496.5
116) RooRealVar::   n_exp_binResolved_mumuqq_Resolved_mumuqq_Resolved_untagged_proc_bkg_zjets = 28680.5
117) RooRealVar:: n_exp_binResolved_mumuqq_Resolved_mumuqq_Resolved_vbf_tagged_proc_bkg_ttbar = 125.318
118) RooRealVar::    n_exp_binResolved_mumuqq_Resolved_mumuqq_Resolved_vbf_tagged_proc_bkg_vz = 84.0287
119) RooRealVar::                                                                           r = 0.02 +/- 0.2
120) RooRealVar::                                                                 sigma_J_err = 0.1
121) RooRealVar::                                                       sigma_VBF_eeqq_Merged = 31.1956
122) RooRealVar::                                                     sigma_VBF_eeqq_Resolved = 41.7743
123) RooRealVar::                                                     sigma_VBF_mumuqq_Merged = 31.1956
124) RooRealVar::                                                   sigma_VBF_mumuqq_Resolved = 41.7743
125) RooRealVar::                                                                 sigma_e_err = 0.2
126) RooRealVar::                                                       sigma_ggH_eeqq_Merged = 31.1956
127) RooRealVar::                                                     sigma_ggH_eeqq_Resolved = 41.7743
128) RooRealVar::                                                     sigma_ggH_mumuqq_Merged = 31.1956
129) RooRealVar::                                                   sigma_ggH_mumuqq_Resolved = 41.7743
130) RooRealVar::                                                                 sigma_j_err = 0.1
131) RooRealVar::                                                                 sigma_m_err = 0.2
Obs:
  1) RooRealVar:: zz2l2q_mass = 3495
  2) RooRealVar::      Dspin0 = 0.95
  3) RooRealVar::  zz2lJ_mass = 3495
  4) RooCategory:: CMS_channel = Resolved_mumuqq_Resolved_mumuqq_Resolved_vbf_tagged(idx = 2)


 -- AsymptoticLimits ( CLs ) --
Expected  2.5%: r < 0.0042
Expected 16.0%: r < 0.0057
Expected 50.0%: r < 0.0082
Expected 84.0%: r < 0.0119
Expected 97.5%: r < 0.0167

Done in 1.25 min (cpu), 1.26 min (real)
[DEBUG] - [utils.py:#71] - ===================================================
[INFO] - [utils.py:#72] - COMMAND TO RUN: combine   -M AsymptoticLimits -d hzz2l2q_Merged_13TeV_xs.txt -m 1000   -n .mH1000_2018_12may_blind_BkgOnlyHypothesis_Merged  --rMin 0 --rMax 2 --rAbsAcc 0 --rRelAcc 0.0005  --run blind   --setParameterRanges r=-1,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  | tee mH1000_2018_12may_blind_BkgOnlyHypothesis_Merged.log
[DEBUG] - [utils.py:#75] - Inside module RunCommand(command, dry_run=False):
 <<< Combine >>>
 <<< v9.2.1 >>>
>>> Random number generator seed is 123456
Will use a-priori instead of a-posteriori expected background.
>>> Method used is AsymptoticLimits
Set Range of Parameter r To : (-1,2)
Set Range of Parameter CMS_scale_J_Abs_2018 To : (-10,10)
Set Range of Parameter CMS_zz2l2q_sigMELA_merged To : (-10,10)
Warning: Did not find a parameter with name BTAG_resolved

 -- AsymptoticLimits ( CLs ) --
Expected  2.5%: r < 0.0033
Expected 16.0%: r < 0.0046
Expected 50.0%: r < 0.0066
Expected 84.0%: r < 0.0097
Expected 97.5%: r < 0.0138

Done in 1.65 min (cpu), 1.66 min (real)
[DEBUG] - [utils.py:#71] - ===================================================
[INFO] - [utils.py:#72] - COMMAND TO RUN: combine   -M AsymptoticLimits -d hzz2l2q_Resolved_13TeV_xs.txt -m 1000   -n .mH1000_2018_12may_blind_BkgOnlyHypothesis_Resolved  --rMin 0 --rMax 2 --rAbsAcc 0 --rRelAcc 0.0005  --run blind   --setParameterRanges r=-1,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  | tee mH1000_2018_12may_blind_BkgOnlyHypothesis_Resolved.log
[DEBUG] - [utils.py:#75] - Inside module RunCommand(command, dry_run=False):
 <<< Combine >>>
 <<< v9.2.1 >>>
>>> Random number generator seed is 123456
Will use a-priori instead of a-posteriori expected background.
>>> Method used is AsymptoticLimits
Set Range of Parameter r To : (-1,2)
Warning: Did not find a parameter with name CMS_scale_J_Abs_2018
Warning: Did not find a parameter with name CMS_zz2l2q_sigMELA_merged
Set Range of Parameter BTAG_resolved To : (-10,10)
Warning: Did not find a parameter with name BTAG_merged

 -- AsymptoticLimits ( CLs ) --
Expected  2.5%: r < 0.0535
Expected 16.0%: r < 0.0736
Expected 50.0%: r < 0.1070
Expected 84.0%: r < 0.1576
Expected 97.5%: r < 0.2225

Done in 1.08 min (cpu), 1.09 min (real)
[DEBUG] - [utils.py:#71] - ===================================================
[INFO] - [utils.py:#72] - COMMAND TO RUN: combine   -M AsymptoticLimits -d hzz2l2q_eeqq_Merged_13TeV.txt -m 1000   -n .mH1000_2018_12may_blind_BkgOnlyHypothesis_eeqq_Merged  --rMin 0 --rMax 2 --rAbsAcc 0 --rRelAcc 0.0005  --run blind   --setParameterRanges r=-1,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  | tee mH1000_2018_12may_blind_BkgOnlyHypothesis_eeqq_Merged.log
[DEBUG] - [utils.py:#75] - Inside module RunCommand(command, dry_run=False):
 <<< Combine >>>
 <<< v9.2.1 >>>
>>> Random number generator seed is 123456
Will use a-priori instead of a-posteriori expected background.
>>> Method used is AsymptoticLimits
Set Range of Parameter r To : (-1,2)
Set Range of Parameter CMS_scale_J_Abs_2018 To : (-10,10)
Set Range of Parameter CMS_zz2l2q_sigMELA_merged To : (-10,10)
Warning: Did not find a parameter with name BTAG_resolved

 -- AsymptoticLimits ( CLs ) --
Expected  2.5%: r < 0.0051
Expected 16.0%: r < 0.0071
Expected 50.0%: r < 0.0104
Expected 84.0%: r < 0.0156
Expected 97.5%: r < 0.0227

Done in 0.79 min (cpu), 0.79 min (real)
[DEBUG] - [utils.py:#71] - ===================================================
[INFO] - [utils.py:#72] - COMMAND TO RUN: combine   -M AsymptoticLimits -d hzz2l2q_eeqq_Resolved_13TeV.txt -m 1000   -n .mH1000_2018_12may_blind_BkgOnlyHypothesis_eeqq_Resolved  --rMin 0 --rMax 2 --rAbsAcc 0 --rRelAcc 0.0005  --run blind   --setParameterRanges r=-1,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  | tee mH1000_2018_12may_blind_BkgOnlyHypothesis_eeqq_Resolved.log
[DEBUG] - [utils.py:#75] - Inside module RunCommand(command, dry_run=False):
 <<< Combine >>>
 <<< v9.2.1 >>>
>>> Random number generator seed is 123456
Will use a-priori instead of a-posteriori expected background.
>>> Method used is AsymptoticLimits
Set Range of Parameter r To : (-1,2)
Warning: Did not find a parameter with name CMS_scale_J_Abs_2018
Warning: Did not find a parameter with name CMS_zz2l2q_sigMELA_merged
Set Range of Parameter BTAG_resolved To : (-10,10)
Warning: Did not find a parameter with name BTAG_merged

 -- AsymptoticLimits ( CLs ) --
Expected  2.5%: r < 0.0698
Expected 16.0%: r < 0.0971
Expected 50.0%: r < 0.1441
Expected 84.0%: r < 0.2165
Expected 97.5%: r < 0.3125

Done in 0.67 min (cpu), 0.68 min (real)
[DEBUG] - [utils.py:#71] - ===================================================
[INFO] - [utils.py:#72] - COMMAND TO RUN: combine   -M AsymptoticLimits -d hzz2l2q_mumuqq_Merged_13TeV.txt -m 1000   -n .mH1000_2018_12may_blind_BkgOnlyHypothesis_mumuqq_Merged  --rMin 0 --rMax 2 --rAbsAcc 0 --rRelAcc 0.0005  --run blind   --setParameterRanges r=-1,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  | tee mH1000_2018_12may_blind_BkgOnlyHypothesis_mumuqq_Merged.log
[DEBUG] - [utils.py:#75] - Inside module RunCommand(command, dry_run=False):
 <<< Combine >>>
 <<< v9.2.1 >>>
>>> Random number generator seed is 123456
Will use a-priori instead of a-posteriori expected background.
>>> Method used is AsymptoticLimits
Set Range of Parameter r To : (-1,2)
Set Range of Parameter CMS_scale_J_Abs_2018 To : (-10,10)
Set Range of Parameter CMS_zz2l2q_sigMELA_merged To : (-10,10)
Warning: Did not find a parameter with name BTAG_resolved

 -- AsymptoticLimits ( CLs ) --
Expected  2.5%: r < 0.0047
Expected 16.0%: r < 0.0065
Expected 50.0%: r < 0.0094
Expected 84.0%: r < 0.0141
Expected 97.5%: r < 0.0202

Done in 0.76 min (cpu), 0.77 min (real)
[DEBUG] - [utils.py:#71] - ===================================================
[INFO] - [utils.py:#72] - COMMAND TO RUN: combine   -M AsymptoticLimits -d hzz2l2q_mumuqq_Resolved_13TeV.txt -m 1000   -n .mH1000_2018_12may_blind_BkgOnlyHypothesis_mumuqq_Resolved  --rMin 0 --rMax 2 --rAbsAcc 0 --rRelAcc 0.0005  --run blind   --setParameterRanges r=-1,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  | tee mH1000_2018_12may_blind_BkgOnlyHypothesis_mumuqq_Resolved.log
[DEBUG] - [utils.py:#75] - Inside module RunCommand(command, dry_run=False):
 <<< Combine >>>
 <<< v9.2.1 >>>
>>> Random number generator seed is 123456
Will use a-priori instead of a-posteriori expected background.
>>> Method used is AsymptoticLimits
Set Range of Parameter r To : (-1,2)
Warning: Did not find a parameter with name CMS_scale_J_Abs_2018
Warning: Did not find a parameter with name CMS_zz2l2q_sigMELA_merged
Set Range of Parameter BTAG_resolved To : (-10,10)
Warning: Did not find a parameter with name BTAG_merged

 -- AsymptoticLimits ( CLs ) --
Expected  2.5%: r < 0.0917
Expected 16.0%: r < 0.1256
Expected 50.0%: r < 0.1820
Expected 84.0%: r < 0.2669
Expected 97.5%: r < 0.3761

Done in 0.57 min (cpu), 0.58 min (real)
