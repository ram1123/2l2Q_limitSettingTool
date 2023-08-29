# ToDO list

## Get pre- and post-fit plots

```bash
combine -M FitDiagnostics -m 500 -d hzz2l2q_13TeV_xs.txt --robustFit 1 -v1 --robustHesse 1 -n testt --setParameters r=0 --freezeParameters r --plots --saveShapes
```

```bash
cd /afs/cern.ch/work/r/rasharma/LearnCombine/CMSSW_11_3_4/src/2l2Q_limitSettingTool/datacards_HIG_23_001/cards_2018/HCG/800
# combine -M FitDiagnostics myworkspace.root --plots --saveShapes
combine -M FitDiagnostics -m 800 -d hzz2l2q_13TeV_xs.txt  --plots --saveShapes
```

# My notes

Step - 1: Create datacard

python makeDCsandWSs.py -y 2018 --log-level ERROR -f 1  step -s dc

This step does not support condor or parallel processing.

Step - 2: Combine cards for different channels

For this step use the parallel processing so that for all 51 mass point we can get combine cards easily.
python makeDCsandWSs.py -y 2018 --log-level ERROR -f 1  -p step -s cc

Step - 3: Run combine command

For this we should use the condor job facility. As this step takes too much time. Furthermore to submit jobs parallely we should use the parallel processing.

python makeDCsandWSs.py -y 2018 --log-level ERROR -f 1  -c -p step -s rc

