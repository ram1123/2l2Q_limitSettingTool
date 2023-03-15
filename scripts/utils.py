import os
import logging

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

    #  FORMAT = "%(prefix)s%(msg)s%(suffix)s"
     FORMAT = "[%(levelname)s] - [%(filename)s:#%(lineno)d] - %(prefix)s%(levelname)s - %(message)s %(suffix)s"
    #  FORMAT = "{}[%(levelname)5s] - [%(filename)s:#%(lineno)d] - [%(funcName)s; %(module)s]{} - %(prefix)s%(message)s %(suffix)s".format(
        #  bcolors.HEADER, bcolors.ENDC
    #  )
    #  FORMAT = "\n%(asctime)s - [%(filename)s:#%(lineno)d] - %(prefix)s%(levelname)s - %(message)s %(suffix)s\n"

     LOG_LEVEL_COLOR = {
         "DEBUG": {'prefix': bcolors.OKBLUE, 'suffix': bcolors.ENDC},
         "INFO": {'prefix': bcolors.OKGREEN, 'suffix': bcolors.ENDC},
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

def RunCommand(command, dry_run=False):
    logger.info("="*51)
    logger.error("Command: {}".format(command))
    logger.debug("dry_run: {}".format(dry_run))
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
        logger.info("{}{}\nCreate directory: {}".format('\t\n', '#'*51, sub_dir_name))
        os.makedirs(sub_dir_name)
    else:
        logger.info('Directory '+sub_dir_name+' already exists. Exiting...')

def border_msg(msg):
    """Print message inside the border
    >>> border_msg('hello')
        +-----+
        |hello|
        +-----+
    Args:
        msg (str): message to print inside border
    """
    row = len(msg)+4
    h = ''.join(['+'] + ['-' *row] + ['+'])
    result= h + '\n'"|  "+msg+"  |"'\n' + h
    print(result)
