# Aim of this tool

1. Alpha  ratio method information: **Independent code**:
    - https://github.com/jialin-guo1/HZZAnalysis/blob/994e9a59b67da505dbe7d15605558ab414eb1310/BackgroundEstimation/AlphaMethod.py
1.  Resolution: Macro: **Independent code**
    -
1. Signal efficiency: **Independent code**
1. templates 1D and 2D: **Independent code**


# Input information required

1. Directory `HM_inputs_2018UL` that contains basic systematic information
2. Resolution info in directory: `Resolution`
3. Templates: `templates1D` and  `templates2D`
4. Directory: `CMSdata`
5. Signal Efficiency: `SigEff`

# Setup

1. Setup combine (Reference: [https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/)

    ```bash
    export SCRAM_ARCH=slc7_amd64_gcc700
    cmsrel CMSSW_10_2_13
    cd CMSSW_10_2_13/src
    cmsenv
    git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
    cd HiggsAnalysis/CombinedLimit
    cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
    git fetch origin
    git checkout v8.2.0
    scramv1 b clean; scramv1 b # always make a clean build
    cd $CMSSW_BASE/src
    bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-ssh.sh)
    scramv1 b -j 8
    ```

2. Get the custom tool for datacard creation and limit computation

  ```bash
  cd $CMSSW_BASE/src
  git clone git@github.com:jialin-guo1/2l2q_limitsettingtool.git -b develop
  ```

3. To make datacards

    ```bash
    cd 2l2q_limitsettingtool
    python makeDCsandWSs.py -i HM_inputs_2018UL -y 2018 -a 2018
    ```

    - In `HM_inputs_*` you should prepare 12 systematics files  ((resolved, merged * b-tagged, un-tagged , vbf-tagged) * ee,mumu). Now, you can just go into these .txt files and change the value of systematics.
    - `-y` is year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all
    - `-a` append name for cards dir. i.e `-a` test will create `cards_test` to stroe all datacards. When you run this tool, it better to keep option `-a` same as `-y`. in `cards_2016`, `cards_2017` and `cards_2018`. There already have combine and plot script.

    Help command of makeDCsandWSs.py:

    ```bash
    Usage: makeDCsandWSs.py [options] datasetList
    makeDCsandWSs.py -h for help

    Options:
    -h, --help            show this help message and exit
    -i INPUT_DIR, --input=INPUT_DIR
                            inputs directory
    -d IS_2D, --is2D=IS_2D
                            is2D (default:1)
    -a APPEND_NAME, --append=APPEND_NAME
                            append name for cards dir
    -f FRAC_VBF, --fracVBF=FRAC_VBF
                            fracVBF (default:0.5%)
    -y YEAR, --year=YEAR  year to run or run for all three year. Options: 2016,
                            2016APV, 2017,2018,all
    -s STEP, --step=STEP  Which step to run: dc (DataCardCreation), cc
                            (CombineCards), rc (RunCombine), or all
    ```

# General commands:

```bash
# local
combine -n testt -m 500 -M AsymptoticLimits hzz2l2q_13TeV_xs_NoNuisance.txt --rMax 1 --rAbsAcc 0 --run blind

# batch
combineTool.py -M AsymptoticLimits -d hzz2l2q_13TeV_xs_NoNuisance.root --rMax 1 --rAbsAcc 0 --run blind -m 500 --job-mode condor
```
