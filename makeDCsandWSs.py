import os
import sys
import optparse
from inputReader import *
from datacardClass import *

def RunCommand(command):
    # print("#"*51)
    print(command)
    os.system(command)

def RemoveFile(FileName):
    if os.path.exists(FileName):
        os.remove(FileName)
    else:
        print("File, {}, does not exist".format(FileName))

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

class DirectoryCreator:

    def __init__(self):
        self.input_dir = ""
        self.is_2d = 1
        self.append_name = ""
        self.frac_vbf = 0.005
        self.year = "2016"
        self.start_mass = 500
        self.step_sizes = 50
        self.end_val = 550 # scan mass end value is 3000, but I added 3001 to include 3000 in for loop. If I write 3000 then it will take last mass value as 2950.
        self.subdir = ['HCG','figs']
        self.dir_name = 'datacards_HIG_23_001/cards_'+self.append_name
        # self.channels = {'eeqq_Resolved'}
        self.channels = {'eeqq_Resolved', 'mumuqq_Resolved'}
        # self.channels = {'eeqq_Resolved', 'mumuqq_Resolved',  'eeqq_Merged', 'mumuqq_Merged'}
        self.cats = {'vbf-tagged','b-tagged','untagged'}
        # self.cats = {'b-tagged'}
        self.ifNuisance = True
        self.Template = ["2D"]
        # self.t_values = ['Resolved', 'Merged']
        self.t_values = ['Resolved']
        self.verbose = False
        self.step = ''
        self.ifCondor = 0

    def parse_options(self):
        usage = ('usage: %prog [options] datasetList\n'
                 + '%prog -h for help')
        parser = optparse.OptionParser(usage)

        parser.add_option('-i', '--input', dest='input_dir', type='string', default="",    help='inputs directory')
        parser.add_option('-d', '--is2D',   dest='is_2d',       type='int',    default=1,     help='is2D (default:1)')
        parser.add_option('-a', '--append', dest='append_name', type='string', default="",    help='append name for cards dir')
        parser.add_option('-f', '--fracVBF',   dest='frac_vbf',       type='float',    default=0.005,     help='fracVBF (default:0.5%)')
        parser.add_option("-y","--year",dest="year",type='string', default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
        parser.add_option("-s","--step",dest="step",type='string', default='dc', help="Which step to run: dc (DataCardCreation), cc (CombineCards), rc (RunCombine), or all")
        parser.add_option("-c","--ifCondor",dest="ifCondor",type='int', default=0, help="if you want to run  combine command for all mass points parallel using condor make it 1")

        options, args = parser.parse_args()

        if (options.is_2d != 0 and options.is_2d != 1):
            print('The input '+options.is_2d+' is unkown for is2D.  Please choose 0 or 1. Exiting...')
            sys.exit()

        if (options.append_name == ''):
            print('Please pass an append name for the cards directory! Exiting...')
            sys.exit()

        if (options.input_dir == ''):
            print('Please pass an input directory! Exiting...')
            sys.exit()

        self.input_dir = options.input_dir
        self.is_2d = options.is_2d
        self.append_name = options.append_name
        self.frac_vbf = options.frac_vbf
        self.year = options.year
        self.dir_name = 'datacards_HIG_23_001/cards_'+self.append_name
        self.step = options.step
        self.ifCondor = options.ifCondor

    def make_directory(self, sub_dir_name):
        if not os.path.exists(sub_dir_name):
            if self.verbose: print("{}{}\nCreate directory: {}".format('\t\n', '#'*51, sub_dir_name))
            os.makedirs(sub_dir_name)
        else:
            if self.verbose: print('Directory '+sub_dir_name+' already exists. Exiting...')

    def Run(self):

        if self.ifCondor:
            self.make_directory('output/{}'.format(self.year))
            RemoveFile('arguments_{}.txt'.format(self.year)) # Delete old argument files as the main script will append.
            with open("condor_job_{}.jdl".format(self.year), "w") as cnd_out:
                cnd_out.write(condor.format(year = self.year))
            with open("run_script_{}.sh".format(self.year), "w") as scriptfile:
                scriptfile.write(script)

        # STEP - 1: For Datacard and workspace creation step load datacard class
        if (self.step).lower() == 'dc' or (self.step).lower() == 'all':
            print ("[INFO] declar datacardClass")
            myClass = datacardClass(self.year)

            if self.verbose: print ("[INFO] load root module")
            myClass.loadIncludes()

        for current_mass in range(self.start_mass, self.end_val, self.step_sizes):
            if (self.step).lower() == 'plot': continue
            RunCommand("#"*85)
            cwd = os.getcwd()
            CurrentMassDirectory = self.dir_name + '/' + '/HCG/' + str(current_mass)
            print('cwd: {}'.format(cwd))
            print('CurrentMassDirectory: {}'.format(CurrentMassDirectory))

            # STEP - 1: Datacard and workspace creation
            if (self.step).lower() == 'dc' or (self.step).lower() == 'all':
                for sub in self.subdir:
                    self.make_directory(self.dir_name + '/'+sub)
                self.make_directory(self.dir_name + '/HCG/' + str(current_mass))
                print("Directory name: {}".format(self.dir_name + '/' + '/HCG/' + str(current_mass)))

                for channel in self.channels:
                    for cat in self.cats:
                        inputreadertxt = self.input_dir+"/"+channel+"_"+cat+".txt"
                        print("inputreadertext: ", inputreadertxt)
                        myReader = inputReader(inputreadertxt)
                        myReader.readInputs()
                        theInputs = myReader.getInputs()
                        myClass.makeCardsWorkspaces(current_mass, self.is_2d, self.dir_name, theInputs, cat,  self.frac_vbf)

            # STEP - 2: Get the combined cards
            if (self.step).lower() == 'cc' or (self.step).lower() == 'all':
                # Change the respective directory where all cards are placed
                os.chdir(CurrentMassDirectory)

                AllCardsCombination = 'combineCards.py  -s '
                for t in self.t_values:
                    RemoveFile("hzz2l2q_mumuqq_{}_13TeV.txt".format(t))
                    RemoveFile("hzz2l2q_eeqq_{}_13TeV.txt".format(t))
                    RemoveFile("hzz2l2q_{}_13TeV_xs.txt".format(t))
                    RemoveFile("hzz2l2q_{}_13TeV_xs.root".format(t))

                    for fs in ["eeqq_{}".format(t), "mumuqq_{}".format(t)]:
                        RunCommand("combineCards.py hzz2l2q_{FinalState}_untagged_13TeV.txt hzz2l2q_{FinalState}_b-tagged_13TeV.txt hzz2l2q_{FinalState}_vbf-tagged_13TeV.txt > hzz2l2q_{FinalState}_13TeV.txt".format(FinalState = fs))

                    RunCommand("combineCards.py hzz2l2q_mumuqq_{Category}_13TeV.txt hzz2l2q_eeqq_{Category}_13TeV.txt > hzz2l2q_{Category}_13TeV_xs.txt".format(Category = t))

                    for cat in self.cats:
                        RunCommand("combineCards.py hzz2l2q_eeqq_{Category}_{Tag}_13TeV.txt hzz2l2q_mumuqq_{Category}_{Tag}_13TeV.txt > hzz2l2q_{Category}_{Tag}_13TeV.txt".format(Category = t,  Tag = cat))

                    AllCardsCombination = AllCardsCombination +' hzz2l2q_{Category}_13TeV_xs.txt'.format(Category = t)
                RunCommand("*"*51)

                AllCardsCombination = AllCardsCombination +' > hzz2l2q_13TeV_xs_NoNuisance.txt'
                AllCardsWithNuisance = (AllCardsCombination.replace('-s','  ')).replace('_NoNuisance','')

                RunCommand(AllCardsWithNuisance)
                RunCommand(AllCardsCombination)
                os.chdir(cwd)


            # STEP - 3: Run Combine commands
            if (self.step).lower() == 'rc' or (self.step).lower() == 'all':
                # TODO:  Combine command should be defined centrally at one place. Whetehr we run using condor or locally it should use the command from one common place.
                datacard = "hzz2l2q_13TeV_xs.txt" if  self.ifNuisance else "hzz2l2q_13TeV_xs_NoNuisance.txt"
                print('datacard: {}'.format(datacard))
                if self.ifCondor:
                    LocalDir = os.getcwd()
                    print('PWD: {}'.format(LocalDir))

                    with open("arguments_{}.txt".format(self.year), "a") as inArgFile:
                        inArgFile.write("{JOBID}  {LOCAL}  {MH}  {DATACARD}\n".format(JOBID = 1, LOCAL = LocalDir+'/'+CurrentMassDirectory, MH=current_mass, DATACARD = datacard))

                else:
                    # Change the respective directory where all cards are placed
                    os.chdir(CurrentMassDirectory)
                    RunCommand("combine -n mH{mH}_exp -m {mH} -M AsymptoticLimits  {datacard}  --rMax 1 --rAbsAcc 0 --run blind > {type}_mH{mH}_exp.log".format(type = self.Template[0], mH = current_mass, datacard = datacard))
                    os.chdir(cwd)

            if (self.step).lower() == 'ri' or (self.step).lower() == 'all':
                datacard = "hzz2l2q_13TeV_xs.txt" if  self.ifNuisance else "hzz2l2q_13TeV_xs_NoNuisance.txt"
                print('datacard: {}'.format(datacard))

                os.chdir(CurrentMassDirectory)
                command = "text2workspace.py " + datacard + " -m " + str(current_mass)  + " -o " + datacard.replace(".txt", ".root")
                RunCommand(command)
                command = "combineTool.py -M Impacts -d " + datacard.replace(".txt", ".root") + " -m "+str(current_mass)+" --rMin -1 --rMax 2 --robustFit 1 --doInitialFit  -t -1 --expectSignal 1"
                RunCommand(command)
                command = "combineTool.py -M Impacts -d " + datacard.replace(".txt", ".root") + " -m "+str(current_mass)+" --rMin -1 --rMax 2 --robustFit 1 --doFits" # --job-mode condor --sub-opts='+JobFlavour=\"workday\"' --task-name jobs_test2
                RunCommand(command)
                command = "combineTool.py -M Impacts -d " + datacard.replace(".txt", ".root") + " -m "+str(current_mass)+" --rMin -1 --rMax 2 --robustFit 1  --output impacts.json"
                RunCommand(command)
                command = "plotImpacts.py -i impacts.json -o impacts"+str(current_mass)
                RunCommand(command)
                os.chdir(cwd)

        if (self.step).lower() == 'plot':
            command = 'python plotLimitExpObs_2D.py {}  {}  {}  {}'.format(self.start_mass, self.end_val, self.step_sizes, self.year)
            RunCommand(command)

        if self.ifCondor:
            print('For running condor jobs do following:')
            print('1. set up proxy:')
            print('\nvoms-proxy-init --voms cms --valid 168:00')
            print('2. Submit the condor jobs:')
            print("\ncondor_submit condor_job_{}.jdl".format(self.year))

if __name__ == "__main__":
    dc = DirectoryCreator()
    dc.parse_options()
    dc.Run()
