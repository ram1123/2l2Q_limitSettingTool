import os
import sys
import optparse
from inputReader import *
from datacardClass import *

class DirectoryCreator:

    def __init__(self):
        self.input_dir = ""
        self.is_2d = 1
        self.append_name = ""
        self.frac_vbf = 0.005
        self.year = "2016"
        self.start_mass = [500]
        self.step_sizes = [50]
        self.end_val = [1]
        self.subdir = ['HCG','figs']
        self.dir_name = 'cards_'+self.append_name
        self.channels = {'eeqq_Resolved', 'mumuqq_Resolved'}
        # self.channels = {'eeqq_Resolved', 'mumuqq_Resolved',  'eeqq_Merged', 'mumuqq_Merged'}
        self.cats = {'vbf-tagged','b-tagged','untagged'}

    def parse_options(self):
        usage = ('usage: %prog [options] datasetList\n'
                 + '%prog -h for help')
        parser = optparse.OptionParser(usage)

        parser.add_option('-i', '--input', dest='input_dir', type='string', default="",    help='inputs directory')
        parser.add_option('-d', '--is2D',   dest='is_2d',       type='int',    default=1,     help='is2D (default:1)')
        parser.add_option('-a', '--append', dest='append_name', type='string', default="",    help='append name for cards dir')
        parser.add_option('-f', '--fracVBF',   dest='frac_vbf',       type='float',    default=0.005,     help='fracVBF (default:0.5%)')
        parser.add_option("-y","--year",dest="year",type='string', default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")

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

    def make_directory(self, sub_dir_name):
        self.dir_name = 'cards_'+self.append_name
        print(self.dir_name)
        if not os.path.exists(self.dir_name+'/'+sub_dir_name):
            os.makedirs(self.dir_name+'/'+sub_dir_name)
        else:
            print('Directory '+self.dir_name+'/'+sub_dir_name+' already exists. Exiting...')
            # sys.exit()

    def creation_loop(self):
        for i in range(len(self.start_mass)):
            for j in range(self.end_val[i]):
                current_mass = self.start_mass[i] + j*self.step_sizes[i]
                for sub in self.subdir:
                    sub_dir_name = "{}".format(sub)
                    self.make_directory(sub_dir_name)

    def creation_loop(self):
        print ("[INFO] declar datacardClass")
        myClass = datacardClass(self.year)
        print ("[INFO] load root module")
        myClass.loadIncludes()
        for i in range(len(self.start_mass)):
            for j in range(self.end_val[i]):
                current_mass = self.start_mass[i] + j*self.step_sizes[i]
                for sub in self.subdir:
                    self.make_directory(sub)
                self.make_directory('HCG' + '/' + str(self.start_mass[i]))
                print("self.dir_name: ",self.dir_name)
                for channel in self.channels:
                    for cat in self.cats:
                        inputreadertxt = self.input_dir+"/"+channel+"_"+cat+".txt"
                        print("inputreadertext: ", inputreadertxt)
                        myReader = inputReader(inputreadertxt)
                        myReader.readInputs()
                        theInputs = myReader.getInputs()
                        myClass.makeCardsWorkspaces(current_mass, self.is_2d, self.dir_name, theInputs, cat,  self.frac_vbf)


if __name__ == "__main__":
    dc = DirectoryCreator()
    dc.parse_options()
    dc.creation_loop()
