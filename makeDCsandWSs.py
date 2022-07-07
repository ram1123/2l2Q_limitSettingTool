#!/usr/bin/python
#-----------------------------------------------
# Latest update: 2012.08.30
# by Matt Snowball
#-----------------------------------------------
import sys, os, pwd, commands
import optparse, shlex, re
import math
from ROOT import *
import ROOT
from array import array
from datacardClass import *
from inputReader import *

#define function for parsing options
def parseOptions():

    usage = ('usage: %prog [options] datasetList\n'
             + '%prog -h for help')
    parser = optparse.OptionParser(usage)
    
    parser.add_option('-i', '--input', dest='inputDir', type='string', default="",    help='inputs directory')
    parser.add_option('-d', '--is2D',   dest='is2D',       type='int',    default=1,     help='is2D (default:1)')
    parser.add_option('-a', '--append', dest='appendName', type='string', default="",    help='append name for cards dir')
    parser.add_option('-b', action='store_true', dest='noX', default=True ,help='no X11 windows')
    parser.add_option('-f', '--fracVBF',   dest='fracVBF',       type='float',    default=0.005,     help='fracVBF (default:0.5%)')    

    # store options and arguments as global variables
    global opt, args
    (opt, args) = parser.parse_args()

    if (opt.is2D != 0 and opt.is2D != 1):
        print 'The input '+opt.is2D+' is unkown for is2D.  Please choose 0 or 1. Exiting...'
        sys.exit()

    if (opt.appendName == ''):
        print 'Please pass an append name for the cards directory! Exiting...'
        sys.exit()

    if (opt.inputDir == ''):
        print 'Please pass an input directory! Exiting...'
        sys.exit()

# define make directory function
def makeDirectory(subDirName):

    cmd = 'mkdir -p '+subDirName
    #status, output = commands.getstatusoutput(cmd)
    output = commands.getstatusoutput(cmd)

    '''
    if (not os.path.exists(subDirName)):
        cmd = 'mkdir -p '+subDirName
        status, output = commands.getstatusoutput(cmd)
        if status !=0:
            print 'Error in creating submission dir '+subDirName+'. Exiting...'
            sys.exit()
    else:
        print 'Directory '+subDirName+' already exists. Exiting...'
        sys.exit()
    '''


#define function for processing of os command
def processCmd(cmd):
#    print cmd
    status, output = commands.getstatusoutput(cmd)
    if status !=0:
        print 'Error in processing command:\n   ['+cmd+'] \nExiting...'
        sys.exit()



def creationLoop(directory):
    global opt, args
    
#    startMass=[ 380.0, 400.0, 600.0 ]
#    stepSizes=[ 10.0,   20.0, 50.0 ]
#    endVal=[ 1, 10, 9 ]

#    startMass=[ 200.0, 290.0, 350.0, 400.0, 600.0 ]
#    stepSizes=[  2.0,   5.0,   10.0,  20.0,  50.0 ]
#    endVal   =[   45,    12,    4,     10,    9   ]

    startMass=[ 550.0]
    stepSizes=[ 50]
    endVal=[   30]

#    startMass=  [ 110.0, 124.5, 126.5, 130.0]
#    stepSizes=  [  0.5,   0.1,   0.5,   1.0]
#    endVal=     [  29,     20,    7,     30]

#    startMass=[ 127.0, 130.0, 160.0]
#    stepSizes=[ 0.5,    1.0,   2.0]
#    endVal=[     6,      30,    21]

    myClass = datacardClass()
    myClass.loadIncludes()

    a=0
    while (a < len(startMass) ):
	
	c = 0
        while (c < endVal[a] ): 
            
            mStart = startMass[a]
            step = stepSizes[a]
            mh = mStart + ( step * c ) 
            mhs = str(mh).replace('.0','')

            print mh

            makeDirectory(directory+'/HCG/'+mhs)

            # channels = {'eeqq_Merged','eeqq_Resolved','mumuqq_Merged','mumuqq_Resolved'}
            channels = {'eeqq_Merged'}
            cats = {'vbf-tagged','b-tagged','untagged'}

            #channels = {'mumuqq_Resolved'}
            #cats = {'untagged'}

            for channel in channels :

               for cat in cats:

                  myReader = inputReader(opt.inputDir+"/"+channel+"_"+cat+".txt")
                  myReader.readInputs()
                  theInputs = myReader.getInputs()

                  myClass.makeCardsWorkspaces(mh,opt.is2D,directory,theInputs,cat, opt.fracVBF)

            c += 1
            

	a += 1






# the main procedure
def makeDCsandWSs():
    
    # parse the arguments and options
    global opt, args
    parseOptions()

    if (opt.appendName != ''):
        dirName = 'cards_'+opt.appendName
    

    subdir = ['HCG','figs']

    for d in subdir:
            makeDirectory(dirName+'/'+d)
        

    creationLoop(dirName)
    

    sys.exit()



# run the create_RM_cfg() as main()
if __name__ == "__main__":
    makeDCsandWSs()


