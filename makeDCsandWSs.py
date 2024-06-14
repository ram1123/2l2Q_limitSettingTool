"""
This script runs combine for high mass Higgs search analysis.
It uses argparse to handle command-line options and settings.
"""
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
import fnmatch

import ROOT


today = datetime.datetime.now()
date_string = today.strftime("%d%b").lower()
import common_strings_pars
CombineStrings = common_strings_pars.CombineStrings(date_string)


def run_parallel_instance(instance, current_mass):
    """Run the instance in parallel

    Args:
        instance (instance): instance
        current_mass (int): scalar mass value

    Returns:
        instance: instance
    """
    return instance.run_parallel(current_mass)

# Context manager for temporary directory change
class cd:
    """
    Context manager for changing the current working directory.
    ## Uses:
        # Use a context manager to change directories temporarily
        with cd(current_mass_directory):
            # Execute the command
            logger.info("Executing: {}".format(command))
            subprocess.run(command, shell=True)
    """
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

class DirectoryCreator:
    DATA_CARD_FILENAME = "hzz2l2q_13TeV_xs.txt"

    def __init__(self, args):
        self.input_dir = args.input_dir
        self.is_2d = args.is_2d
        self.append_name = args.append_name
        self.frac_vbf = args.frac_vbf
        self.year = args.year
        self.start_mass = args.MassStartVal
        self.step_sizes = args.MassStepVal
        self.end_val = args.MassEndVal
        self.subdir = ['HCG','figs']
        self.dir_name = 'datacards_HIG_23_001'
        self.channels = {'eeqq_Resolved', 'mumuqq_Resolved', 'eeqq_Merged', 'mumuqq_Merged'}
        self.cats = {'vbf_tagged','b_tagged','untagged'}
        self.ifNuisance = True
        self.Template = ["2D"]
        self.t_values = ['Resolved', 'Merged']
        self.date = args.date
        self.tag = args.tag
        self.step = args.step
        self.substep = args.substep
        self.ifCondor = args.ifCondor
        self.blind = args.blind
        self.howToBlind = args.howToBlind
        self.allDatacard = args.allDatacard
        self.signalStrength = args.signalStrength
        self.freezeParameters = args.freezeParameters
        self.setParameterRanges = args.setParameterRanges
        self.AdditionalFitOptions = args.AdditionalFitOptions
        self.verbose = args.verbose
        self.combineVerbose = args.combineVerbose
        self.dry_run = args.dry_run
        self.ifParallel = args.parallel
        self.SanityCheckPlotUsingWorkspaces = args.SanityCheckPlotUsingWorkspaces
        self.split_2016 = args.split2016


        self.CombineCondor = " --job-mode condor --sub-opts='+JobFlavour=\"{JobFlavour}\"{Additional}' --task-name {name}_{FitType}"

        self.blindString = ""
        self.FitType = ""
        if self.signalStrength == 0.0:
            self.FitType = "BkgOnlyHypothesis"
        elif self.signalStrength == 1.0:
            self.FitType = "SBHypothesis"
        else:
            self.FitType = "SBHypo_SStrength{}".format(self.signalStrength)

        if self.blind:
            self.blindString = " " + args.howToBlind + " "
            if args.howToBlind == "-t -1":
                self.blindString += " --expectSignal {} ".format(self.signalStrength)
            if args.step == 'ri' or args.step == 'riess':
                self.blindString = " -t -1 "
                if self.signalStrength != -1.0:
                    self.blindString += " --expectSignal {} ".format(self.signalStrength)
            if args.step == 'fs':
                self.blindString = " -t -1  "
        else:
            self.blindString = " "

        self.datacards = [self.DATA_CARD_FILENAME] if not self.allDatacard else datacardList

    def ResetBlindString(self):
        if self.blind:
            self.blindString = " " + self.howToBlind + " "
            if self.howToBlind == "-t -1":
                self.blindString += " --expectSignal {} ".format(self.signalStrength)
            if self.step == 'ri' or self.step == 'riess':
                self.blindString = " -t -1  --expectSignal {} ".format(self.signalStrength)
            if self.step == 'fs':
                self.blindString = " -t -1  "
        else:
            self.blindString = " "

        # if self.signalStrength == 0.0:
        #     self.FitType = "BkgOnlyHypothesis"
        # elif self.signalStrength == 1.0:
        #     self.FitType = "SBHypothesis"
        # else:
        #     self.FitType = "SBHypo_SStrength{}".format(self.signalStrength)

    def ResetTag(self):
        if (self.date).lower() != '' or (self.tag).lower() != '':
            CombineStrings.printAll()
            if (self.date).lower() != '':
                logger.debug("Setting date string to {}".format(self.date))
                CombineStrings.set_date(self.date)
            if (self.tag).lower() != '':
                logger.debug("Setting tag string to {}".format(self.tag))
                CombineStrings.set_tag_impact( self.tag)
            CombineStrings.printAll()

    def GetCategory(self, datacard):
        return ((((datacard.replace("hzz2l2q_","")).replace("_13TeV","")).replace(".txt","")).replace("_xs","")).replace("13TeV","")

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

    def run_text2workspace(self, current_mass, current_mass_directory, datacard):
        logger.info("Inside run_text2workspace member function")
        logger.debug("Current directory: {}".format(os.getcwd()))
        with cd(current_mass_directory):
            logger.debug("Current directory: {}".format(os.getcwd()))
            if os.path.exists(datacard.replace(".txt", ".root")):
                logger.warning("Removing existing workspace: {}".format(datacard.replace(".txt", ".root")))
                os.remove(datacard.replace(".txt", ".root"))

            # Create the workspace
            command = "text2workspace.py {datacard}.txt  -m {mH} -o {datacard}.root".format( datacard = datacard.replace(".txt", ""), mH = current_mass)
            RunCommand(command, self.dry_run)
        logger.debug("Current directory: {}".format(os.getcwd()))

    def get_text2workspace(self, current_mass, current_mass_directory, cwd):
        """For each datacard, create a workspace using text2workspace.py

        Args:
            current_mass (int): scalar mass value
            current_mass_directory (str): directory where the datacards are stored
            cwd (str): current working directory
        """
        logger.debug("Current mass: {}".format(current_mass))
        logger.debug("Current mass directory: {}".format(current_mass_directory))
        logger.debug("Current working directory: {}".format(cwd))

        logger.debug("Current directory: {}".format(os.getcwd()))

        for datacard in self.datacards:
            self.run_text2workspace(current_mass, current_mass_directory, datacard)

        logger.debug("Current directory: {}".format(os.getcwd()))

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
        yearlists  = ['2016', '2017', '2018'] if not self.split_2016 else ['2016preAPV', '2016postAPV','2017', '2018']
        for year in yearlists:
            # AllCardsCombination = AllCardsCombination +' Era{year}=../../../{cards_{year}{additionalString}}/HCG/{mH}/{datacard}'.format(mH = current_mass, year = year, datacard = self.DATA_CARD_FILENAME, additionalString = "" if self.append_name == "" else "_"+self.append_name)
            AllCardsCombination = AllCardsCombination +' Era{year}=../../../{Run2_Cards}/HCG/{mH}/{datacard}'.format(mH = current_mass, year = year, datacard = self.DATA_CARD_FILENAME, additionalString = "" if self.append_name == "" else "_"+self.append_name, Run2_Cards = (self.dir_name).replace("datacards_HIG_23_001/","").replace("run2",year))
        AllCardsCombination = AllCardsCombination +' > {datacard}'.format(datacard = "hzz2l2q_13TeV_xs_NoNuisance.txt")
        AllCardsCombination = AllCardsCombination +' > hzz2l2q_13TeV_xs_NoNuisance.txt'
        AllCardsWithNuisance = (AllCardsCombination.replace('-s','  ')).replace('_NoNuisance','')

        RunCommand(AllCardsCombination, self.dry_run)
        RunCommand(AllCardsWithNuisance, self.dry_run)
        os.chdir(cwd)


    def run_combine(self, current_mass, current_mass_directory, cwd):
        """
        STEP - 3: run Combine commands
        Runs the combine utility for the given mass and conditions.
        """
        logger.debug("Datacard: {}".format(self.datacards))

        for datacard in self.datacards:
            AppendNameString = CombineStrings.COMBINE_ASYMP_LIMIT.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = self.GetCategory(datacard), bOnlyOrSB = self.FitType)

            # -M HybridNew --LHCmode LHC-limits
            CombineCommonArguments = ' -M AsymptoticLimits -d {datacard} -m {mH}   -n .{name} '.format(mH = current_mass, datacard = datacard, name = AppendNameString)
            CombineCommonArgumentsHybrid = ' -M HybridNew --LHCmode LHC-limits -d {datacard} -m {mH}   -n .{name}Hybrid '.format(mH = current_mass, datacard = datacard, name = AppendNameString)
            #CombineCommonArguments += ' --rMin -1 --rMax 2 --rAbsAcc 0 --rRelAcc 0.0005 '
            CombineCommonArguments += ' --rMin 0 --rMax 2 --rAbsAcc 0 --rRelAcc 0.0005 '

            # Add the blind option
            CombineCommonArguments += self.blindString
            CombineCommonArgumentsHybrid += self.blindString
            if self.combineVerbose != 0:
                CombineCommonArguments += " -v {}".format(self.combineVerbose)
                CombineCommonArgumentsHybrid += " -v {}".format(self.combineVerbose)
            #     CombineCommonArgumentsHybrid += "    " + self.blindString
                # CombineCommonArguments += " --run expected "
                # CombineCommonArguments += " --run blind -t -1 "
                # CombineCommonArguments += " --run blind -t -1 --expectSignal 1 "

            Stat = " "
            if self.setParameterRanges != "":
                Stat += " --setParameterRanges {}".format(self.setParameterRanges)
            if self.AdditionalFitOptions != "":
                Stat += " {}".format(self.AdditionalFitOptions)
            CombineCommonArguments += Stat
            CombineCommonArgumentsHybrid += Stat

            # freeze the nuisance JES and JER
            freeze = " "
            if self.freezeParameters != "":
                freeze += " --freezeParameters {}".format(self.freezeParameters)
            CombineCommonArguments += freeze
            CombineCommonArgumentsHybrid += freeze

            if self.ifCondor:
                LocalDir = os.getcwd()
                os.chdir(current_mass_directory)
                command = "combineTool.py " + CombineCommonArguments
                commandHybrid = "combineTool.py " + CombineCommonArgumentsHybrid

                Condor_queue = datacardList_condor[datacard] # Get the condor queue from the dictionary datacardList_condor defined in the file ListOfDatacards.py
                if self.year == 'run2':
                    command += self.CombineCondor.format(name = AppendNameString+"_AsympLimit", FitType = self.FitType, JobFlavour = "workday", Additional = "\\nRequestCpus=4\\nrequest_memory = 10000")
                else:
                    command += self.CombineCondor.format(name = AppendNameString+"_AsympLimit", FitType = self.FitType, JobFlavour = Condor_queue, Additional = "")
                commandHybrid += self.CombineCondor.format(name = AppendNameString+"_Hybrid", FitType = self.FitType, JobFlavour = "tomorrow", Additional = "")
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

    def run_impact_expSS(self, current_mass, current_mass_directory, cwd):
        """This member function will first grab the expected upper limit from the combine output.
         Then set the signalStrength value to the expected limit then run the impact plot

        Args:
            current_mass (str): Mass of scalar over which its going to run
            current_mass_directory (str): path where it will find input datacards and place output information
            cwd (str): current working directory
        """
        # Get the expected upper limit from the combine output

        logger.debug("Datacard: {}".format(self.datacards))
        expUL = 0.0
        TempSignalStrength = self.signalStrength
        with cd(current_mass_directory):
            logger.debug("Current directory: {}".format(os.getcwd()))
            for datacard in self.datacards:
                AppendNameString = CombineStrings.COMBINE_ASYMP_LIMIT.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = self.GetCategory(datacard), bOnlyOrSB = self.FitType)
                # Get the expected upper limit from the combine output (its format is "mH500_run2_03sep_blind_BkgOnlyHypothesis__AsympLimit_BkgOnlyHypothesis.6008612.0.out")
                # self.CombineCondor = " --job-mode condor --sub-opts='+JobFlavour=\"{JobFlavour}\"{Additional}' --task-name {name}_{FitType}"
                #
                logger.debug("Opening file: {}".format("{name}*.out".format(name = AppendNameString+"_AsympLimit")))

                # List all files with the name {name}*.out in current directory. Pick the one with the latest creation time
                matching_files = []
                for filename in os.listdir("."):
                    if fnmatch.fnmatch(filename, "{name}*.out".format(name = AppendNameString+"_AsympLimit")):
                        filepath = os.path.join(".", filename)
                        creation_time = os.path.getctime(filepath)
                        matching_files.append((filename, creation_time))

                # Sort the files by creation time in descending order
                sorted_files = sorted(matching_files, key=lambda x: x[1], reverse=True)

                # Pick the latest file if there is at least one
                if sorted_files:
                    latest_file = sorted_files[0][0]
                    logger.debug("The most recently created file is {}".format(latest_file))
                else:
                    logger.error("No matching files found.")
                    sys.exit(1)

                with open(latest_file, 'r') as f:
                    for line in f:
                        if "Expected 50.0%: r <" in line:
                            expUL = float(line.split("Expected 50.0%: r <")[1].split(" ")[1])
                            logger.info("Expected upper limit: {}".format(expUL))
                            break
        # Update the signal strength value
        self.signalStrength = expUL
        self.ResetBlindString()
        self.tag = "expUL"
        self.ResetTag()
        # Run the impact plot
        self.run_impact(current_mass, current_mass_directory, cwd)

    def run_impact(self, current_mass, current_mass_directory, cwd):
        logger.debug('datacards: {}'.format(self.datacards))
        with cd(current_mass_directory):
            countDatacards = 1
            for datacard in self.datacards:
                logger.debug("===> Submitting {}/{}".format(countDatacards, len(self.datacards)))
                AppendOutName = CombineStrings.COMBINE_IMPACT.format(
                    year = self.year, mH = current_mass,
                    blind = "blind" if self.blind else "",
                    Category = self.GetCategory(datacard),
                    bOnlyOrSB = self.FitType
                    )

                # STEP 1: Check if .root file exists; if not, create it
                if not os.path.exists(datacard.replace(".txt", ".root")):
                    command = "text2workspace.py {datacard}.txt  -m {mH} -o {datacard}.root".format( datacard = datacard.replace(".txt", ""), mH = current_mass)
                    RunCommand(command, self.dry_run)

                Stat = " "
                Stat += " --setRobustFitStrategy 2 "
                Stat +=  " --cminFallbackAlgo Minuit,1:10 " # Added this line as fits were failing
                Stat += " --cminDefaultMinimizerTolerance 0.01  --setRobustFitTolerance 0.01 " # Added this line as fits were failing for some cases

                # (BR,BTAG_merged,CMS_Vtagging,CMS_Vtagging_In,CMS_channel,CMS_eff_e,CMS_eff_e_In,CMS_eff_m,CMS_eff_m_In,CMS_scale_J_Abs,CMS_scale_J_Abs_2018,CMS_scale_J_Abs_2018_In,CMS_scale_J_Abs_In,CMS_scale_J_BBEC1,CMS_scale_J_BBEC1_2018,CMS_scale_J_BBEC1_2018_In,CMS_scale_J_BBEC1_In,CMS_scale_J_EC2,CMS_scale_J_EC2_2018,CMS_scale_J_EC2_2018_In,CMS_scale_J_EC2_In,CMS_scale_J_FlavQCD,CMS_scale_J_FlavQCD_In,CMS_scale_J_HF,CMS_scale_J_HF_2018,CMS_scale_J_HF_2018_In,CMS_scale_J_HF_In,CMS_scale_J_RelBal,CMS_scale_J_RelBal_In,CMS_scale_J_RelSample_2018,CMS_scale_J_RelSample_2018_In,CMS_zz2l2q_bkgMELA_merged,CMS_zz2l2q_bkgMELA_merged_In,CMS_zz2l2q_mean_e_sig,CMS_zz2l2q_mean_e_sig_In,CMS_zz2l2q_mean_m_sig,CMS_zz2l2q_mean_m_sig_In,CMS_zz2l2q_sigMELA_merged,CMS_zz2l2q_sigMELA_merged_In,CMS_zz2l2q_sigma_e_sig,CMS_zz2l2q_sigma_e_sig_In,CMS_zz2l2q_sigma_m_sig,CMS_zz2l2q_sigma_m_sig_In,CMS_zz2lJ_mean_J_sig,CMS_zz2lJ_mean_J_sig_In,CMS_zz2lJ_sigma_J_sig,CMS_zz2lJ_sigma_J_sig_In,Dspin0,LUMI_13_2018,MH,QCDscale_vz,QCDscale_vz_In,a1_VBF_eeqq_Merged_2018,a1_VBF_mumuqq_Merged_2018,a1_ggH_eeqq_Merged_2018,a1_ggH_mumuqq_Merged_2018,a2_VBF_eeqq_Merged_2018,a2_VBF_mumuqq_Merged_2018,a2_ggH_eeqq_Merged_2018,a2_ggH_mumuqq_Merged_2018,bias_VBF_eeqq_Merged,bias_VBF_mumuqq_Merged,bias_ggH_eeqq_Merged,bias_ggH_mumuqq_Merged,frac_VBF,lumi_13TeV_2018,lumi_13TeV_2018_In,lumi_13TeV_correlated_16_17_18,       lumi_13TeV_correlated_16_17_18_In,lumi_13TeV_correlated_17_18,lumi_13TeV_correlated_17_18_In,mean_J_err,mean_e_err,mean_m_err,n1_VBF_eeqq_Merged_2018,n1_VBF_mumuqq_Merged_2018,n1_ggH_eeqq_Merged_2018,n1_ggH_mumuqq_Merged_2018,n2_VBF_eeqq_Merged_2018,n2_VBF_mumuqq_Merged_2018,n2_ggH_eeqq_Merged_2018,n2_ggH_mumuqq_Merged_2018,pdf_hzz2l2q_accept,pdf_hzz2l2q_accept_In,pdf_qqbar,pdf_qqbar_In,r,sigma_J_err,sigma_VBF_eeqq_Merged,sigma_VBF_mumuqq_Merged,sigma_e_err,sigma_ggH_eeqq_Merged,sigma_ggH_mumuqq_Merged,sigma_m_err,zjetsAlpha_merged_btagged,zjetsAlpha_merged_btagged_In,zjetsAlpha_merged_untagged,zjetsAlpha_merged_untagged_In,zjetsAlpha_merged_vbftagged,zjetsAlpha_merged_vbftagged_In,zz2lJ_mass)

                Stat += " --setParameterRanges r=-1,3 "
                # Stat += " --setParameterRanges r=-1,2:frac_VBF=0,1:CMS_zz2l2q_bkgMELA_merged=0,1:CMS_zz2l2q_sigMELA_merged=0,1:CMS_zz2l2q_mean_e_sig=0,1:CMS_zz2l2q_mean_m_sig=0,1:CMS_zz2l2q_sigma_e_sig=0,1:CMS_zz2l2q_sigma_m_sig=0,1 "

                Stat = " "
                if self.setParameterRanges != "":
                    Stat += " --setParameterRanges {}".format(self.setParameterRanges)

                if self.AdditionalFitOptions != "":
                    Stat += " {}".format(self.AdditionalFitOptions)

                # Stat += " --setParameters r=0"
                # freeze the nuisance JES and JER
                freeze = " "
                if self.freezeParameters != "":
                    freeze += " --freezeParameters {}".format(self.freezeParameters)
                # freeze +=  " --freezeNuisanceGroups check "  # To freese the nuisance group named check
                # freeze += " --freezeParameters frac_VBF "
                # freeze += " --freezeParameters allConstrainedNuisances "
                # freeze = " "

                if self.substep == 1:
                    # STEP - 1
                    command = "combineTool.py -M Impacts -d {datacard}  -m {mH} -n .{name}  --robustFit 1 --doInitialFit ".format(datacard = datacard.replace(".txt", ".root"), mH = current_mass, name = AppendOutName)   # Main command
                    #command = "combineTool.py -M Impacts -d {datacard}  -m {mH} --rMin -10  --doInitialFit -v 3 ".format(datacard = datacard.replace(".txt", ".root"), mH = current_mass)   # Main command
                    command += self.blindString
                    if self.combineVerbose != 0:
                        command += " -v {}".format(self.combineVerbose)
                    command += Stat
                    command += freeze

                    if self.ifCondor:
                        Condor_queue = datacardList_condor[datacard] # Get the condor queue from the dictionary datacardList_condor defined in the file ListOfDatacards.py
                        if self.year == 'run2':
                            command += self.CombineCondor.format(name = AppendOutName+"_ImpactS1", FitType = self.FitType, JobFlavour = "workday", Additional = "\\nRequestCpus=4\\nrequest_memory = 10000")
                        else:
                            command += self.CombineCondor.format(name = AppendOutName+"_ImpactS1", FitType = self.FitType, JobFlavour = Condor_queue, Additional = "")
                    else:
                        command +=  " | tee {name}.log".format(name = AppendOutName)

                    RunCommand(command, self.dry_run)

                if self.substep == 2:
                    # STEP - 2
                    command = "combineTool.py -M Impacts -d {datacard}  -m {mH}  -n .{name} --robustFit 1 --doFits ".format(datacard = datacard.replace(".txt", ".root"), mH = current_mass, name = AppendOutName)
                    #if self.blind: command += " -t -1 --expectSignal 1 "
                    command += self.blindString
                    command += Stat
                    command += freeze

                    if self.ifCondor:
                        Condor_queue = datacardList_condor[datacard] # Get the condor queue from the dictionary datacardList_condor defined in the file ListOfDatacards.py
                        if self.year == 'run2':
                            command += self.CombineCondor.format(name = AppendOutName+"_ImpactS2", FitType = self.FitType, JobFlavour = "workday", Additional = "\\nRequestCpus=4\\nrequest_memory = 10000")
                        else:
                            command += self.CombineCondor.format(name = AppendOutName+"_ImpactS2", FitType = self.FitType, JobFlavour = Condor_queue, Additional = "")
                    else:
                        # use multi core processing to run impact plot
                        command += " --parallel 8 "


                    RunCommand(command, self.dry_run)

                if self.substep == 3:
                    # STEP - 3
                    command = "combineTool.py -M Impacts -d {datacard} -m {mH}  -n .{name}   --robustFit 1   --output impacts_{name}.json".format(datacard = datacard.replace(".txt", ".root"), mH = current_mass, name = AppendOutName)
                    command += Stat
                    command += freeze

                    RunCommand(command, self.dry_run)

                    # STEP - 4
                    # create a directory named "impacts" inside figs directory to keep impact plots
                    make_directory('{pathh}/impacts'.format(pathh =  '../../figs'))
                    command = "plotImpacts.py -i impacts_{name}.json -o {pathh}/impacts/impacts_{name} ".format(pathh =  '../../figs', name = AppendOutName) # --blind
                    RunCommand(command, self.dry_run)
                countDatacards += 1

    def run_LHS(self, current_mass, current_mass_directory, cwd): # Commands taken From Ankita

        logger.debug('datacard: {}'.format(self.DATA_CARD_FILENAME))

        os.chdir(current_mass_directory)

        for datacard in self.datacards:
            # if datacard.root file exists, then skip this step
            if not os.path.exists(datacard.replace(".txt", ".root")):
                command = "text2workspace.py {datacard}.txt  -m {mH} -o {datacard}.root".format( datacard = datacard.replace(".txt", ""), mH = current_mass)
                RunCommand(command, self.dry_run)

            OutNameAppend = CombineStrings.COMBINE_FITDIAGNOSTIC.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = self.GetCategory(datacard))

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

                CustomString = CombineStrings.COMBINE_IMPACT.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = self.GetCategory(datacard), bOnlyOrSB = self.FitType)

                CondorCommandPatch = " -v -1 " + self.CombineCondor.format(name = CustomString+"_LHS", FitType = self.FitType, JobFlavour = "tomorrow", Additional = "\\nRequestCpus=4\\nrequest_memory = 10000")

                if self.substep == 1:
                    # STEP - 1
                    command = " -M MultiDimFit --algo grid --points {pointsToScan} --rMin -3 --rMax 3 -d {datacard} -m {mH} -n .{name} --saveWorkspace {blindString}  ".format(pointsToScan = pointsToScan, datacard = datacard.replace(".txt",".root"), mH = current_mass, blindString = self.blindString, name = name)
                    # while running on condor, switch the verbosity level to -1 (very quite)
                    if self.ifCondor:
                        command = "combineTool.py " + command + CondorCommandPatch+"Step1"
                    else:
                        command = "combine " + command
                    RunCommand(command + " | tee LHS_Float.log", self.dry_run)

                if self.substep == 2:
                    # STEP - 2
                    command = " -M MultiDimFit --algo none --rMin -3 --rMax 3 -d {datacard} -m {mH} -n .{name} --saveWorkspace {blindString} ".format(datacard = datacard.replace(".txt",".root"), mH = current_mass, blindString = self.blindString, name = name2) # FIXME: name
                    # while running on condor, switch the verbosity level to -1 (very quite)
                    if self.ifCondor:
                        command = "combineTool.py " + command + CondorCommandPatch+"Step2"
                    else:
                        command = "combine " + command
                    RunCommand(command + " | tee LHS_AllConstrained.log", self.dry_run)

                    # STEP - 3
                    command = " -M MultiDimFit higgsCombine.{name}.MultiDimFit.mH{mH}.root -m {mH} --freezeParameters allConstrainedNuisances -n .{name3} --rMin -3 --rMax 3 --snapshotName MultiDimFit {blindString} --algo grid --points {pointsToScan} ".format(name = name, name3 = name3, mH = current_mass, blindString = self.blindString, pointsToScan = pointsToScan)
                    if self.ifCondor:
                        command = "combineTool.py " + command + CondorCommandPatch+"Step3"
                    else:
                        command = "combine " + command
                    RunCommand(command + " | tee LHS_plot.log", self.dry_run)

                if self.substep == 3:
                    # STEP - 4
                    command = "plot1DScan.py higgsCombine.{name}.MultiDimFit.mH{mH}.root --main-label \"With systematics\" --main-color 1 --others higgsCombine.{name3}.MultiDimFit.mH{mH}.root:\"Stat-only\":2 -o {outPDFName} --breakdown syst,stat".format(datacard=datacard.replace(".txt",".root"), mH=current_mass, pointsToScan = pointsToScan, name = name, name3 = name3, outPDFName = '../../figs/'+outPDFName)
                    RunCommand(command + " | tee LHS_plot.log", self.dry_run)

                ############################################
                #       Version 2 of LHS: https://twiki.cern.ch/twiki/bin/view/Sandbox/TestTopic11111180#Likelihood_scan
                ############################################
                if self.substep == 21:
                    # # STEP - 1: Inclusive likelihood scan with syst and stats:
                    # combineTool.py -M MultiDimFit --algo grid --points 100 --rMin 0 --rMax 3 ttHmultilep_WS.root --alignEdges 1 --floatOtherPOIs=1 -P r_ttH -n .likelihoodscan --saveWorkspace
                    command = "combineTool.py -M MultiDimFit --algo grid --points {pointsToScan} --rMin 0 --rMax 3 {datacard} --alignEdges 1 --floatOtherPOIs=1  -n .likelihoodscan --saveWorkspace  -m {mH} ".format(pointsToScan = pointsToScan, datacard = datacard.replace(".txt",".root"), mH = current_mass)
                    if self.ifCondor:
                        command = "combineTool.py " + command + CondorCommandPatch+"Step21"
                    else:
                        command = "combine " + command
                    RunCommand(command + " ", self.dry_run)

                if self.substep == 22:
                    # # STEP - 2: Plot inclusive likelihood scan:
                    # plot1DScan.py all.root  --y-cut 50 --y-max 50
                    command = "plot1DScan.py higgsCombine.likelihoodscan.MultiDimFit.mH125.root  --y-cut 50 --y-max 50"
                    RunCommand(command + " ", self.dry_run)

                if self.substep == 23:
                    # # STEP - 3: Get statistical only component:
                    # combine -M MultiDimFit higgsCombine.likelihoodscan.MultiDimFit.mH125.root -n .likelihoodscan.freezeAll -m 125 --rMin 0 --rMax 3  --algo grid --points 30 --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit --alignEdges 1 --floatOtherPOIs=1 -P r_ttH
                    command = "combine -M MultiDimFit higgsCombine.likelihoodscan.MultiDimFit.mH{mH}.root -n .likelihoodscan.freezeAll -m {mH} --rMin 0 --rMax 3  --algo grid --points {pointsToScan} --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit --alignEdges 1 ".format(pointsToScan = pointsToScan, mH = current_mass)
                    if self.ifCondor:
                        command = "combineTool.py " + command + CondorCommandPatch+"Step23"
                    else:
                        command = "combine " + command
                    RunCommand(command + " ", self.dry_run)

                if self.substep == 24:
                    # # STEP - 4: Plot breakdown stat and syst:
                    # plot1DScan.py higgsCombine.likelihoodscan.MultiDimFit.mH125.root --POI r_ttH --y-cut 50 --y-max 50 --breakdown syst,stat --others "higgsCombine.likelihoodscan.freezeAll.MultiDimFit.mH125.root:Stat only:2"
                    command = "plot1DScan.py higgsCombine.likelihoodscan.MultiDimFit.mH125.root --y-cut 50 --y-max 50 --breakdown syst,stat --others \"higgsCombine.likelihoodscan.freezeAll.MultiDimFit.mH{mH}.root:Stat only:2\"".format(mH = current_mass)
                    RunCommand(command + " ", self.dry_run)

                # # From Chenguang:
                # if self.substep == 31:
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

        OutNameAppend = CombineStrings.COMBINE_FITDIAGNOSTIC.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = self.GetCategory(datacard))

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

            command = "combine -M MultiDimFit -d {datacard} -m {mH} --freezeParameters MH -n .{name} --setParameterRanges r={rRange} --saveWorkspace  {blindString}".format(datacard=self.DATA_CARD_FILENAME.replace(".txt",".root"), mH=current_mass, blindString = self.blindString, rRange = rRange, name = name)
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
            ExpectedSignal = 0
            rRange= "-2,2" # for ExpectedSignal = 1
            command = "combine -M MultiDimFit {datacard} -m {mH} --freezeParameters MH -n .correlation --cminDefaultMinimizerStrategy 0  --robustHesse 1 --robustHesseSave 1 --saveFitResult  -t -1 --expectSignal  {ExpectedSignal} ".format(datacard=self.DATA_CARD_FILENAME.replace(".txt",".root"), mH=current_mass, ExpectedSignal = ExpectedSignal)
            RunCommand(command, self.dry_run)


        os.chdir(cwd)

    def FitDiagnostics(self, current_mass, current_mass_directory, cwd):
        """ Information:
        Simple fits
        """

        logger.debug('self.datacards: {}'.format(self.datacards))
        os.chdir(current_mass_directory)
        rRange= "-2,2" # for ExpectedSignal = 1
        for datacard in self.datacards:
            OutNameAppend = CombineStrings.COMBINE_FITDIAGNOSTIC.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = self.GetCategory(datacard), bOnlyOrSB = self.FitType)

            blindString = ""
            FitType = ""

            # if pre- and post-fit plots are needed use additional options `--plots --saveShapes` and `--saveWithUncertainties` respectively
            blindString = " -t -1 --expectSignal 0 "   # b-only fit diagnostics
            FitType = "BkgOnlyHypothesis"
            command = "combineTool.py -M FitDiagnostics  -m {mH}  -d {datacard} --rMin -10   -n .{name}".format(datacard=datacard, mH=current_mass, name = OutNameAppend+"_"+FitType)
            command += blindString
            # command += " --plots  --saveNLL --saveNormalizations --savePredictionsPerToy --saveWithUncertainties  --saveShapes --saveOverallShapes --ignoreCovWarning"

            # always run the FitDiagnostics using condor
            command += self.CombineCondor.format(name = OutNameAppend+"_FitDiagnostics", FitType = FitType, JobFlavour = "tomorrow", Additional = "")
            RunCommand(command, self.dry_run)

            blindString = " -t -1 --expectSignal 1 "   # s+b fit diagnostics
            FitType = "SBHypothesis"
            command = "combineTool.py -M FitDiagnostics  -m {mH}  -d {datacard} --rMin -10   -n .{name}".format(datacard=datacard, mH=current_mass, name = OutNameAppend+"_"+FitType)
            command += blindString
            # command += " --plots  --saveNLL --saveNormalizations --savePredictionsPerToy --saveWithUncertainties  --saveShapes --saveOverallShapes --ignoreCovWarning"

            # always run the FitDiagnostics using condor
            command += self.CombineCondor.format(name = OutNameAppend+"_FitDiagnostics", FitType = FitType, JobFlavour = "tomorrow", Additional = "")
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

        logger.debug('self.datacards: {}'.format(self.datacards))
        os.chdir(current_mass_directory)
        rRange= "-2,2" # for ExpectedSignal = 1
        for datacard in self.datacards:
            OutNameAppend = CombineStrings.COMBINE_FITDIAGNOSTIC.format(year = self.year, mH = current_mass, blind = "blind" if self.blind else "", Category = self.GetCategory(datacard), bOnlyOrSB = self.FitType)

            if not os.path.exists(datacard.replace(".txt", ".root")):
                logger.debug("Creating workspace for datacard: {}".format(datacard))
                command = "text2workspace.py {datacard}.txt  -m {mH} -o {datacard}.root".format( datacard = datacard.replace(".txt", ""), mH = current_mass)
                RunCommand(command, self.dry_run)

            if self.blind:
                command = "combine -M GenerateOnly -d {datacard} -m {mH} -n .{name} --saveToys  --setParameters r=1 --setParameterRanges r=-5,5 ".format(datacard=datacard.replace(".txt",".root"), mH=current_mass, name = OutNameAppend+"_"+self.FitType)
                command += self.blindString
                RunCommand(command, self.dry_run)

            command = "combineTool.py -M FastScan -w {datacard}:w ".format(datacard=datacard.replace(".txt",".root"))
            if self.blind:
                command += " -d higgsCombine.{name}.GenerateOnly.mH{mH}.123456.root:toys/toy_asimov -o ../../figs/fastScan_{name} ".format(mH=current_mass, name = OutNameAppend+"_"+self.FitType)

            command += " --parallel 8 "

            if self.blind: command += "  --setParameters r=1 "

            Stat = " "
            if self.setParameterRanges != "":
                Stat += " --setParameterRanges {}".format(self.setParameterRanges)
            if self.AdditionalFitOptions != "":
                Stat += " {}".format(self.AdditionalFitOptions)

            command += Stat

            # freeze the nuisance JES and JER
            freeze = " "
            if self.freezeParameters != "":
                freeze += " --freezeParameters {}".format(self.freezeParameters)
            command += freeze

            if self.ifCondor:
                command += self.CombineCondor.format(name = OutNameAppend+"_FastScan", FitType = self.FitType, JobFlavour = "tomorrow", Additional = "")
            # additionalArguments = "   "
            # additionalArguments = " --robustHesse 1"
            # additionalArguments = " --cminFallbackAlgo Minuit,1:10 --setRobustFitStrategy 2"

            # additionalArguments += " --setParameters r=1 --setParameterRanges r=0,10 "

            # fitting options
            # additionalArguments += " --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.01 --setRobustFitTolerance 0.01 "

            # additionalArguments += " --cminFallbackAlgo Minuit,1:10 --setRobustFitStrategy 2"

            RunCommand(command, self.dry_run)

        os.chdir(cwd)

    def run_parallel(self, current_mass):
        border_msg("Running step {step} for mass {current_mass}, year: {year}".format(step=self.step, current_mass=current_mass, year = self.year))
        actions = {
            "cc": self.combine_cards,
            "ws": self.get_text2workspace,
            "rc": self.run_combine,
            "fd": self.FitDiagnostics,
            "ri": self.run_impact,
            "riess": self.run_impact_expSS,
            "fs": self.fastScan,
            "rll": self.run_LHS,
            "corr": self.run_correlation,
            "plot": None  # Placeholder for when no function is needed
        }

        current_mass_directory = os.path.join(self.dir_name, 'HCG', str(current_mass))
        cwd = os.getcwd()   # Get present working directory

        logger.debug("Running step {step} for mass {current_mass} in directory {current_mass_directory}".format(step=self.step, current_mass=current_mass, current_mass_directory= current_mass_directory))

        if self.step.lower() == "all":
            actions["cc"](current_mass, current_mass_directory, cwd)
            # actions["ws"](current_mass, current_mass_directory, cwd)
            actions["rc"](current_mass, current_mass_directory, cwd)
            # actions["ri"](current_mass, current_mass_directory, cwd)
            #actions["fitdiagnostics"](current_mass, current_mass_directory, cwd)
        else:
            action = actions.get(self.step.lower())
            if action is not None: # FIXME: Need to add condition that when the year is `run2` then for combining cards we need to use `run2` function instead of `cc`
                action(current_mass, current_mass_directory, cwd)

    def run_step_dc(self):
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
                #  create_workspace memeber function takes two arguments mass and datacard_class
                # pool.map(partial(self.create_workspaces, datacard_class), range(self.start_mass, self.end_val, self.step_sizes))
                arguments = [(current_mass, datacard_class) for current_mass in range(self.start_mass, self.end_val, self.step_sizes)]
                pool.starmap(self.create_workspaces, arguments)
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

    def run_step_plot(self):
        logger.debug("Datacard: {}".format(self.datacards))

        for datacard in self.datacards:
            SearchString4Datacard = CombineStrings.COMBINE_ASYMP_LIMIT.format(year = self.year, mH = "REPLACEMASS", blind = "blind" if self.blind else "", Category = self.GetCategory(datacard), bOnlyOrSB = self.FitType)
            logger.debug("SearchString4Datacard: {}".format(SearchString4Datacard))

            # Collect summary of limits in the json file
            command = 'combineTool.py -M CollectLimits {pathh}/HCG/*/higgsCombine.{name}.AsymptoticLimits.mH*.root --use-dirs -o {oPath}/limits_{name2}.json'.format(pathh = self.dir_name, name = SearchString4Datacard.replace("REPLACEMASS","*"), name2 = SearchString4Datacard.replace("mHREPLACEMASS","Summary"), oPath =  os.path.join(self.dir_name, 'figs'))
            RunCommand(command, self.dry_run)

            # Plot the limits
            command = 'python plotLimitExpObs_2D.py {}  {}  {}  {} {} {} {} {} {}'.format(self.start_mass, self.end_val, self.step_sizes, self.year, self.blind, datacard, SearchString4Datacard, self.dir_name, self.frac_vbf)
            RunCommand(command, self.dry_run)

    def Run(self):
        logger.debug("Current working directory: %s", os.getcwd())

        # STEP - 1: For Datacard and workspace creation step load datacard class
        if (self.step).lower() in ('dc'): # or (self.step).lower() == 'all': # Fixme: all year is not working for 'dc'
            self.run_step_dc()
        elif (self.step).lower() == 'plot':
            self.run_step_plot()
        else:
            if not self.ifParallel:
                logger.debug("Running in serial mode")
                for current_mass in range(self.start_mass, self.end_val, self.step_sizes):
                    self.run_parallel(current_mass)
            else:
                pool = mp.Pool()
                try:
                    pool.map(partial(run_parallel_instance, self), range(self.start_mass, self.end_val, self.step_sizes))
                finally:
                    pool.close()
                    pool.join()

