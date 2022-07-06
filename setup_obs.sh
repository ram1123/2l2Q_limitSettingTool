

type=$1

cd ../CMSSW_7_4_7/src/
eval `scram r -sh`

cd -

#sh buildPackage.sh

rm -rf cards_sm13_${1}D_12p9fb_fracVBF_${2}_floatFracVBF

echo "reco ${1}D"
python makeDCsandWSs.py -i SM_inputs_13TeV -a sm13_${1}D_12p9fb_fracVBF_${2}_floatFracVBF -d $(($1-1)) -f $2

