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

class DirectoryCreator:

    def __init__(self):
        self.input_dir = ""
        self.is_2d = 1
        self.append_name = ""
        self.frac_vbf = 0.005
        self.year = "2016"
        self.start_mass = [500]
        self.step_sizes = [50]
        self.end_val = [51] # if start_mass starts from 200 then use 57, if starts from 500 then 51
        self.subdir = ['HCG','figs']
        self.dir_name = 'cards_'+self.append_name
        self.channels = {'eeqq_Resolved', 'mumuqq_Resolved'}
        # self.channels = {'eeqq_Resolved', 'mumuqq_Resolved',  'eeqq_Merged', 'mumuqq_Merged'}
        self.cats = {'vbf-tagged','b-tagged','untagged'}
        self.ifNuisance = True
        self.Template = ["2D"]
        # self.t_values = ['Resolved', 'Merged']
        self.t_values = ['Resolved']
        self.verbose = False
        self.step = ''

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
        self.dir_name = 'cards_'+self.append_name
        self.step = options.step

    def make_directory(self, sub_dir_name):
        if not os.path.exists(self.dir_name+'/'+sub_dir_name):
            if self.verbose: print("{}{}\nCreate directory: {}".format('\t\n', '#'*51, self.dir_name+'/'+sub_dir_name))
            os.makedirs(self.dir_name+'/'+sub_dir_name)
        else:
            if self.verbose: print('Directory '+self.dir_name+'/'+sub_dir_name+' already exists. Exiting...')

    def Run(self):
        # STEP - 1: For Datacard and workspace creation step load datacard class
        if (self.step).lower() == 'dc' or (self.step).lower() == 'all':
            print ("[INFO] declar datacardClass")
            myClass = datacardClass(self.year)

            if self.verbose: print ("[INFO] load root module")
            myClass.loadIncludes()

        for i in range(len(self.start_mass)):
            for j in range(self.end_val[0]):
                RunCommand("#"*85)
                current_mass = self.start_mass[i] + j*self.step_sizes[i]
                cwd = os.getcwd()
                CurrentMassDirectory = self.dir_name + '/' + '/HCG/' + str(current_mass)
                print('cwd: {}'.format(cwd))
                print('CurrentMassDirectory: {}'.format(CurrentMassDirectory))

                # STEP - 1: Datacard and workspace creation
                if (self.step).lower() == 'dc' or (self.step).lower() == 'all':
                    for sub in self.subdir:
                        self.make_directory(sub)
                    self.make_directory('HCG' + '/' + str(current_mass))
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
                    # Change the respective directory where all cards are placed
                    os.chdir(CurrentMassDirectory)
                    RunCommand("combine -n mH{mH}_exp -m {mH} -M AsymptoticLimits  {datacard}  --rMax 1 --rAbsAcc 0 --run blind > {type}_mH{mH}_exp.log".format(type = self.Template[0], mH = current_mass, datacard = datacard))
                    os.chdir(cwd)

if __name__ == "__main__":
    dc = DirectoryCreator()
    dc.parse_options()
    dc.Run()
