from makeDCsandWSs import cd
import os
from utils import logger

datacardPath = "/afs/cern.ch/user/r/rasharma/work/h2l2Q/EL7_Container/Limit_Extraction_FW/CMSSW_11_3_4/src/2l2Q_limitSettingTool/datacards_HIG_23_001/cards_2018_new_smooth/HCG/1000"

datacardName = "hzz2l2q_mumuqq_Merged_b_tagged_13TeV.txt"
datacardName = datacardName.split(".")[0]

massValue = datacardPath.split("/")[-1]

with cd(datacardPath):
    logger.error("In directory: {}".format(os.getcwd()))
    command = (
        "text2workspace.py {datacardName}.txt -m {massValue} -o {datacardName}.root ".format(
            datacardName=datacardName, massValue=massValue
        )
    )
    logger.error("COMMAND: {}".format(command))
    os.system(command)

    # Print the content of workspace into txt file
    #  hzz2l2q_mumuqq_Merged_b_tagged_13TeV.input.root
    command = (
        "combineTool.py -M PrintWorkspace -i {datacardName}.input.root ".format(
            datacardName=datacardName
        )
    )
    # logger.error("COMMAND: {}".format(command))
    # os.system(command)


# run combine
# [INFO] - [utils.py:#72] - COMMAND TO RUN: combine   -M AsymptoticLimits -d hzz2l2q_13TeV_xs.txt -m 1000   -n .mH1000_2018_03jun_blind_BkgOnlyHypothesis_  --run blind    | tee mH1000_2018_03jun_blind_BkgOnlyHypothesis_.log
# command = "combine -M MultiDimFit {datacard} -m {mH} --freezeParameters MH -n .{name}_fastScan_{pointsToScan} --cminDefaultMinimizerStrategy 0 --robustFit 1 --fastScan  ".format(
#
with cd(datacardPath):
    command = "combine -M AsymptoticLimits -d {datacardName}.root -m {massValue} -n .mH{massValue}_2018_03jun_blind_BkgOnlyHypothesis_ --run blind --setParameterRanges r=-20000,20000  --cminFallbackAlgo Minuit,1:10 --cminDefaultMinimizerTolerance 0.001   --X-rtd FAST_VERTICAL_MORPH ".format(
        datacardName=datacardName, massValue=massValue
    )
    logger.error("COMMAND: {}".format(command))
    os.system(command)
    # command = "combine -M MultiDimFit {datacardName}.root -m {massValue} --freezeParameters MH -n .{name}_fastScan_{pointsToScan} --cminDefaultMinimizerStrategy 0 --robustFit 1 --fastScan  --setParameterRanges r=0,2  --cminFallbackAlgo Minuit,1:10  --X-rtd FAST_VERTICAL_MORPH  -v 3".format(
    #     datacardName=datacardName,
    #     massValue=massValue,
    #     name=datacardName,
    #     pointsToScan=1000,
    # )
    command = "combineTool.py -M FastScan -w {datacardName}.root:w -m {massValue} --cminDefaultMinimizerStrategy 0 --setParameterRanges CMS_Vtagging=-10,10:CMS_scale_J_Abs=-10,10:CMS_scale_J_Abs_2018=-10,10:CMS_scale_J_BBEC1=-10,10:ttbar_btagged=-10,10:ttbar_untagged=-10,10:ttbar_vbftagged=-10,10  ".format(
        datacardName=datacardName, massValue=massValue
    )
    logger.error("COMMAND: {}".format(command))
    os.system(command)
