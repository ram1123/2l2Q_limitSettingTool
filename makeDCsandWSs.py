import os
import logging
from inputReader import *
from datacardClass import *
from utils import *
import argparse
from ListOfDatacards import datacardList, datacardList_condor
import multiprocessing as mp
from functools import partial
import datetime

import ROOT


today = datetime.datetime.now()
date_string = today.strftime("%d%b").lower()
import common_strings_pars
CombineStrings = common_strings_pars.CombineStrings(date_string)


def run_parallel_instance(instance, current_mass):
    return instance.run_parallel(current_mass)

class DirectoryCreator:
    DATA_CARD_FILENAME = "hzz2l2q_13TeV_xs.txt"

    def __init__(self, input_dir="", is_2d=1, MassStartVal = 500, MassEndVal = 3001, MassStepVal = 50, append_name="", frac_vbf=0.005, year="2016", step="dc", substep = 1, ifCondor=False, blind=True, verbose=True, allDatacard = False, bOnly = False, dry_run=False, ifParallel = False, SanityCheckPlotUsingWorkspaces = True):
        self.input_dir = input_dir
        self.is_2d = is_2d
        self.append_name = append_name
        self.frac_vbf = frac_vbf
        self.year = year
        self.start_mass = MassStartVal
        self.step_sizes = MassStepVal
        self.end_val = MassEndVal
        self.subdir = ['HCG','figs']
        self.dir_name = 'datacards_HIG_23_001'
        self.channels = {'eeqq_Resolved', 'mumuqq_Resolved', 'eeqq_Merged', 'mumuqq_Merged'}
        self.cats = {'vbf_tagged','b_tagged','untagged'}
        self.ifNuisance = True
        self.Template = ["2D"]
        self.t_values = ['Resolved', 'Merged']
        self.step = step
        self.substep = substep
        self.ifCondor = ifCondor
        self.blind = blind
        self.allDatacard = allDatacard
        self.bOnly = bOnly
        self.verbose = verbose
        self.dry_run = dry_run
        self.ifParallel = ifParallel
        self.SanityCheckPlotUsingWorkspaces = SanityCheckPlotUsingWorkspaces

    def SetDirName(self):
        self.dir_name = 'datacards_HIG_23_001/cards_'+str(self.year)
        if self.append_name != "":
            self.dir_name = self.dir_name + '_' + self.append_name
        if self.frac_vbf != -1:
            self.dir_name = self.dir_name + '_fVBF' + str(self.frac_vbf)
        for sub in self.subdir:
            make_directory(self.dir_name + '/'+sub)

    def SetYearRelatedStrings(self, year):
        self.year = year
        self.input_dir = 'HM_inputs_{}UL'.format(year)

    def create_workspaces(self, current_mass, datacard_class):
        # STEP - 1: Datacard and workspace creation
        border_msg("Creating datacards and workspaces for mass: {}".format(current_mass))

        # create the directory for the current mass: self.dir_name + '/HCG/' + str(current_mass)
        directoryName = os.path.join(self.dir_name, 'HCG', str(current_mass))
        make_directory(directoryName)

        logger.debug("Directory name: {}".format(directoryName))

        for channel in self.channels:
            for cat in self.cats:
                input_reader_txt = self.input_dir+"/"+channel+"_"+cat+".txt"
                logger.debug("inputreadertext: {}".format(input_reader_txt))
                input_reader = inputReader(input_reader_txt)
                input_reader.readInputs()
                theInputs = input_reader.getInputs()
                datacard_class.makeCardsWorkspaces(current_mass, self.is_2d, self.dir_name, theInputs, cat,  self.frac_vbf, self.SanityCheckPlotUsingWorkspaces)

    def combine_cards(self, current_mass, current_mass_directory, cwd):
        # STEP - 2: Get the combined cards
        if self.year == 'run2':
            logger.info("Running combine_cards_allYears")
            self.combine_cards_allYears(current_mass, current_mass_directory, cwd)
            return

        # Change the respective directory where all cards are placed
        os.chdir(current_mass_directory)
        AllCardsCombination = 'combineCards.py  -s '
        for t in self.t_values:
            # if int(current_mass) >= 2800:
            #     if t == 'Resolved':
            #         logger.warning("current mass value: {}, but the Resolved category not available for mH >= 2800".format(current_mass))
            #         continue
            RemoveFile("hzz2l2q_mumuqq_{}_13TeV.txt".format(t))
            RemoveFile("hzz2l2q_eeqq_{}_13TeV.txt".format(t))
            RemoveFile("hzz2l2q_{}_13TeV_xs.txt".format(t))
            RemoveFile("hzz2l2q_{}_13TeV_xs.root".format(t))

            for fs in ["eeqq_{}".format(t), "mumuqq_{}".format(t)]:
                RunCommand("combineCards.py {FinalState}_untagged=hzz2l2q_{FinalState}_untagged_13TeV.txt {FinalState}_b_tagged=hzz2l2q_{FinalState}_b_tagged_13TeV.txt {FinalState}_vbf_tagged=hzz2l2q_{FinalState}_vbf_tagged_13TeV.txt > hzz2l2q_{FinalState}_13TeV.txt".format(FinalState = fs), self.dry_run)

            RunCommand("combineCards.py mumuqq_{Category}=hzz2l2q_mumuqq_{Category}_13TeV.txt eeqq_{Category}=hzz2l2q_eeqq_{Category}_13TeV.txt > hzz2l2q_{Category}_13TeV_xs.txt".format(Category = t), self.dry_run)

            for cat in self.cats:
                RunCommand("combineCards.py eeqq_{Category}_{Tag}=hzz2l2q_eeqq_{Category}_{Tag}_13TeV.txt mumuqq_{Category}_{Tag}=hzz2l2q_mumuqq_{Category}_{Tag}_13TeV.txt > hzz2l2q_{Category}_{Tag}_13TeV.txt".format(Category = t,  Tag = cat), self.dry_run)

            AllCardsCombination = AllCardsCombination +' {Category}=hzz2l2q_{Category}_13TeV_xs.txt'.format(Category = t)
        RunCommand("{stringg}\t {mH} \t {stringg}".format(stringg = "*"*11, mH = current_mass))

        AllCardsCombination = AllCardsCombination +' > hzz2l2q_13TeV_xs_NoNuisance.txt'
        AllCardsWithNuisance = (AllCardsCombination.replace('-s','  ')).replace('_NoNuisance','')

        RunCommand(AllCardsWithNuisance, self.dry_run)
        RunCommand(AllCardsCombination, self.dry_run)
        os.chdir(cwd)

    def combine_cards_allYears(self, current_mass, current_mass_directory, cwd):
        # Go to a new directory named `cards_Run2_Combined` inside `datacards_HIG_23_001` where all three years cards are combined  and workspace is created
        logger.info("Combining cards for all years")
        logger.debug("Current directory: {}".format(os.getcwd()))
        make_directory(current_mass_directory)
        os.chdir(current_mass_directory)
        logger.debug("Current directory: {}".format(os.getcwd()))
        AllCardsCombination = 'combineCards.py -s '
        for year in ['2016', '2017', '2018']:
            # AllCardsCombination = AllCardsCombination +' Era{year}=../../../{cards_{year}{additionalString}}/HCG/{mH}/{datacard}'.format(mH = current_mass, year = year, datacard = self.DATA_CARD_FILENAME, additionalString = "" if self.append_name == "" else "_"+self.append_name)
            AllCardsCombination = AllCardsCombination +' Era{year}=../../../{Run2_Cards}/HCG/{mH}/{datacard}'.format(mH = current_mass, year = year, datacard = self.DATA_CARD_FILENAME, additionalString = "" if self.append_name == "" else "_"+self.append_name, Run2_Cards = (self.dir_name).replace("datacards_HIG_23_001/","").replace("run2",year))
        AllCardsCombination = AllCardsCombination +' > {datacard}'.format(datacard = "hzz2l2q_13TeV_xs_NoNuisance.txt")
        AllCardsCombination = AllCardsCombination +' > hzz2l2q_13TeV_xs_NoNuisance.txt'
        AllCardsWithNuisance = (AllCardsCombination.replace('-s','  ')).replace('_NoNuisance','')

        RunCommand(AllCardsCombination, self.dry_run)
        RunCommand(AllCardsWithNuisance, self.dry_run)
        os.chdir(cwd)


    def run_combine(self, current_mass, current_mass_directory, cwd):
    # STEP - 3: run Combine commands
        if self.allDatacard:
            datacards = datacardList
        else:
            datacards = [self.DATA_CARD_FILENAME]

        logger.debug("Datacard: {}".format(datacards))
        for datacard in datacards:
            # TODO:  Combine command should be defined centrally at one place. Whetehr we run using condor or locally it should use the command from one common place.
            category = ((((datacard.replace("hzz2l2q_","")).replace("_13TeV","")).replace(".txt","")).replace("_xs","")).replace("13TeV","")
            AppendNameString = CombineStrings.COMBINE_ASYMP_LIMIT.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = category)

            # -M HybridNew --LHCmode LHC-limits
            CombineCommonArguments = ' -M AsymptoticLimits -d {datacard} -m {mH} --rMin -1 --rMax 2 --rAbsAcc 0  -n .{name} '.format(mH = current_mass, datacard = datacard, name = AppendNameString)
            CombineCommonArgumentsHybrid = ' -M HybridNew --LHCmode LHC-limits -d {datacard} -m {mH} --rMin -1 --rMax 2 --rAbsAcc 0  -n .{name}Hybrid '.format(mH = current_mass, datacard = datacard, name = AppendNameString)
            # FIXME: Only for debug:
            #CombineCommonArguments += " --freezeParameters MH,allConstrainedNuisances "
            if self.blind:
                CombineCommonArguments += " --run blind "
                CombineCommonArgumentsHybrid += "  -t -1 --expectSignal 1  "
                # CombineCommonArguments += " --run expected "
                # CombineCommonArguments += " --run blind -t -1 "
                # CombineCommonArguments += " --run blind -t -1 --expectSignal 1 "
                # CombineCommonArguments += " --run blind -t -1 --expectSignal 0 "
            # CombineCommonArguments += " --dry-run "
            if self.ifCondor:
                LocalDir = os.getcwd()
                os.chdir(current_mass_directory)
                command = "combineTool.py " + CombineCommonArguments
                commandHybrid = "combineTool.py " + CombineCommonArgumentsHybrid

                Condor_queue = datacardList_condor[datacard] # Get the condor queue from the dictionary datacardList_condor defined in the file ListOfDatacards.py
                if self.year == 'run2':
                    command += " --job-mode condor --sub-opts='+JobFlavour=\"workday\"\\nRequestCpus=4\\nrequest_memory = 10000' --task-name {name}_AsympLimit".format(mH=current_mass, name = AppendNameString)
                else:
                    command += " --job-mode condor --sub-opts='+JobFlavour=\"{Condor_queue}\"' --task-name {name}_AsympLimit".format(mH=current_mass, name = AppendNameString, Condor_queue = Condor_queue)
                commandHybrid += " --job-mode condor --sub-opts='+JobFlavour=\"tomorrow\"' --task-name {name}_Hybrid".format(mH=current_mass, name = AppendNameString)
                # espresso = 20min
                # microcentury = 1 hr
                # longlunch = 2 hr
                # workday = 8 hr
                # tomorrow = 1 day
                # testmatch = 3 day
                RunCommand(command, self.dry_run)
                #RunCommand(commandHybrid, self.dry_run)
                os.chdir(cwd)

            else:
                # Change the respective directory where all cards are placed
                os.chdir(current_mass_directory)
                command = "combine  {CombineCommonArguments} | tee {name}.log".format(CombineCommonArguments = CombineCommonArguments, name = AppendNameString)

                RunCommand(command, self.dry_run)
                os.chdir(cwd)

    def run_impact(self, current_mass, current_mass_directory, cwd):
        if self.allDatacard:
            datacards = datacardList
        else:
            datacards = [self.DATA_CARD_FILENAME]

        logger.debug('datacards: {}'.format(datacards))
        os.chdir(current_mass_directory)
        countDatacards = 1
        for datacard in datacards:
            logger.debug("===> Submitting {}/{}".format(countDatacards, len(datacards)))
            category = ((((datacard.replace("hzz2l2q_","")).replace("_13TeV","")).replace(".txt","")).replace("_xs","")).replace("13TeV","")
            AppendOutName = CombineStrings.COMBINE_IMPACT.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = category)

            if not os.path.exists(datacard.replace(".txt", ".root")):
                command = "text2workspace.py {datacard}.txt  -m {mH} -o {datacard}.root".format( datacard = datacard.replace(".txt", ""), mH = current_mass)
                RunCommand(command, self.dry_run)

            # SetParRange = ' --setParameterRanges r=-1,2:frac_VBF=0,1'
            SetParRange = ' --setParameterRanges frac_VBF=0,1'

            if args.substep == 1:
                # STEP - 1
                command = "combineTool.py -M Impacts -d {datacard}  -m {mH} --rMin -10  --robustFit 1 --doInitialFit ".format(datacard = datacard.replace(".txt", ".root"), mH = current_mass)   # Main command
                if self.blind: command += " -t -1 --expectSignal 1 "
                # command +=  " --cminFallbackAlgo Minuit,1:10 --setRobustFitStrategy 2  " # Added this line as fits were failing
                # command += " --cminDefaultMinimizerTolerance 0.01  --setRobustFitTolerance 0.01 " # Added this line as fits were failing for some cases
                # command +=  " --freezeNuisanceGroups check "  # To freese the nuisance group named check

                Condor_queue = datacardList_condor[datacard] # Get the condor queue from the dictionary datacardList_condor defined in the file ListOfDatacards.py
                if self.year == 'run2':
                    command += " --job-mode condor --sub-opts='+JobFlavour=\"workday\"\\nRequestCpus=4\\nrequest_memory = 10000' --task-name {name}_ImpactS1".format(name = CombineStrings.COMBINE_IMPACT.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = category))
                else:
                    command += " --job-mode condor --sub-opts='+JobFlavour=\"{Condor_queue}\"' --task-name {name}_ImpactS1".format(name = CombineStrings.COMBINE_IMPACT.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = category), Condor_queue = Condor_queue)

                RunCommand(command, self.dry_run)
            if args.substep == 2:
                # STEP - 2
                command = "combineTool.py -M Impacts -d {datacard}  -m {mH} --rMin -10 --robustFit 1 --doFits ".format(datacard = datacard.replace(".txt", ".root"), mH = current_mass)
                if self.blind: command += " -t -1 --expectSignal 1 "
                command +=  " --cminFallbackAlgo Minuit,1:10 --setRobustFitStrategy 2 " # Added this line as fits were failing
                command += " --cminDefaultMinimizerTolerance 0.01  --setRobustFitTolerance 0.01 " # Added this line as fits were failing for some cases # 2018 mH3000

                Condor_queue = datacardList_condor[datacard] # Get the condor queue from the dictionary datacardList_condor defined in the file ListOfDatacards.py
                if self.year == 'run2':
                    command += " --job-mode condor --sub-opts='+JobFlavour=\"workday\"\\nRequestCpus=4\\nrequest_memory = 10000' --task-name {name}_ImpactS2".format(name = CombineStrings.COMBINE_IMPACT.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = category))
                else:
                    command += " --job-mode condor --sub-opts='+JobFlavour=\"{Condor_queue}\"' --task-name {name}_ImpactS2".format(name = CombineStrings.COMBINE_IMPACT.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = category), Condor_queue = Condor_queue)

                RunCommand(command, self.dry_run)

            if args.substep == 3:
                # STEP - 3
                command = "combineTool.py -M Impacts -d {datacard} -m {mH} --rMin -10  --robustFit 1   --output impacts_{name}.json".format(datacard = datacard.replace(".txt", ".root"), mH = current_mass, name = AppendOutName)
                RunCommand(command, self.dry_run)

                # STEP - 4
                command = "plotImpacts.py -i impacts_{name}.json -o {pathh}/impacts_{name} ".format(pathh =  '../../figs', name = AppendOutName) # --blind
                RunCommand(command, self.dry_run)
            countDatacards += 1
        os.chdir(cwd)

    def run_LHS(self, current_mass, current_mass_directory, cwd): # Commands taken From Ankita
        if self.allDatacard:
            datacards = datacardList
        else:
            datacards = [self.DATA_CARD_FILENAME]

        logger.debug('datacard: {}'.format(self.DATA_CARD_FILENAME))

        os.chdir(current_mass_directory)

        for datacard in datacards:
            # if datacard.root file exists, then skip this step
            if not os.path.exists(datacard.replace(".txt", ".root")):
                command = "text2workspace.py {datacard}.txt  -m {mH} -o {datacard}.root".format( datacard = datacard.replace(".txt", ""), mH = current_mass)
                RunCommand(command, self.dry_run)

            category = ((((datacard.replace("hzz2l2q_","")).replace("_13TeV","")).replace(".txt","")).replace("_xs","")).replace("13TeV","")
            OutNameAppend = CombineStrings.COMBINE_FITDIAGNOSTIC.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = category)

            OutNameAppend = CombineStrings.COMBINE_FITDIAGNOSTIC.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = category)

            blindString = ""
            FitType = ""
            if self.bOnly and self.blind:
                blindString = " -t -1 --expectSignal 0 "   # b-only fit diagnostics
                FitType = "bOnly"
                OutFileExt = 0
            if (not self.bOnly) and self.blind:
                blindString = " -t -1 --expectSignal 1 "   # s+b fit diagnostics
                FitType = "SplusB"
                OutFileExt = 1

            if (not self.blind):
                logger.debug("Analysis is blinded")
                pass
            else:
                pointsToScan = 200
                rRange= "-3,3" # for ExpectedSignal = 1
                CommonArguments = ' --algo grid --points {pointsToScan}'.format(pointsToScan = pointsToScan)
                name = "nominal.with_syst_" + "points"+str(pointsToScan)   # String append to the name of floting pars
                name2 = "bestfit.with_syst_" + "points"+str(pointsToScan) # String append to the name of AllConstrainedNuisances
                name3 = "scan.with_syst.statonly_correct_" + "points"+str(pointsToScan) # String append to the name of AllConstrainedNuisances
                outPDFName = OutNameAppend + "_points"+str(pointsToScan) # Output PDF File

                CondorCommandPatch = " -v -1  --job-mode condor --sub-opts='+JobFlavour=\"tomorrow\"\\nRequestCpus=4\\nrequest_memory = 10000' --task-name {name}_LHS".format(name = CombineStrings.COMBINE_IMPACT.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = category))

                if args.substep == 1:
                    # STEP - 1
                    command = " -M MultiDimFit --algo grid --points {pointsToScan} --rMin -3 --rMax 3 -d {datacard} -m {mH} -n .{name} --saveWorkspace {blindString}  ".format(pointsToScan = pointsToScan, datacard = datacard.replace(".txt",".root"), mH = current_mass, blindString = blindString, name = name)
                    # while running on condor, switch the verbosity level to -1 (very quite)
                    if self.ifCondor:
                        command = "combineTool.py " + command + CondorCommandPatch+"Step1"
                    else:
                        command = "combine " + command
                    RunCommand(command + " | tee LHS_Float.log", self.dry_run)

                if args.substep == 2:
                    # STEP - 2
                    command = " -M MultiDimFit --algo none --rMin -3 --rMax 3 -d {datacard} -m {mH} -n .{name} --saveWorkspace {blindString} ".format(datacard = datacard.replace(".txt",".root"), mH = current_mass, blindString = blindString, name = name2) # FIXME: name
                    # while running on condor, switch the verbosity level to -1 (very quite)
                    if self.ifCondor:
                        command = "combineTool.py " + command + CondorCommandPatch+"Step2"
                    else:
                        command = "combine " + command
                    RunCommand(command + " | tee LHS_AllConstrained.log", self.dry_run)

                    # STEP - 3
                    command = " -M MultiDimFit higgsCombine.{name}.MultiDimFit.mH{mH}.root -m {mH} --freezeParameters allConstrainedNuisances -n .{name3} --rMin -3 --rMax 3 --snapshotName MultiDimFit {blindString} --algo grid --points {pointsToScan} ".format(name = name, name3 = name3, mH = current_mass, blindString = blindString, pointsToScan = pointsToScan)
                    if self.ifCondor:
                        command = "combineTool.py " + command + CondorCommandPatch+"Step3"
                    else:
                        command = "combine " + command
                    RunCommand(command + " | tee LHS_plot.log", self.dry_run)

                if args.substep == 3:
                    # STEP - 4
                    command = "plot1DScan.py higgsCombine.{name}.MultiDimFit.mH{mH}.root --main-label \"With systematics\" --main-color 1 --others higgsCombine.{name3}.MultiDimFit.mH{mH}.root:\"Stat-only\":2 -o {outPDFName} --breakdown syst,stat".format(datacard=datacard.replace(".txt",".root"), mH=current_mass, pointsToScan = pointsToScan, name = name, name3 = name3, outPDFName = '../../figs/'+outPDFName)
                    RunCommand(command + " | tee LHS_plot.log", self.dry_run)

                ############################################
                #       Version 2 of LHS: https://twiki.cern.ch/twiki/bin/view/Sandbox/TestTopic11111180#Likelihood_scan
                ############################################
                if args.substep == 21:
                    # # STEP - 1: Inclusive likelihood scan with syst and stats:
                    # combineTool.py -M MultiDimFit --algo grid --points 100 --rMin 0 --rMax 3 ttHmultilep_WS.root --alignEdges 1 --floatOtherPOIs=1 -P r_ttH -n .likelihoodscan --saveWorkspace
                    command = "combineTool.py -M MultiDimFit --algo grid --points {pointsToScan} --rMin 0 --rMax 3 {datacard} --alignEdges 1 --floatOtherPOIs=1  -n .likelihoodscan --saveWorkspace  -m {mH} ".format(pointsToScan = pointsToScan, datacard = datacard.replace(".txt",".root"), mH = current_mass)
                    if self.ifCondor:
                        command = "combineTool.py " + command + CondorCommandPatch+"Step21"
                    else:
                        command = "combine " + command
                    RunCommand(command + " ", self.dry_run)

                if args.substep == 22:
                    # # STEP - 2: Plot inclusive likelihood scan:
                    # plot1DScan.py all.root  --y-cut 50 --y-max 50
                    command = "plot1DScan.py higgsCombine.likelihoodscan.MultiDimFit.mH125.root  --y-cut 50 --y-max 50"
                    RunCommand(command + " ", self.dry_run)

                if args.substep == 23:
                    # # STEP - 3: Get statistical only component:
                    # combine -M MultiDimFit higgsCombine.likelihoodscan.MultiDimFit.mH125.root -n .likelihoodscan.freezeAll -m 125 --rMin 0 --rMax 3  --algo grid --points 30 --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit --alignEdges 1 --floatOtherPOIs=1 -P r_ttH
                    command = "combine -M MultiDimFit higgsCombine.likelihoodscan.MultiDimFit.mH{mH}.root -n .likelihoodscan.freezeAll -m {mH} --rMin 0 --rMax 3  --algo grid --points {pointsToScan} --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit --alignEdges 1 ".format(pointsToScan = pointsToScan, mH = current_mass)
                    if self.ifCondor:
                        command = "combineTool.py " + command + CondorCommandPatch+"Step23"
                    else:
                        command = "combine " + command
                    RunCommand(command + " ", self.dry_run)

                if args.substep == 24:
                    # # STEP - 4: Plot breakdown stat and syst:
                    # plot1DScan.py higgsCombine.likelihoodscan.MultiDimFit.mH125.root --POI r_ttH --y-cut 50 --y-max 50 --breakdown syst,stat --others "higgsCombine.likelihoodscan.freezeAll.MultiDimFit.mH125.root:Stat only:2"
                    command = "plot1DScan.py higgsCombine.likelihoodscan.MultiDimFit.mH125.root --y-cut 50 --y-max 50 --breakdown syst,stat --others \"higgsCombine.likelihoodscan.freezeAll.MultiDimFit.mH{mH}.root:Stat only:2\"".format(mH = current_mass)
                    RunCommand(command + " ", self.dry_run)

                # # From Chenguang:
                # if args.substep == 31:
                #     # syst + stat
                #     # combine -P MH --floatOtherPOIs=1 --robustFit=0 --saveInactivePOI 1 --algo=grid --setParameters MH=125.38,r=1.0 --saveWorkspace -M MultiDimFit -m 125.38 -d inputworkspace.root --points 40 --firstPoint 0 --lastPoint 9 -n outputworkspace
                #     command = "combineTool.py -P MH --floatOtherPOIs=1 --robustFit=0 --saveInactivePOI 1 --algo=grid --setParameters MH={mH},r=1.0 --saveWorkspace -M MultiDimFit -m {mH} -d {datacard} --points {pointsToScan} --firstPoint 0 --lastPoint 9 -n {name}".format(mH = current_mass, datacard = datacard.replace(".txt",".root"), pointsToScan = pointsToScan, name = name)

                #     # stat

                #     # combine -P MH --floatOtherPOIs=1 --robustFit=0 --saveInactivePOI 1 --algo=grid --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit -M MultiDimFit -m 125.38 -d outputworkspace.root --points 40 --firstPoint 0 --lastPoint 9 -n run12_hzz_all_13TeV_massmodelforMH_Scan_MH_120p0_130p0_nosyst_condor_obs.POINTS.0.

        os.chdir(cwd)

    def run_2DLHS(self, current_mass, current_mass_directory, cwd):
        logger.debug('datacard: {}'.format(self.DATA_CARD_FILENAME))

        os.chdir(current_mass_directory)
        command = "text2workspace.py " + self.DATA_CARD_FILENAME + " -m " + str(current_mass)  + " -o " + self.DATA_CARD_FILENAME.replace(".txt", ".root")
        logger.debug(command)

        category = ((((self.DATA_CARD_FILENAME.replace("hzz2l2q_","")).replace("_13TeV","")).replace(".txt","")).replace("_xs","")).replace("13TeV","")
        OutNameAppend = CombineStrings.COMBINE_FITDIAGNOSTIC.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = category)

        blindString = ""
        FitType = ""
        if self.bOnly and self.blind:
            blindString = " -t -1 --expectSignal 0 "   # b-only fit diagnostics
            FitType = "bOnly"
            OutFileExt = 0
        if (not self.bOnly) and self.blind:
            blindString = " -t -1 --expectSignal 1 "   # s+b fit diagnostics
            FitType = "SplusB"
            OutFileExt = 1

        if (not self.blind):
            logger.debug("Analysis is blinded")
            pass
        else:
            pointsToScan = 50
            rRange= "-3,3" # for ExpectedSignal = 1
            CommonArguments = ' --algo grid --points {pointsToScan}'.format(pointsToScan = pointsToScan)
            name = "bestfit.with_syst_" + "points"+str(pointsToScan)   # String append to the name of floting pars
            name2 = "scan.with_syst.statonly_correct_" + "points"+str(pointsToScan) # String append to the name of AllConstrainedNuisances
            outPDFName = OutNameAppend + "_points"+str(pointsToScan) # Output PDF File

            command = "combine -M MultiDimFit -d {datacard} -m {mH} --freezeParameters MH -n .{name} --setParameterRanges r={rRange} --saveWorkspace  {blindString}".format(datacard=self.DATA_CARD_FILENAME.replace(".txt",".root"), mH=current_mass, blindString = blindString, rRange = rRange, name = name)
            command += CommonArguments
            RunCommand(command + " | tee LHS_Float.log", self.dry_run)

            command = "combine -M MultiDimFit datacard_part6_combined_multiSignalModel.root -m 125 --freezeParameters MH -n .scan2D.part6_multiSignalModel --algo grid --points 800 --cminDefaultMinimizerStrategy 0 -P r_ggH -P r_VBF --setParameterRanges r_ggH=0.5,2.5:r_VBF=-1,2"
            command = "combine -M MultiDimFit {datacard} -m {mH} --freezeParameters MH -n .{name} --algo grid --points 200 --cminDefaultMinimizerStrategy 0 -P r_ggH -P r_VBF --setParameterRanges r_ggH=0.5,2.5:r_VBF=-1,2"

            command = 'plot1DScan.py higgsCombine.{name}.MultiDimFit.mH{mH}.root --main-label "With systematics" --main-color 1 --others higgsCombine.{name2}.MultiDimFit.mH{mH}.root:"Stat-only":2 -o {outPDFName} --breakdown syst,stat'.format(datacard=self.DATA_CARD_FILENAME.replace(".txt",".root"), mH=current_mass, pointsToScan = pointsToScan, name = name, name2 = name2, outPDFName = outPDFName)
            RunCommand(command + " | tee LHS_plot.log", self.dry_run)
        os.chdir(cwd)

    def run_correlation(self, current_mass, current_mass_directory, cwd):
        """ Information:
        Simple fits
        """

        logger.debug('datacard: {}'.format(self.DATA_CARD_FILENAME))

        os.chdir(current_mass_directory)
        command = "text2workspace.py " + self.DATA_CARD_FILENAME + " -m " + str(current_mass)  + " -o " + self.DATA_CARD_FILENAME.replace(".txt", ".root")
        RunCommand(command, self.dry_run)

        if (not self.blind):
            logger.debug("Analysis is blinded")
            pass
        else:
            pointsToScan = 75
            ExpectedSignal = 1
            if ExpectedSignal == 0: OutFileExt = 0
            else: OutFileExt = 1
            rRange= "-2,2" # for ExpectedSignal = 1
            command = "combine -M MultiDimFit {datacard} -m {mH} --freezeParameters MH -n .correlation --cminDefaultMinimizerStrategy 0  --robustHesse 1 --robustHesseSave 1 --saveFitResult  -t -1 --expectSignal  {ExpectedSignal} ".format(datacard=self.DATA_CARD_FILENAME.replace(".txt",".root"), mH=current_mass, ExpectedSignal = ExpectedSignal)
            RunCommand(command, self.dry_run)
        os.chdir(cwd)

    def FitDiagnostics(self, current_mass, current_mass_directory, cwd):
        """ Information:
        Simple fits
        """

        if self.allDatacard:
            datacards = datacardList
        else:
            datacards = [self.DATA_CARD_FILENAME]

        logger.debug('datacards: {}'.format(datacards))
        os.chdir(current_mass_directory)
        rRange= "-2,2" # for ExpectedSignal = 1
        for datacard in datacards:
            category = ((((datacard.replace("hzz2l2q_","")).replace("_13TeV","")).replace(".txt","")).replace("_xs","")).replace("13TeV","")
            OutNameAppend = CombineStrings.COMBINE_FITDIAGNOSTIC.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = category)

            blindString = ""
            FitType = ""
            # if self.bOnly and self.blind:
            #     blindString = " -t -1 --expectSignal 0 "   # b-only fit diagnostics
            #     FitType = "bOnly"
            # if (not self.bOnly) and self.blind:
            #     blindString = " -t -1 --expectSignal 1 "   # s+b fit diagnostics
            #     FitType = "SplusB"

            # if pre- and post-fit plots are needed use additional options `--plots --saveShapes` and `--saveWithUncertainties` respectively
            blindString = " -t -1 --expectSignal 0 "   # b-only fit diagnostics
            FitType = "bOnly"
            command = "combineTool.py -M FitDiagnostics  -m {mH}  -d {datacard} --rMin -10   -n .{name}".format(datacard=datacard, mH=current_mass, name = OutNameAppend+"_"+FitType)
            command += blindString

            # always run the FitDiagnostics using condor
            command += " --job-mode condor --sub-opts='+JobFlavour=\"longlunch\"' --task-name {name}_FitDiagnostics_{FitType}".format(name = OutNameAppend, FitType = FitType)
            RunCommand(command, self.dry_run)

            blindString = " -t -1 --expectSignal 1 "   # s+b fit diagnostics
            FitType = "SplusB"
            command = "combineTool.py -M FitDiagnostics  -m {mH}  -d {datacard} --rMin -10   -n .{name}".format(datacard=datacard, mH=current_mass, name = OutNameAppend+"_"+FitType)
            command += blindString

            # always run the FitDiagnostics using condor
            command += " --job-mode condor --sub-opts='+JobFlavour=\"longlunch\"' --task-name {name}_FitDiagnostics_{FitType}".format(name = OutNameAppend, FitType = FitType)
            RunCommand(command, self.dry_run)
        os.chdir(cwd)

    def PrePostFitPlots(self, current_mass, current_mass_directory, cwd):
        """ Information:
        Simple fits
        """

        logger.debug('datacard: {}'.format(self.DATA_CARD_FILENAME))
        os.chdir(current_mass_directory)
        os.chdir(cwd)

    def fastScan(self, current_mass, current_mass_directory, cwd):
        """ Information:
        Analyzing the NLL shape in each parameter: [https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/debugging/#analyzing-the-nll-shape-in-each-parameter](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/debugging/#analyzing-the-nll-shape-in-each-parameter)
        """

        if self.allDatacard:
            datacards = datacardList
        else:
            datacards = [self.DATA_CARD_FILENAME]

        logger.debug('datacards: {}'.format(datacards))
        os.chdir(current_mass_directory)
        rRange= "-2,2" # for ExpectedSignal = 1
        for datacard in datacards:
            category = ((((datacard.replace("hzz2l2q_","")).replace("_13TeV","")).replace(".txt","")).replace("_xs","")).replace("13TeV","")
            OutNameAppend = CombineStrings.COMBINE_FITDIAGNOSTIC.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = category)

            blindString = ""
            FitType = ""
            # if self.bOnly and self.blind:
            #     blindString = " -t -1 " #--expectSignal 0 "   # b-only fit diagnostics
            #     FitType = "bOnly"
            if self.blind:
                blindString = " -t -1 " #--expectSignal 1 "   # s+b fit diagnostics
                FitType = "SplusB"

                command = "combine -M GenerateOnly -d {datacard} -m {mH} -n .{name} --saveToys --setParameters r=1 ".format(datacard=datacard.replace(".txt",".root"), mH=current_mass, name = OutNameAppend+"_"+FitType)
                command += blindString
                RunCommand(command, self.dry_run)

            command = "combineTool.py -M FastScan -w {datacard}:w ".format(datacard=datacard.replace(".txt",".root"))
            if self.blind:
                command += " -d higgsCombine.{name}.GenerateOnly.mH{mH}.123456.root:toys/toy_asimov".format(mH=current_mass, name = OutNameAppend+"_"+FitType)

            additionalArguments = " "
            # additionalArguments = " --robustHesse 1"
            # additionalArguments = " --cminFallbackAlgo Minuit,1:10 --setRobustFitStrategy 2"
            command += additionalArguments
            RunCommand(command, self.dry_run)

        os.chdir(cwd)

    def run_parallel(self, current_mass):
        border_msg("Running step {step} for mass {current_mass}, year: {year}".format(step=self.step, current_mass=current_mass, year = self.year))
        actions = {
            "cc": self.combine_cards,
            "rc": self.run_combine,
            "ri": self.run_impact,
            "rll": self.run_LHS,
            "correlation": self.run_correlation,
            "fitdiagnostics": self.FitDiagnostics,
            "fastscan": self.fastScan,
            "plot": None  # Placeholder for when no function is needed
        }

        current_mass_directory = os.path.join(self.dir_name, 'HCG', str(current_mass))
        cwd = os.getcwd()   # Get present working directory

        logger.debug("Running step {step} for mass {current_mass} in directory {current_mass_directory}".format(step=self.step, current_mass=current_mass, current_mass_directory= current_mass_directory))

        if self.step.lower() == "all":
            actions["cc"](current_mass, current_mass_directory, cwd)
            actions["rc"](current_mass, current_mass_directory, cwd)
            #actions["ri"](current_mass, current_mass_directory, cwd)
            #actions["fitdiagnostics"](current_mass, current_mass_directory, cwd)
        else:
            action = actions.get(self.step.lower())
            if action is not None: # FIXME: Need to add condition that when the year is `run2` then for combining cards we need to use `run2` function instead of `cc`
                action(current_mass, current_mass_directory, cwd)

    def Run(self):
        logger.debug("Current working directory: %s", os.getcwd())

        # STEP - 1: For Datacard and workspace creation step load datacard class
        if (self.step).lower() in ('dc'): # or (self.step).lower() == 'all': # Fixme: all year is not working for 'dc'
            # get git diff patch and move it to each mass directory
            logger.debug("get git diff patch")
            RunCommand("git diff > git_diff.patch", self.dry_run)

            logger.debug("Declar datacardClass")
            datacard_class = datacardClass(str(self.year), self.verbose)

            logger.debug("load root module")
            datacard_class.loadIncludes()

            # Run the create_workspaces function as parallel for each mass point
            if self.ifParallel:
                # FIXME: This is not working
                logger.error("Parallel is not working for datacard creation step")
                exit(1)
                # create_workspaces takes two arguments, mass and datacard_class
                pool = mp.Pool()
                try:
                    pool.map(partial(self.create_workspaces, datacard_class=datacard_class), range(self.start_mass, self.end_val, self.step_sizes))
                except Exception as e:
                    logger.error(e)
                    pool.close()
                    pool.join()
                    exit(1)
            else:
                for current_mass in range(self.start_mass, self.end_val, self.step_sizes):
                    self.create_workspaces(current_mass, datacard_class)
                    RunCommand("mv git_diff.patch {}/".format(self.dir_name + '/HCG/' + str(current_mass)), self.dry_run)

            # exit the program after creating datacards and workspaces
            logger.debug("Exiting the program after creating datacards and workspaces")
            exit(0)

        if (self.step).lower() != 'plot' and (not self.ifParallel):
            for current_mass in range(self.start_mass, self.end_val, self.step_sizes):
                self.run_parallel(current_mass)

        if (self.step).lower() != 'plot' and self.ifParallel:
            pool = mp.Pool()
            try:
                pool.map(partial(run_parallel_instance, self), range(self.start_mass, self.end_val, self.step_sizes))
            finally:
                pool.close()
                pool.join()

        if (self.step).lower() == 'plot':
            if self.allDatacard:
                datacards = datacardList
            else:
                datacards = [self.DATA_CARD_FILENAME]

            logger.debug("Datacard: {}".format(datacards))
            for datacard in datacards:
                category = ((((datacard.replace("hzz2l2q_","")).replace("_13TeV","")).replace(".txt","")).replace("_xs","")).replace("13TeV","")
                SearchString4Datacard = CombineStrings.COMBINE_ASYMP_LIMIT.format(year = self.year, mH = "REPLACEMASS", blind = "blind" if self.blind else "", Category = category)
                logger.debug("SearchString4Datacard: {}".format(SearchString4Datacard))

                # Collect summary of limits in the json file
                command = 'combineTool.py -M CollectLimits {pathh}/HCG/*/higgsCombine.{name}.AsymptoticLimits.mH*.root --use-dirs -o {oPath}/limits_{name2}.json'.format(pathh = self.dir_name, name = SearchString4Datacard.replace("REPLACEMASS","*"), name2 = SearchString4Datacard.replace("mHREPLACEMASS","Summary"), oPath =  os.path.join(self.dir_name, 'figs'))
                # RunCommand(command, self.dry_run)

                # Plot the limits
                command = 'python plotLimitExpObs_2D.py {}  {}  {}  {} {} {} {} {} {}'.format(self.start_mass, self.end_val, self.step_sizes, self.year, self.blind, self.DATA_CARD_FILENAME, SearchString4Datacard, self.dir_name, self.frac_vbf)
                RunCommand(command, self.dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run combine for high mass Higgs search analysis")
    parser.add_argument('-i', '--input', dest='input_dir', type=str, default="", help='inputs directory')
    parser.add_argument('-d', '--is2D', dest='is_2d', type=int, default=1, help='is2D (default:1)')
    parser.add_argument('-mi', '--MassStartVal', dest='MassStartVal', type=int, default=500, help='MassStartVal (default:1)')
    parser.add_argument('-mf', '--MassEndVal', dest='MassEndVal', type=int, default=3001, help='MassEndVal (default:1)') # # scan mass end value is 3000, but I added 3001 to include 3000 in for loop. If I write 3000 then it will take last mass value as 2950.
    parser.add_argument('-ms', '--MassStepVal', dest='MassStepVal', type=int, default=50, help='MassStepVal (default:1)')
    parser.add_argument('-a', '--append', dest='append_name', type=str, default="", help='append name for cards dir')
    #parser.add_argument('-f', '--fracVBF', dest='frac_vbf', type=float, default=0.005, help='fracVBF (default:0.5%)')
    parser.add_argument('-f', '--fracVBF', dest='frac_vbf', type=float, default=-1, help='fracVBF, -1 means float this frac. (default:-1)')
    parser.add_argument("-y", "--year", dest="year", type=str, default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
    parser.add_argument("-c", "--ifCondor", action="store_true", dest="ifCondor", default=False, help="if you want to run combine command for all mass points parallel using condor make it 1")
    parser.add_argument("-b", "--blind", action="store_false", dest="blind", default=True, help="Running blind?")
    parser.add_argument("-allDatacard", "--allDatacard", action="store_true", dest="allDatacard", default=False, help="If we need limit values or impact plot for each datacards, stored in file ListOfDatacards.py")
    parser.add_argument("-bOnly", "--bOnly", action="store_true", dest="bOnly", default=False, help="If this option given then it will set --expectSignal 0, which means this is background only fit. By default it will always perform S+B limit/fit")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False, help="don't print status messages to stdout")
    # parser.add_argument("--log-level", help="Set the logging level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
    parser.add_argument(
        "--log-level",
        default=logging.WARNING,
        type=lambda x: getattr(logging, x.upper()),
        help="Configure the logging level."
        )
    parser.add_argument(
        "--log-level-roofit",
        default=ROOT.RooFit.WARNING,
        type=lambda x: getattr(ROOT.RooFit, x.upper()),
        help="Configure the logging level for RooFit."
        )
    parser.add_argument("--dry-run", action="store_true", help="Don't actually run the command, just print it.")
    parser.add_argument("-p", "--parallel", action="store_true", help="Run jobs parallelly")
    # parser.add_argument("-n", "--ncores", dest="ncores", type=int, default=8, help="number of cores to use")

    parser.add_argument("-date", "--date", dest="date", type=str, default='', help="date string") # This resets the date string to be added in the combine related input/output files
    parser.add_argument("-tag", "--tag", dest="tag", type=str, default='', help="tag string") # This appends additional string in the combine related input/output files
    parser.add_argument("-SanityCheckPlotUsingWorkspaces", "--SanityCheckPlotUsingWorkspaces", action="store_true", dest="SanityCheckPlotUsingWorkspaces", default=False, help="If this option given then it will plot the sanity check plots using workspaces") # This plots the mZZ plots for signal and background using workspaces

    subparsers = parser.add_subparsers(dest="step", help="Sub-commands for steps")

    # create the parser for the "step" command
    parser_step = subparsers.add_parser('step', help='step help')
    parser_step.add_argument('-s', '--step', dest='step', type=str, default='dc', help='Which step to run: dc (DataCardCreation), cc (CombineCards), rc (RunCombine), ri (run Impact), rll (run loglikelihood with and without syst) , fast (FastScan) or all')
    parser_step.add_argument('-ss', '--substep', dest='substep', type=int, default=1, help='sub-step help')

    args = parser.parse_args()

    # Get the full command line used to run the current Python script
    command_line = ' '.join(sys.argv)
    SaveInfoToTextFile("#"*75+'\n\n')
    SaveInfoToTextFile('python '+command_line+'\n\n')

    # Set the logging level based on the command line argument
    logger.setLevel(args.log_level)

    # # Set the global message level to WARNING
    ROOT.RooMsgService.instance().setGlobalKillBelow(args.log_level_roofit)

    DirectoryCreatorObj = DirectoryCreator(args.input_dir, args.is_2d, args.MassStartVal, args.MassEndVal, args.MassStepVal , args.append_name, args.frac_vbf, args.year, args.step,  args.substep, args.ifCondor, args.blind, args.verbose, args.allDatacard, args.bOnly, args.dry_run, args.parallel, args.SanityCheckPlotUsingWorkspaces)
    # DirectoryCreatorObj.validate()
    if args.year == '2016': years = [2016]
    if args.year == '2017': years = [2017]
    if args.year == '2018': years = [2018]
    # if (args.year).lower() == 'all': years = [ 2016, 2017, 2018]
    if (args.year).lower() == 'all': years = [ 2016, 2017, 2018, "run2"]
    if (args.year).lower() == 'run2': years = ["run2"]
    if (args.year).lower() == 'run2':
        RunCommand("ulimit -s unlimited", args.dry_run)

    if (args.date).lower() != '' or (args.tag).lower() != '':
        CombineStrings.printAll()
        if (args.date).lower() != '':
            logger.debug("Setting date string to {}".format(args.date))
            CombineStrings.set_date(args.date)
        if (args.tag).lower() != '':
            logger.debug("Setting tag string to {}".format(args.tag))
            CombineStrings.set_tag( args.tag)
        CombineStrings.printAll()

    for year in years:
        if str(year).lower() == 'run2':
            RunCommand("ulimit -s unlimited", args.dry_run) # this is needed for run2 combination otherwise it will give segmentation fault. Not sure why.
        border_msg("Year = {}".format(year))
        DirectoryCreatorObj.SetYearRelatedStrings(year)
        DirectoryCreatorObj.SetDirName()
        DirectoryCreatorObj.Run()
