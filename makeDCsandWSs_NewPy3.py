import argparse
import os
from inputReader import *
from datacardClass import *
from utils import *

class DirectoryCreator:

    def __init__(self, input_dir="", is_2d=1, append_name="", frac_vbf=0.005, year="2016", step="dc", ifCondor=False, blind=True, verbose=True):
        self.input_dir = input_dir
        self.is_2d = is_2d
        self.append_name = append_name
        self.frac_vbf = frac_vbf
        self.year = year
        self.start_mass = 500
        self.step_sizes = 50
        self.end_val = 3001
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
        self.quiet = True

    def run(self):
        # STEP - 1: For Datacard and workspace creation step load datacard class
        if self.step.lower() in ['dc', 'all']:
            print(f"[INFO] declare datacardClass for year {self.year}")
            myClass = datacardClass(self.year)

            if self.verbose:
                print("[INFO] loading ROOT module")
            myClass.loadIncludes()

        # Default name of combined datacard
        datacard = "hzz2l2q_13TeV_xs.txt" if self.ifNuisance else "hzz2l2q_13TeV_xs_NoNuisance.txt"

        for current_mass in range(self.start_mass, self.end_val, self.step_sizes):
            if self.step.lower() == 'plot':
                break

            RunCommand("#" * 85)
            cwd = os.getcwd()
            CurrentMassDirectory = f"{self.dir_name}/HCG/{current_mass}" # FIXME: Hardcoded `HCG`
            print(f"cwd: {cwd}")
            print(f"CurrentMassDirectory: {CurrentMassDirectory}")

            # STEP - 1: Datacard and workspace creation
            if self.step.lower() in ['dc', 'all']:
                for sub in self.subdir:
                    make_directory(f"{self.dir_name}/{sub}")
                make_directory(CurrentMassDirectory)
                print(f"Directory name: {CurrentMassDirectory}")

                for channel in self.channels:
                    for cat in self.cats:
                        inputreadertxt = f"{self.input_dir}/{channel}_{cat}.txt"
                        print(f"inputreadertext: {inputreadertxt}")
                        myReader = inputReader(inputreadertxt)
                        myReader.readInputs()
                        theInputs = myReader.getInputs()
                        myClass.makeCardsWorkspaces(current_mass, self.is_2d, self.dir_name, theInputs, cat, self.frac_vbf)

            # STEP - 2: Get the combined cards
            if self.step.lower() in ['cc', 'all']:
                # Change the respective directory where all cards are placed
                os.chdir(CurrentMassDirectory)

                AllCardsCombination = 'combineCards.py -s '
                for t in self.t_values:
                    # for fs in ['eeqq', 'mumuqq']: # FIXME: Check this part!! Do I need this?
                    #     RemoveFile(f"hzz2l2q_{fs}_{t}_13TeV.txt")

                    for fs in ['eeqq', 'mumuqq']:
                        RunCommand(f"combineCards.py hzz2l2q_{fs}_{t}_untagged_13TeV.txt hzz2l2q_{fs}_{t}_b-tagged_13TeV.txt hzz2l2q_{fs}_{t}_vbf-tagged_13TeV.txt > hzz2l2q_{fs}_{t}_13TeV.txt")

                    RunCommand(f"combineCards.py hzz2l2q_eeqq_{t}_13TeV.txt hzz2l2q_mumuqq_{t}_13TeV.txt > hzz2l2q_{t}_13TeV_xs.txt")

                    for cat in self.cats:
                        RunCommand(f"combineCards.py hzz2l2q_eeqq_{t}_{cat}_13TeV.txt hzz2l2q_mumuqq_{t}_{cat}_13TeV.txt > hzz2l2q_{t}_{cat}_13TeV_xs.txt")

                    AllCardsCombination += f" hzz2l2q_{t}_13TeV_xs.txt "

                RunCommand("*" * 51)

                AllCardsCombination += ' > hzz2l2q_13TeV_xs_NoNuisance.txt '
                AllCardsWithNuisance = AllCardsCombination.replace('-s', '')

                RunCommand(AllCardsWithNuisance)
                RunCommand(AllCardsCombination)
                os.chdir(cwd)

    def validate(self):
        # code to validate DirectoryCreator options
        print("In validate")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create directories")
    parser.add_argument('-i', '--input', dest='input_dir', type=str, default="", help='inputs directory')
    parser.add_argument('-d', '--is2D', dest='is_2d', type=int, default=1, help='is2D (default:1)')
    parser.add_argument('-a', '--append', dest='append_name', type=str, default="", help='append name for cards dir')
    parser.add_argument('-f', '--fracVBF', dest='frac_vbf', type=float, default=0.005, help='fracVBF (default:0.5%)')
    parser.add_argument("-y", "--year", dest="year", type=str, default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
    parser.add_argument("-s", "--step", dest="step", type=str, default='dc', help="Which step to run: dc (DataCardCreation), cc (CombineCards), rc (RunCombine), ri (run Impact), rll (run loglikelihood with and without syst) , fast (FastScan) or all")
    parser.add_argument("-c", "--ifCondor", action="store_true", dest="ifCondor", default=False, help="if you want to run combine command for all mass points parallel using condor make it 1")
    parser.add_argument("-b", "--blind", action="store_false", dest="blind", default=True, help="Running blind?")
    parser.add_argument("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")
    args = parser.parse_args()

    DirectoryCreatorObj = DirectoryCreator(args.input_dir, args.is_2d, args.append_name, args.frac_vbf, args.year, args.step, args.ifCondor, args.blind, args.verbose)
    DirectoryCreatorObj.validate()
    DirectoryCreatorObj.run()
