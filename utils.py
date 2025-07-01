import os
import logging
import datetime

import yaml
import ROOT as R

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# create a formatter
class ColorLogFormatter(logging.Formatter):
     """A class for formatting colored logs.
     Reference: https://stackoverflow.com/a/70796089/2302094
     """

     # FORMAT = "%(prefix)s%(msg)s%(suffix)s"
     FORMAT = "%(prefix)s[%(levelname)s] - [%(filename)s:#%(lineno)d] - %(message)s %(suffix)s"
    #  FORMAT = "{}[%(levelname)5s] - [%(filename)s:#%(lineno)d] - [%(funcName)s; %(module)s]{} - %(prefix)s%(message)s %(suffix)s".format(
        #  bcolors.HEADER, bcolors.ENDC
    #  )
    #  FORMAT = "\n%(asctime)s - [%(filename)s:#%(lineno)d] - %(prefix)s%(levelname)s - %(message)s %(suffix)s\n"

     LOG_LEVEL_COLOR = {
         "INFO": {'prefix': bcolors.OKGREEN, 'suffix': bcolors.ENDC},
         "DEBUG": {'prefix': bcolors.OKBLUE, 'suffix': bcolors.ENDC},
         "WARNING": {'prefix': bcolors.WARNING, 'suffix': bcolors.ENDC},
         "CRITICAL": {'prefix': bcolors.FAIL, 'suffix': bcolors.ENDC},
         "ERROR": {'prefix': bcolors.FAIL+bcolors.BOLD, 'suffix': bcolors.ENDC+bcolors.ENDC},
     }

     def format(self, record):
         """Format log records with a default prefix and suffix to terminal color codes that corresponds to the log level name."""
         if not hasattr(record, 'prefix'):
             record.prefix = self.LOG_LEVEL_COLOR.get(record.levelname.upper()).get('prefix')

         if not hasattr(record, 'suffix'):
             record.suffix = self.LOG_LEVEL_COLOR.get(record.levelname.upper()).get('suffix')

         formatter = logging.Formatter(self.FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p' )
         return formatter.format(record)

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(ColorLogFormatter())
logger.addHandler(stream_handler)
logger.setLevel( logging.ERROR)

def SaveInfoToTextFile(Info):
    # Get the CMSSW environment path
    cmssw_base = os.environ.get('CMSSW_BASE', '')
    today = datetime.datetime.now()
    date_string = today.strftime("%d%b").lower()
    file_path = os.path.join(cmssw_base, 'src/2l2q_limitsettingtool/commands_{}.log'.format(date_string))
    with open(file_path, 'a') as file:
        # Get the current date and time, and format it as a string
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Get the current working directory (pwd)
        current_working_directory = os.getcwd()
        # Write the command to the file
        file.write('===> Current time: ' + current_time + '\n')
        file.write('pwd: ' + current_working_directory + '\n')
        file.write('Command: ' + Info + '\n')

def RunCommand(command, dry_run=False):
    logger.debug("="*51)
    logger.info("COMMAND TO RUN: {}".format(command))
    SaveInfoToTextFile(command)
    if not dry_run:
        logger.debug("Inside module RunCommand(command, dry_run=False):")
        os.system(command)

def RemoveFile(FileName):
    if os.path.exists(FileName):
        logger.debug("Removing file, {}".format(FileName))
        os.remove(FileName)
    else:
        logger.debug("File, {}, does not exist".format(FileName))

def make_directory( sub_dir_name):
    if not os.path.exists(sub_dir_name):
        logger.debug("{}{}\nCreate directory: {}".format('\t\n', '#'*51, sub_dir_name))
        os.makedirs(sub_dir_name)
    else:
        logger.debug('Directory '+sub_dir_name+' already exists. Exiting...')

def border_msg(msg):
    """
    Print message inside the border.

    Example:
    >>> border_msg('hello')
    +-----+
    |hello|
    +-----+

    Args:
        msg (str): message to print inside border
    """
    row = len(msg)+12
    h = ''.join(['+'] + ['-' *row] + ['+'])
    result = h + '\n'"|      "+msg+"      |"'\n' + h
    print(result)


def read_bkg(fs, year, jetType, region, cat, sam, ZZmass):
    if (cat == 'vbf_tagged'):
        cat = "vbf"
    elif (cat == 'b_tagged'):
        cat = "btag"
    elif (cat == 'untagged'):
        cat = ""

    path = "hist_pars_{}_{}.yaml".format(fs, year)
    with open(path, 'r') as file:
        data_dict = yaml.safe_load(file)
    par = data_dict["{}_{}_{}_{}".format(jetType, region, cat, sam)]
    a0 = R.RooRealVar("a0", "", 1, 200., 550.)
    a1 = R.RooRealVar("a1", "", 1, 10., 200.)
    a2 = R.RooRealVar("a2", "", 1, 0., 300.)
    a3 = R.RooRealVar("a3", "", 0, 0., 1.0)
    a4 = R.RooRealVar("a4", "", par[4], 200., 550.)
    a5 = R.RooRealVar("a5", "", par[5], 10., 500.)
    a6 = R.RooRealVar("a6", "", par[6], 0., 300.)
    a7 = R.RooRealVar("a7", "", par[7], 0., 1.0)
    a8 = R.RooRealVar("a8", "", par[8], 0., 300.)
    a9 = R.RooRealVar("a9", "", par[9], -1.0, 1.0)
    a0.setConstant(True)
    a1.setConstant(True)
    a2.setConstant(True)
    a3.setConstant(True)
    aa = [a0, a1, a2, a3, a4, a5, a6, a7, a8, a9]
    ggzzpdf = R.RooggZZPdf_v2("ggzzpdf", "",ZZmass , a0, a1, a2, a3, a4, a5, a6, a7, a8, a9)

    # canvas = R.TCanvas("canvas", "ggzzpdf Plot", 800, 600)
    # canvas.cd()
    # frame = ZZmass.frame(R.RooFit.Title("ggzzpdf Distribution"))
    # ggzzpdf.plotOn(frame, R.RooFit.LineColor(R.kBlue), R.RooFit.LineWidth(2))
    # frame.Draw()
    # latex = R.TLatex()
    # latex.SetNDC()
    # latex.SetTextSize(0.04)
    # canvas.SaveAs("test/{}_{}_{}_{}.png".format(jetType, region, cat, sam))

    return ggzzpdf, aa, par[-1]