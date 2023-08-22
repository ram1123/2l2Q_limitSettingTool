import os,sys

basedir="Cards/Modifiedcards/combination/"
dc="dc_2022-01-15-SoBord_sqV3m3lm4l_ll_noee_FR2_cs_combined"
step=sys.argv[1]
run=sys.argv[2]
useThis=" -t -1 --expectSignal 1 " if run=="exp" else ""

tryThis="--setParameterRanges r=-5,5 --cminFallbackAlgo Minuit,1:10 --setRobustFitStrategy 2"
if step=="1":
    os.system("text2workspace.py {bdir}{dc}.txt -m 125".format(dc=dc,bdir=basedir))
    os.system("cp {bdir}{dc}.root {bdir}{dc}_workspace.root".format(dc=dc,bdir=basedir))
    os.system("combineTool.py -M Impacts -d {bdir}{dc}.root -m 125 {useW}  --robustFit 1  --doInitialFit {here} ".format(dc=dc,bdir=basedir,useW=useThis,here=tryThis))
    os.system("combineTool.py -M Impacts --job-mode condor --sub-opts='+JobFlavour=\"workday\"' -d {bdir}{dc}.root  -m 125 {useW}  --robustFit 1 {here} --doFits --task-name jobs_{dc}_{run}".format(dc=dc,bdir=basedir,here=tryThis,useW=useThis,run=run))

else:
    os.system("combineTool.py -M Impacts -d {bd}{dc}.root -m 125 {useW} {here}  --robustFit 1 -o impacts_{HERE}.json".format(HERE=run,dc=dc,useW=useThis,bd=basedir,here=tryThis))
    os.system("plotImpacts.py -i impacts_{HERE}.json -o {dc}_{HERE}  --per-page 50 --blind".format(dc=dc,HERE=run)) #--blind
    os.system("cp {dc}_{HERE}.pdf /eos/user/a/anmehta/www/datacard_review/unblinding/{dc}_modified_{HERE}.pdf".format(dc=dc,HERE=run))




# --cminDefaultMinimizerTolerance 0.003
#--cminDefaultMinimizerStrategy 1 --X-rtd MINIMIZER_MaxCalls=9999999

#####checks for dc validation
#ValidateDatacards.py dc_2021-12-07-SoBord_sqV3m3lm4l_ll_noee_FR2_cs_combined.txt --printLevel 3 > /eos/user/a/anmehta/www/datacard_review/validate_card.txt
#combine -M FitDiagnostics Cards/combination/dc_2021-12-07-SoBord_sqV3m3lm4l_ll_noee_FR2_cs_combined.txt -t -1 --expectSignal 1



# combineTool.py -M GoodnessOfFit Cards/combination/dc_2022-01-22-SoBord_sqV3m3lm4l_ll_noee_FR2_cs_combined.txt --algo saturated -t 1000 -s 980034 --job-mode condor --sub-opts='+JobFlavour="tomorrow"' --task-name gof_htc

#text2workspace.py Cards/combination/dc_2022-01-24-SoBord_sqV3m3lm4l_ll_noee_FR2_cs_combined.txt -o dc_2022-01-24_FR2_workspace.root
#combine -M FitDiagnostics dc_2022-01-24_FR2_workspace.root  --saveShapes --saveWithUncertainties --saveNormalizations --saveOverallShapes  --job-mode condor #--skipBOnlyFit
#python /afs/cern.ch/work/a/anmehta/public/combineTool/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a fitDiagnosticsTest.root -g plots.root --abs --all --format text > /eos/user/a/anmehta/www/datacard_review/diffnuisance_asimov.txt



######### nLL scan with stat and syst separated
#combine -M MultiDimFit --algo grid --points 100 --rMin -7 --rMax 7 Cards/combination/dc_2022-02-10-SoBord_sqV3m3lm4l_ll_noee_FR2_cs_combined.root -m 125 -n nominal
#plot1DScan.py higgsCombinenominal.MultiDimFit.mH125.root
#combine -M MultiDimFit --algo none --rMin -1 --rMax 4 Cards/combination/dc_2022-02-10-SoBord_sqV3m3lm4l_ll_noee_FR2_cs_combined.root -m 125 -n bestfit --saveWorkspace
#combine -M MultiDimFit --algo grid --points 50 --rMin -1 --rMax 4 -m 125 -n stat higgsCombinebestfit.MultiDimFit.mH125.root --snapshotName MultiDimFit --freezeParameters allConstrainedNuisances
#plot1DScan.py higgsCombinenominal.MultiDimFit.mH125.root --others 'higgsCombinestat.MultiDimFit.mH125.root:Freeze all:2' --breakdown syst,stat

