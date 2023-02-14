# Prepare condor jobs
condor = '''executable              = run_script_{year}.sh
output                  = output/{year}/strips.$(ClusterId).$(ProcId).out
error                   = output/{year}/strips.$(ClusterId).$(ProcId).out
log                     = output/{year}/strips.$(ClusterId).$(ProcId).out
transfer_input_files    = run_script_{year}.sh
on_exit_remove          = (ExitBySignal == False) && (ExitCode == 0)
periodic_release        = (NumJobStarts < 3) && ((CurrentTime - EnteredCurrentStatus) > (60*60))

+JobFlavour             = "espresso"
+AccountingGroup        = "group_u_CMS.CAF.ALCA"
queue arguments from arguments_{year}.txt
'''


script = '''#!/bin/sh -e
echo "Starting job on " `date`
echo "Running on: `uname -a`"
echo "System software: `cat /etc/redhat-release`"
JOBID=$1;
LOCAL=$2;
MH=$3;
DATACARD=$4
echo "Print arguments: "
echo "JOBID: ${JOBID}"
echo "LOCAL: ${LOCAL}"
echo "MH: ${MH}"
echo "DATACARD: ${DATACARD}"
echo "========="

echo "Print local path: `pwd`"
cd ${LOCAL}
echo "Print local path: `pwd`"
echo "Print local path: `pwd`"

eval `scramv1 ru -sh`
echo "========="
echo "combine -n mH${MH}_exp -m ${MH} -M AsymptoticLimits  ${DATACARD}  --rMax 1 --rAbsAcc 0 --run blind"
echo "========="
combine -n mH${MH}_exp -m ${MH} -M AsymptoticLimits  ${DATACARD}  --rMax 1 --rAbsAcc 0 --run blind
echo "========="

echo -e "DONE";
echo "Ending job on " `date`
'''
