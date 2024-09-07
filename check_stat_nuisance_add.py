from makeDCsandWSs import cd
import os
from utils import logger

# datacardPath = "/afs/cern.ch/user/r/rasharma/work/h2l2Q/EL7_Container/Limit_Extraction_FW/CMSSW_11_3_4/src/2l2Q_limitSettingTool/datacards_HIG_23_001/cards_2018_NoStat/HCG/1000"
datacardPath = "/afs/cern.ch/user/r/rasharma/work/h2l2Q/EL7_Container/Limit_Extraction_FW/CMSSW_11_3_4/src/2l2Q_limitSettingTool/datacards_HIG_23_001/cards_2018_WithStat/HCG/1000"

datacardName = "hzz2l2q_mumuqq_Merged_b_tagged_13TeV.txt"
# datacardName = "hzz2l2q_Merged_13TeV_xs.txt"
datacardName = datacardName.split(".")[0]

massValue = datacardPath.split("/")[-1]

with cd(datacardPath):
    logger.error("In directory: {}".format(os.getcwd()))

    # Convert the datacard into a workspace
    command1 = (
        "text2workspace.py {datacardName}.txt -m {massValue} -o {datacardName}.root ".format(
            datacardName=datacardName, massValue=massValue
        )
    )

    # Print the content of workspace into txt file
    #  hzz2l2q_mumuqq_Merged_b_tagged_13TeV.input.root
    command2 = (
        "combineTool.py -M PrintWorkspace -i {datacardName}.input.root ".format(
            datacardName=datacardName
        )
    )

    # Compute the limits
    command3 = "combine -M AsymptoticLimits -d {datacardName}.txt -m {massValue} -n .mH{massValue}_2018_03jun_blind_BkgOnlyHypothesis_ --run blind --setParameterRanges r=0,20  --cminFallbackAlgo Minuit,1:10 --cminDefaultMinimizerTolerance 0.001   --X-rtd FAST_VERTICAL_MORPH ".format(
        datacardName=datacardName, massValue=massValue
    )

    # Fast scan
    command4 = "combine -M MultiDimFit {datacardName}.root -m {massValue} --freezeParameters MH -n .{name}_fastScan_{pointsToScan} --cminDefaultMinimizerStrategy 0 --robustFit 1 --fastScan  --setParameterRanges r=0,2  --cminFallbackAlgo Minuit,1:10  --X-rtd FAST_VERTICAL_MORPH  -v 3".format(
        datacardName=datacardName,
        massValue=massValue,
        name=datacardName,
        pointsToScan=1000,
    )

    # Fast scan
    # command5 = "combineTool.py -M FastScan -w {datacardName}.root:w -m {massValue} --cminDefaultMinimizerStrategy 1 --setParameterRanges CMS_Vtagging=-10,5:CMS_scale_J_Abs=-2,2:CMS_scale_J_Abs_2018=-2,5:CMS_scale_J_BBEC1=-2,2:CMS_scale_J_BBEC1_2018=-2,2:CMS_scale_J_EC2=-2,2:CMS_scale_J_EC2_2018=-2,2:CMS_scale_J_FlavQCD=-2,2:CMS_scale_J_HF=-2,2:ttbar_btagged=-10,10:ttbar_untagged=-10,10:ttbar_vbftagged=-10,10   -v 5".format(
    command5 = "combineTool.py -M FastScan -w {datacardName}.root:w -m {massValue}    -v 99".format(
        datacardName=datacardName, massValue=massValue
    )

    command5 += " --cminDefaultMinimizerType Minuit --cminDefaultMinimizerTolerance 0.001 --cminDefaultMinimizerPrecision 0.00000001 --robustHesse 1 "

    command5 += "--parallel 8    --setParameterRanges r=0,20:ttbar_btagged=0,20:vz_btagged=0,20:zjet_btagged=0,20:CMS_scale_J_Abs_2018=0,2:CMS_zz2l2q_sigMELA_merged=0,2:CMS_zz2lJ_sigma_J_sig=0,2:CMS_zz2lJ_mean_J_sig=0,2:CMS_zz2l2q_sigma_j_sig=0,2:CMS_zz2l2q_mean_m_sig=0,2:CMS_zz2l2q_mean_e_sig=0,2:frac_VBF=0,1 --setRobustFitStrategy 0 --cminFallbackAlgo Minuit,1:10    --setRobustFitTolerance 0.001 --X-rtd FAST_VERTICAL_MORPH  "

    logger.error("COMMAND: {}".format(command5))
    os.system(command5)
