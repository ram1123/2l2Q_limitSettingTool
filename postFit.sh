pwdd=/afs/cern.ch/user/r/rasharma/work/LearnCombine/CMSSW_11_3_4/src/2l2Q_limitSettingTool

ERA=2018
CHANNEL="All"
VARIABLE="mZZ"
WORKSPACE="hzz2l2q_13TeV_xs.txt"
ID=${ERA}_${CHANNEL}_${VARIABLE}
LOGFILE="logFile.log"
cd datacards_HIG_23_001/cards_2018/HCG/500/
# ls

combine \
        -M FitDiagnostics \
        -m 500 -d $WORKSPACE \
        --robustFit 1 -v1 \
        --robustHesse 1 \
        -n .$ID \
        --setParameters r=0 --freezeParameters r \
        # --X-rtd MINIMIZER_analytic \
        --cminDefaultMinimizerStrategy 0  --plots --saveShapes |
        tee logFile.log

# FITFILE=fitDiagnostics.${ID}.MultiDimFit.mH125.root
# mv fitDiagnostics.${ID}.root $FITFILE
# pwd
# python check_mlfit.py $FITFILE
# root -l $FITFILE <<< "fit_b->Print(); fit_s->Print()"


# python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
        # fitDiagnostics.${ID}.MultiDimFit.mH125.root -a \
        # -f html > nuisances.html

# """
#         FITFILE=${datacard_output}/fitDiagnostics.${ID}.MultiDimFit.mH125.root
#         mv fitDiagnostics.${ID}.root $FITFILE
#         #python combine/check_mlfit.py fitDiagnostics${ERA}.root
#         # root -l $FITFILE <<< "fit_b->Print(); fit_s->Print()"

#         python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
#             ${datacard_output}/fitDiagnostics.${ID}.MultiDimFit.mH125.root -a \
#             -f html >${datacard_output}/nuisances.html
#         PostFitShapesFromWorkspace -m 125 -w $WORKSPACE \
#             -o ${datacard_output}/${ID}-datacard-shapes-prefit.root \
#             -d ${datacard_output}/cmb/125/htt_${CHANNEL}_300_${ERA}.txt

#         PostFitShapesFromWorkspace -m 125 -w $WORKSPACE \
#             -o ${datacard_output}/${ID}-datacard-shapes-postfit-b.root \
#             -f ${datacard_output}/fitDiagnostics.${ID}.MultiDimFit.mH125.root:fit_b --postfit --sampling \
#             -d ${datacard_output}/cmb/125/htt_${CHANNEL}_300_${ERA}.txt
# """

cd  ${pwdd}
