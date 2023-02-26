import os
from inputReader import *
from datacardClass import *
from utils import *
import common_strings_pars
import argparse


class DirectoryCreator:

    def __init__(self, input_dir="", is_2d=1, MassStartVal = 500, MassEndVal = 3001, MassStepVal = 50, append_name="", frac_vbf=0.005, year="2016", step="dc", ifCondor=False, blind=True, verbose=True):
        self.input_dir = input_dir
        self.is_2d = is_2d
        self.append_name = append_name
        self.frac_vbf = frac_vbf
        self.year = year
        self.start_mass = MassStartVal
        self.step_sizes = MassStepVal
        self.end_val = MassEndVal
        self.subdir = ['HCG','figs']
        self.dir_name = 'datacards_HIG_23_001/cards_'+self.append_name
        self.channels = {'eeqq_Resolved', 'mumuqq_Resolved', 'eeqq_Merged', 'mumuqq_Merged'}
        self.cats = {'vbf-tagged','b-tagged','untagged'}
        self.ifNuisance = True
        self.Template = ["2D"]
        self.t_values = ['Resolved', 'Merged']
        self.verbose = verbose
        self.step = step
        self.ifCondor = ifCondor
        self.blind = blind

    def Run(self, year = '2016'):

        # STEP - 1: For Datacard and workspace creation step load datacard class
        if (self.step).lower() == 'dc' or (self.step).lower() == 'all':
            print ("[INFO] declar datacardClass")
            myClass = datacardClass(str(year), self.verbose)

            if self.verbose: print ("[INFO] load root module")
            myClass.loadIncludes()

        # Default name of combined datacard
        datacard = "hzz2l2q_13TeV_xs.txt" if  self.ifNuisance else "hzz2l2q_13TeV_xs_NoNuisance.txt"

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
                    make_directory(self.dir_name + '/'+sub)
                make_directory(self.dir_name + '/HCG/' + str(current_mass))
                print("Directory name: {}".format(self.dir_name + '/' + '/HCG/' + str(current_mass)))

                for channel in self.channels:
                    for cat in self.cats:
                        inputreadertxt = self.input_dir+"/"+channel+"_"+cat+".txt"
                        if (self.verbose): print("inputreadertext: ", inputreadertxt)
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

                print('datacard: {}'.format(datacard))
                if self.ifCondor:
                    LocalDir = os.getcwd()
                    print('PWD: {}'.format(LocalDir))

                    os.chdir(CurrentMassDirectory)
                    command = "combineTool.py -M AsymptoticLimits -d {datacard} -m {mH} --rMin -1 --rMax 1 --rAbsAcc 0  -n {name}".format(mH = current_mass, datacard = datacard, name = common_strings_pars.COMBINE_ASYMP_LIMIT.format(year = year, mH = current_mass))
                    command += " --run blind "
                    # command += " --run expected "
                    # command += " --run blind -t -1 "
                    # command += " --run blind -t -1 --expectSignal 1 "
                    # command += " --run blind -t -1 --expectSignal 0 "
                    # command += " --dry-run "
                    command += "--job-mode condor --sub-opts='+JobFlavour=\"longlunch\"' --task-name {name}".format(mH=current_mass, name = common_strings_pars.COMBINE_ASYMP_LIMIT.format(year = year, mH = current_mass))
                    # microcentury = 1 hr
                    # longlunch = 2 hr
                    RunCommand(command)
                    os.chdir(cwd)

                else:
                    # Change the respective directory where all cards are placed
                    os.chdir(CurrentMassDirectory)
                    command = "combine -n {name} -m {mH} -M AsymptoticLimits  {datacard}  --rMax 1 --rAbsAcc 0 --run blind > {type}_mH{mH}_exp.log".format(type = self.Template[0], mH = current_mass, datacard = datacard, name = common_strings_pars.COMBINE_ASYMP_LIMIT.format(year = year, mH = current_mass))

                    RunCommand(command)
                    os.chdir(cwd)

            if (self.step).lower() == 'ri' or (self.step).lower() == 'all':

                print('datacard: {}'.format(datacard))

                os.chdir(CurrentMassDirectory)
                command = "text2workspace.py {datacard}.txt  -m {mH} -o {datacard}.root".format( datacard = datacard.replace(".txt", ""), mH = current_mass)
                #RunCommand(command)
                # SetParRange = ' --setParameterRanges r=-1,2:frac_VBF=0,1'
                SetParRange = ' --setParameterRanges frac_VBF=0,1'

                # STEP - 1
                command = "combineTool.py -M Impacts -d {datacard}  -m {mH} --rMin -1 --rMax 2 --robustFit 1 --doInitialFit ".format(datacard = datacard.replace(".txt", ".root"), mH = current_mass)   # Main command
                if self.blind: command += " -t -1 --expectSignal 1 "
                # command +=  " --cminFallbackAlgo Minuit,1:10 --setRobustFitStrategy 2 " # Added this line as fits were failing
                # command +=  " --freezeNuisanceGroups check "  # To freese the nuisance group named check
                command += "--job-mode condor --sub-opts='+JobFlavour=\"longlunch\"' --task-name impact_step1_{mH}_{year}".format(year = year, mH = current_mass)
                #RunCommand(command)

                # STEP - 2
                command = "combineTool.py -M Impacts -d {datacard}  -m {mH} --rMin -1 --rMax 2 --robustFit 1 --doFits ".format(datacard = datacard.replace(".txt", ".root"), mH = current_mass)
                if self.blind: command += " -t -1 --expectSignal 1 "
                # command +=  " --cminFallbackAlgo Minuit,1:10 --setRobustFitStrategy 2 " # Added this line as fits were failing
                command += " --job-mode condor --sub-opts='+JobFlavour=\"longlunch\"' --task-name impact_step2_{mH}_{year}".format(year = year, mH = current_mass)

                #RunCommand(command)

                # STEP - 3
                command = "combineTool.py -M Impacts -d {datacard} -m {mH} --rMin -1 --rMax 2 --robustFit 1   --output impacts_mH{mH}_{year}_{blind}.json".format(datacard = datacard.replace(".txt", ".root"), mH = current_mass, year = year, blind = "blind" if self.blind else "")
                RunCommand(command)

                # STEP - 4
                command = "plotImpacts.py -i impacts_mH{mH}_{year}_{blind}.json -o impacts_{blind}_M{mH}_{year} --blind".format(mH = current_mass, year = year, blind = "blind" if self.blind else "")
                RunCommand(command)
                os.chdir(cwd)

            if (self.step).lower() == 'rll':

                print('datacard: {}'.format(datacard))

                os.chdir(CurrentMassDirectory)
                # First do a fit and save a workspace with a snapshot of the parameters at the best fit
                command = "combine -M MultiDimFit " + str(datacard) + " -n .snapshot -m "+str(current_mass)+" --rMin -3 --rMax 3 --algo grid --points 100 --saveWorkspace -t -1 --expectSignal 1"
                RunCommand(command)

                # Then re-run the scan with parameters frozen on top of this workspace, restoring the snapshot
                command = "combine -M MultiDimFit higgsCombine.snapshot.MultiDimFit.mH"+str(current_mass)+".root -n .freezeall -m "+str(current_mass)+" --rMin -3 --rMax 3 --algo grid --points 100 --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit  -t -1 --expectSignal 1"
                RunCommand(command)

                # Finally plot the LL scan
                command = "python $CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/plot1DScan.py higgsCombine.snapshot.MultiDimFit.mH"+str(current_mass)+".root --others 'higgsCombine.freezeall.MultiDimFit.mH"+str(current_mass)+".root:FreezeAll:2' -o freeze_all"
                # command = "python $CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/plot1DScan.py higgsCombine.snapshot.MultiDimFit.mH"+str(current_mass)+".root --main-label \"With systematics\" --main-color 1  --others 'higgsCombine.freezeall.MultiDimFit.mH"+str(current_mass)+".root:\"Stat-only\":2' -o freeze_all"
                RunCommand(command)

                os.chdir(cwd)


            if (self.step).lower() == 'Correlation':
                """ Information:
                Simple fits
                """

                print('datacard: {}'.format(datacard))

                os.chdir(CurrentMassDirectory)
                command = "text2workspace.py " + datacard + " -m " + str(current_mass)  + " -o " + datacard.replace(".txt", ".root")
                print(command)

                if (not self.blind):
                    print("Analysis is blinded")
                    pass
                else:
                    pointsToScan = 75
                    ExpectedSignal = 1
                    if ExpectedSignal == 0: OutFileExt = 0
                    else: OutFileExt = 1
                    rRange= "-2,2" # for ExpectedSignal = 1
                    command = "combine -M MultiDimFit {datacard} -m {mH} --freezeParameters MH -n .correlation --cminDefaultMinimizerStrategy 0  --robustHesse 1 --robustHesseSave 1 --saveFitResult  -t -1 --expectSignal  {ExpectedSignal} ".format(datacard=datacard.replace(".txt",".root"), mH=current_mass, ExpectedSignal = ExpectedSignal)
                    RunCommand(command)
                os.chdir(cwd)

            if (self.step).lower() == 'ls':
                """ Information:
                Simple fits
                """

                print('datacard: {}'.format(datacard))

                os.chdir(CurrentMassDirectory)
                command = "text2workspace.py " + datacard + " -m " + str(current_mass)  + " -o " + datacard.replace(".txt", ".root")
                print(command)

                if (not self.blind):
                    print("Analysis is blinded")
                    pass
                else:
                    pointsToScan = 75
                    ExpectedSignal = 1
                    if ExpectedSignal == 0: OutFileExt = 0
                    else: OutFileExt = 1
                    rRange= "-2,2" # for ExpectedSignal = 1
                    command = "combine -M MultiDimFit {datacard} -m {mH} --freezeParameters MH -n .bestfit.with_syst --setParameterRanges r=-1,2.5 --saveWorkspace  -t -1 --expectSignal  {ExpectedSignal}".format(datacard=datacard.replace(".txt",".root"), mH=current_mass, ExpectedSignal = ExpectedSignal)
                    # RunCommand(command)
                    command ="combine -M MultiDimFit higgsCombine.bestfit.with_syst.MultiDimFit.mH{mH}.root -m {mH} --freezeParameters MH,allConstrainedNuisances -n .scan.with_syst.statonly_correct --algo grid --points {pointsToScan} --setParameterRanges r=-1,2.5 --snapshotName MultiDimFit  -t -1 --expectSignal  {ExpectedSignal}".format(datacard=datacard.replace(".txt",".root"), mH=current_mass, ExpectedSignal = ExpectedSignal, pointsToScan = pointsToScan)
                    # RunCommand(command)
                    # command = 'plot1DScan.py higgsCombine.scan.with_syst.MultiDimFit.mH{mH}.root --main-label "With systematics" --main-color 1 --others higgsCombine.scan.with_syst.statonly_correct.MultiDimFit.mH{mH}.root:"Stat-only":2 -o part3_scan_v1 --breakdown syst,stat'.format(datacard=datacard.replace(".txt",".root"), mH=current_mass, ExpectedSignal = ExpectedSignal, pointsToScan = pointsToScan)
                    command = 'plot1DScan.py higgsCombine.bestfit.with_syst.MultiDimFit.mH{mH}.root --main-label "With systematics" --main-color 1 --others higgsCombine.scan.with_syst.statonly_correct.MultiDimFit.mH{mH}.root:"Stat-only":2 -o part3_scan_v1 --breakdown syst,stat'.format(datacard=datacard.replace(".txt",".root"), mH=current_mass, ExpectedSignal = ExpectedSignal, pointsToScan = pointsToScan)
                    RunCommand(command)
                os.chdir(cwd)

        if (self.step).lower() == 'plot':
            command = 'python plotLimitExpObs_2D.py {}  {}  {}  {}'.format(self.start_mass, self.end_val, self.step_sizes, year)
            RunCommand(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create directories")
    parser.add_argument('-i', '--input', dest='input_dir', type=str, default="", help='inputs directory')
    parser.add_argument('-d', '--is2D', dest='is_2d', type=int, default=1, help='is2D (default:1)')
    parser.add_argument('-mi', '--MassStartVal', dest='MassStartVal', type=int, default=500, help='MassStartVal (default:1)')
    parser.add_argument('-mf', '--MassEndVal', dest='MassEndVal', type=int, default=3001, help='MassEndVal (default:1)') # # scan mass end value is 3000, but I added 3001 to include 3000 in for loop. If I write 3000 then it will take last mass value as 2950.
    parser.add_argument('-ms', '--MassStepVal', dest='MassStepVal', type=int, default=50, help='MassStepVal (default:1)')
    parser.add_argument('-a', '--append', dest='append_name', type=str, default="", help='append name for cards dir')
    parser.add_argument('-f', '--fracVBF', dest='frac_vbf', type=float, default=0.005, help='fracVBF (default:0.5%)')
    parser.add_argument("-y", "--year", dest="year", type=str, default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
    parser.add_argument("-s", "--step", dest="step", type=str, default='dc', help="Which step to run: dc (DataCardCreation), cc (CombineCards), rc (RunCombine), ri (run Impact), rll (run loglikelihood with and without syst) , fast (FastScan) or all")
    parser.add_argument("-c", "--ifCondor", action="store_true", dest="ifCondor", default=False, help="if you want to run combine command for all mass points parallel using condor make it 1")
    parser.add_argument("-b", "--blind", action="store_false", dest="blind", default=True, help="Running blind?")
    parser.add_argument("-q", "--quiet", action="store_true", dest="verbose", default=False, help="don't print status messages to stdout")
    args = parser.parse_args()

    DirectoryCreatorObj = DirectoryCreator(args.input_dir, args.is_2d, args.MassStartVal, args.MassEndVal, args.MassStepVal , args.append_name, args.frac_vbf, args.year, args.step, args.ifCondor, args.blind, args.verbose)
    # DirectoryCreatorObj.validate()
    if args.year == '2016': years = [2016]
    if args.year == '2017': years = [2017]
    if args.year == '2018': years = [2018]
    if args.year == 'all': years = [2016, 2017, 2018]
    for year in years:
        DirectoryCreatorObj.Run(year)