# Run with systematics
combine -M MultiDimFit --algo grid --points 150 --rMin -3 --rMax 3 -d hzz2l2q_13TeV_xs.root -m 600 -n .nominal.with_syst_points150  --saveWorkspace   -t -1 --expectSignal 1
combine -M MultiDimFit --algo none  --rMin -3 --rMax 3 -d hzz2l2q_13TeV_xs.root -m 600 -n .bestfit.with_syst_points150  --saveWorkspace   -t -1 --expectSignal 1
# combine -M MultiDimFit -d hzz2l2q_13TeV_xs.root -m 600 --freezeParameters MH -n .bestfit2.with_syst_points150 --setParameterRanges r=-3,3 --saveWorkspace   -t -1 --expectSignal 1    --algo none

# Run with --freezeParameters allConstrainedNuisances
combine -M MultiDimFit higgsCombine.nominal.with_syst_points150.MultiDimFit.mH600.root -m 600 --freezeParameters allConstrainedNuisances -n .scan.with_syst.statonly_correct_points150 --rMin -3 --rMax 3 --snapshotName MultiDimFit   -t -1 --expectSignal 1    --algo grid --points 250

# plot
plot1DScan.py higgsCombine.nominal.with_syst_points150.MultiDimFit.mH600.root --main-label "With systematics" --main-color 1 --others higgsCombine.scan.with_syst.statonly_correct_points150.MultiDimFit.mH600.root:"Stat-only":2 -o ../../figs/mH600_2018_29mar_blind__points150 --breakdown syst,stat

# NEW
combine -M MultiDimFit --algo grid --points 300 --rMin -7 --rMax 7 hzz2l2q_13TeV_xs.root -m 600 -n nominal
plot1DScan.py higgsCombinenominal.MultiDimFit.mH600.root # got error
combine -M MultiDimFit --algo none --rMin -4 --rMax 4 hzz2l2q_13TeV_xs.root -m 600 -n bestfit --saveWorkspace  --cminFallbackAlgo Minuit,1:10 --setRobustFitStrategy 2
combine -M MultiDimFit --algo grid --points 300 --rMin -1 --rMax 4 -m 600 -n stat higgsCombinebestfit.MultiDimFit.mH600.root --snapshotName MultiDimFit --freezeParameters allConstrainedNuisances
plot1DScan.py higgsCombinenominal.MultiDimFit.mH600.root --others 'higgsCombinestat.MultiDimFit.mH600.root:Freeze all:2' --breakdown syst,stat

#text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel   --PO verbose   --PO 'map=.*/DPSWWn:r_s0[1,0,10]' --PO 'map=.*/DPSWWp:r_s1[1,0,10]' dpsww_py.text   -o workspace_dpsww_py_two.root;
#combine -M MultiDimFit workspace_dpsww_py_two.root -n dpsww_py_two_obs --algo=singles --robustFit=1 --X-rtd FITTER_DYN_STEP  --redefineSignalPOIs r_s0,r_s1
# combine -M FitDiagnostics --redefineSignalPOIs r_etan,r_etap dc_2022-02-13-SoBord_sqV3m3lm4l_ll_noee_FR2_combined_py_asym.root

#https://twiki.cern.ch/twiki/bin/view/Sandbox/TestTopic11111180#Combined_card
#text2workspace.py  -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel   --PO verbose   --PO 'map=.*/DPSWWn.*:r_s0[1,0,10]' --PO 'map=.*/DPSWWp.*:r_s1[1,0,10]' AsymCards/combination/dc_2022-02-13-SoBord_sqV3m3lm4l_ll_noee_FR2_combined_newsim_asym.tx
#combine -M MultiDimFit AsymCards/combination/dc_2022-02-13-SoBord_sqV3m3lm4l_ll_noee_FR2_combined_newsim_asym.root --algo=singles --robustFit=1 --X-rtd FITTER_DYN_STEP  --redefineSignalPOIs r_s0,r_s1

#python test/makePlots.py --input /afs/cern.ch/user/c/cmartinp/Legacy/combine/CMSSW_10_2_13/src/CombineHarvester/fits/CA_7Apr_unblind_step3_v2/fitDiagnostics_ttHmultilep_WS_naming.root --odir /afs/cern.ch/user/c/cmartinp/Legacy/combine/CMSSW_10_2_13/src/CombineHarvester/fits/CA_7Apr_unblind_step3_v2/outputs/ --era 2016 --nameOut ttH_2lss_1tau_miss_2016 --channel 2lss_1tau --nameLabel " missing jet" --do_bottom --unblind --doPostFit --binToRead ttH_2lss_1tau_miss_2016 --original /afs/cern.ch/user/c/cmartinp/Legacy/combine/CMSSW_10_2_13/src/CombineHarvester/fits/CA_7Apr_unblind_step3_v2/ttH_2lss_1tau_miss_2016.root --binToReadOriginal ttH_2lss_1tau_miss
#python /afs/cern.ch/work/a/anmehta/public/combineTool/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit/test/mlfitNormsToText.py -u fitDiagnostics.root


##text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose --PO 'map=.*/DPSWWn:r_etan[1,0,6]' --PO 'map=.*/DPSWWp:r_etap[1,0,5]' dc_2022-02-13-SoBord_sqV3m3lm4l_ll_noee_FR2_combined_py_asym.txt
