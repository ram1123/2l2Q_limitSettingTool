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