def validate_args(args):
    """Validate command-line arguments.

    Args:
        args (namespace): Namespace containing command-line arguments.

    Raises:
        argparse.ArgumentError: Raise argument error if valiaation fails.
    """
    if args.step == 'ri' and args.substep == 11:
        raise argparse.ArgumentError(None, "--substep/-ss is mandatory for step ri")

def configure_logging(args):
    """Configure logging based on command-line arguments.

    Args:
        args (namespace): Namespace containing command-line arguments.
    """
    logger.debug("Setting log level to {}".format(args.log_level))
    logger.setLevel(args.log_level)
    ROOT.RooMsgService.instance().setGlobalKillBelow(args.log_level_roofit)

def set_years_new(args_year):
    """This code need the array of years to run the code for all years or for a specific year. This function will return the array of years.

    Args:
        args_year (str): defined year string

    Returns:
        array: array having years
    """
    year_mapping = {
        '2016preapv': ['2016preAPV'],
        '2016postapv': ['2016postAPV'],
        '2016': [2016],
        '2017': [2017],
        '2018': [2018],
        'all': [2016, 2017, 2018],
        'allc': [2016, 2017, 2018,'run2'],
        'run2': ['run2']
    }
    return year_mapping.get(args_year.lower(), [])

def main():
    """Main function to handle command-line arguments, validate them, and run the appropriate steps.
    """
    parser = argparse.ArgumentParser(description="Run combine for high mass Higgs search analysis")

    general_settings = parser.add_argument_group("General Settings")
    mass_settings = parser.add_argument_group("Mass Settings")
    year_condor_settings = parser.add_argument_group("Year and Condor Settings")
    fit_settings = parser.add_argument_group("Fit Settings")
    logging_settings = parser.add_argument_group("Logging Settings")
    advanced_settings = parser.add_argument_group("Advanced Settings")
    step_control = parser.add_argument_group("Step Control")

    # General Settings
    general_settings.add_argument('-i', '--input', dest='input_dir', type=str, default="", help='inputs directory')
    general_settings.add_argument('-d', '--is2D', dest='is_2d', type=int, default=1, help='is2D (default:1)')
    general_settings.add_argument('-a', '--append', dest='append_name', type=str, default="", help='append name for cards dir')
    general_settings.add_argument("--dry-run", action="store_true", help="Don't actually run the command, just print it.")
    general_settings.add_argument("-p", "--parallel", action="store_true", help="Run jobs parallelly")

    # Mass Settings
    mass_settings.add_argument('-mi', '--MassStartVal', dest='MassStartVal', type=int, default=500, help='MassStartVal (default:1)')
    mass_settings.add_argument('-mf', '--MassEndVal', dest='MassEndVal', type=int, default=3001, help='MassEndVal (default:1)')
    mass_settings.add_argument('-ms', '--MassStepVal', dest='MassStepVal', type=int, default=50, help='MassStepVal (default:1)')

    # Year and Condor Settings
    year_condor_settings.add_argument("-y", "--year", dest="year", type=str, default='2016', help="year to run or run for all three year. Options: 2016, 2017, 2018,all (=16, 17 and 18), allc (=all + run2), run2")
    year_condor_settings.add_argument("-c", "--ifCondor", action="store_true", dest="ifCondor", default=False, help="if you want to run combine command for all mass points parallel using condor make it 1")

    # Fit Settings
    fit_settings.add_argument("-allDatacard", "--allDatacard", action="store_true", dest="allDatacard", default=False, help="If we need limit values or impact plot for each datacards, stored in file ListOfDatacards.py")
    fit_settings.add_argument('-f', '--fracVBF', dest='frac_vbf', type=float, default=-1, help='fracVBF, -1 means float this frac. (default:-1)')
    fit_settings.add_argument("-b", "--blind", action="store_false", dest="blind", default=True, help="Running blind?")
    fit_settings.add_argument("-howToBlind", "--howToBlind", dest="howToBlind", type=str, default='--run blind', help="howToBlind: --run blind, -t -1 --expectSignal 0, -t -1 --expectSignal 1")
    fit_settings.add_argument("-signalStrength", "--signalStrength", dest="signalStrength", type=float, default=0.0, help="signal strength for the fit")
    fit_settings.add_argument("-freezeParameters", "--freezeParameters", dest="freezeParameters", type=str, default="", help="freeze parameters for the fit. If want to freeze all then give argumen `allConstrainedNuisances`")
    fit_settings.add_argument("-setParameterRanges", "--setParameterRanges", dest="setParameterRanges", type=str, default="", help="set parameters range for the fit. Its format should be `r=-1,3:BTAG_resolved=-5,5:BTAG_merged=-5,5`")
    fit_settings.add_argument("-AdditionalFitOptions", "--AdditionalFitOptions", dest="AdditionalFitOptions", type=str, default="", help="AdditionalFitOptions for the fit. Its format should be `--cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.01 --setRobustFitTolerance 0.01`")

    # Logging Settings
    logging_settings.add_argument("--log-level", default=logging.INFO, type=lambda x: getattr(logging, x.upper()), help="Configure the logging level.")
    logging_settings.add_argument("--log-level-roofit", default=ROOT.RooFit.WARNING, type=lambda x: getattr(ROOT.RooFit, x.upper()), help="Configure the logging level for RooFit.")
    logging_settings.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False, help="don't print status messages to stdout")
    logging_settings.add_argument("-combineVerbose", "--combineVerbose", dest="combineVerbose", type=int, default=0, help="combineVerbose for the fit. Its format should be `--verbose 0`")

    # Advanced Settings
    advanced_settings.add_argument("-date", "--date", dest="date", type=str, default='', help="If this option is given, then it will append date string to the output file name. This is helpful if I want to use the combine output from different date")
    advanced_settings.add_argument("-tag", "--tag", dest="tag", type=str, default='', help="This option add additional string in the combine output root file as well as condor/combine log file")
    advanced_settings.add_argument("-sanityCheck", "--sanity-check", action="store_true", dest="SanityCheckPlotUsingWorkspaces", default=False, help="If this option is given, then it will plot the sanity check plots using workspaces")
    advanced_settings.add_argument("-split2016", "--split2016", action="store_true", default=False, help="when combine run2 datacards set this option to True to split 2016 to 2016preAPV and 2016postAPV")


    # Step Control
    step_control.add_argument('-s', '--step', dest='step', type=str, default='dc', help='Which step to run: dc (DataCardCreation), cc (CombineCards), ws (Get workspaces) rc (RunCombine), fd (Fit Diagnostics) ri (run Impact), fs (fastScan), rll (run loglikelihood with and without syst) , corr (Correlation), plot or all', choices=["dc", "cc", "ws", "rc", "fd", "ri", "riess", "fs", "rll", "corr", "plot", "all"])
    step_control.add_argument('-ss', '--substep', dest='substep', type=int, default=11, help='sub-step help')

    args = parser.parse_args()

    # Validate arguments for the step. This function is added as some of steps (like ri) need substep to be defined as there are multiple substeps for that step
    # Just to ensure that we give appropriate sub-step for the step, this function is added
    try:
        validate_args(args)
    except argparse.ArgumentError as e:
        parser.error(str(e))

    # Logging setup for both logging and RooFit logging
    configure_logging(args)
    logger.info("Setting log level to {}".format(args.log_level))

    # Get the full command line used to run the current Python script
    command_line = ' '.join(sys.argv)
    SaveInfoToTextFile("#"*75+'\n\n')
    SaveInfoToTextFile('python '+command_line+'\n\n')

    DirectoryCreatorObj = DirectoryCreator(args)

    # Get the list of years to run
    years = set_years_new(args.year)

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

if __name__ == "__main__":
    main()
