import ROOT

import argparse
parser = argparse.ArgumentParser(description="A simple ttree plotter")
parser.add_argument("-y","--year",dest="year",default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
parser.add_argument("-s","--sample",dest="sample",default='ggh', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
args = parser.parse_args()

year = args.year; sam = args.sample
tags = ['vbf-','b-','un']
channels = ['mumuqq','eeqq']
cases = ['Merged','Resolved']
infile = ROOT.TFile("SigEff/2l2q_Efficiency_spin0_{}_{}.root".format(sam,year))

with open("Eff_{}_{}.txt".format(sam,year), "w") as fout:
    for channel in channels:
        for case in cases:
            for tag in tags:
                fout.write('============================================================================\n')
                fout.write('========================={}_{}_{}tagged===========================\n'.format(channel,case,tag))
                fout.write('============================================================================\n')
                for mass in range(400,3200,50):
                        eff = infile.Get("spin0_{}_{}_{}_{}tagged".format(sam,channel,case,tag)).GetListOfFunctions().First().Eval(mass)
                        fout.write('eff = {} in {}_{}_{}_{}_{}\n'.format(eff,sam,channel,case,tag,mass))
