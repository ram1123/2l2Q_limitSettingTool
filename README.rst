Introduction
============

This is a command line tool designed to perform a high mass Higgs search analysis using the combine software. It includes options for creating datacards, combining them, and running combine on the resulting cards to produce various results including limit values and impact plots.

Installation
============

Setup Higgs combine tool
------------------------

**Step-1:** Combine setup inheritted from [https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/)

.. code:: bash

   export SCRAM_ARCH=slc7_amd64_gcc700
   cmsrel CMSSW_11_3_4
   cd CMSSW_11_3_4/src
   cmsenv
   git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
   cd HiggsAnalysis/CombinedLimit
   cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
   git fetch origin
   git checkout v9.0.0
   scramv1 b clean; scramv1 b # always make a clean build
   cd $CMSSW_BASE/src
   bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/main/CombineTools/scripts/sparse-checkout-ssh.sh)
   scramv1 b -j 8


**Step-2:** Get the custom tool for datacard creation and limit computation

.. code:: bash

   cd $CMSSW_BASE/src
   git clone git@github.com:ram1123/2l2q_limitsettingtool.git -b main

Usage
=====

The tool is run from the command line with various options. Here is a list of command line available options:

General Settings
----------------

- **-i, --input**
    - Type: ``str``
    - Default: ``""``
    - Description: Specifies the input directory.

- **-d, --is2D**
    - Type: ``int``
    - Default: ``1``
    - Description: Determines whether it is a 2D analysis.

- **-a, --append**
    - Type: ``str``
    - Default: ``""``
    - Description: Append name for cards directory.

- **--dry-run**
    - Action: ``store_true``
    - Description: Don't actually run the command, just print it.

- **-p, --parallel**
    - Action: ``store_true``
    - Description: Run jobs in parallel.

Mass Settings
-------------

- **-mi, --MassStartVal**
    - Type: ``int``
    - Default: ``500``
    - Description: Starting value for mass range.

- **-mf, --MassEndVal**
    - Type: ``int``
    - Default: ``3001``
    - Description: Ending value for mass range.

- **-ms, --MassStepVal**
    - Type: ``int``
    - Default: ``50``
    - Description: Step value for mass range.

Year and Condor Settings
------------------------

- **-y, --year**
    - Type: ``str``
    - Default: ``2016``
    - Description: Specifies the year to run the analysis. Options are: 2016, 2017, 2018, all, allc, run2.

- **-c, --ifCondor**
    - Action: ``store_true``
    - Default: ``False``
    - Description: Use Condor to run the combine command for all mass points in parallel.

Fit Settings
------------

- **-allDatacard, --allDatacard**
    - Action: ``store_true``
    - Default: ``False``
    - Description: If enabled, provides limit values or impact plots for each data card stored in ``ListOfDatacards.py``.

- **-f, --fracVBF**
    - Type: ``float``
    - Default: ``-1``
    - Description: Fraction of VBF (Vector Boson Fusion). A value of -1 means this fraction will float.

- **-b, --blind**
    - Action: ``store_false``
    - Default: ``True``
    - Description: Enable or disable blind analysis.

- **-signalStrength, --signalStrength**
    - Type: ``float``
    - Default: ``0.0``
    - Description: Signal strength for the fit.

- **-freezeParameters, --freezeParameters**
    - Type: ``str``
    - Default: ``""``
    - Description: Freeze parameters for the fit. The format should be like ``r=-1,3:BTAG_resolved=-5,5:BTAG_merged=-5,5``.

Logging Settings
----------------

- **--log-level**
    - Type: ``logging level``
    - Default: ``logging.INFO``
    - Description: Configure the logging level.

- **--log-level-roofit**
    - Type: ``RooFit level``
    - Default: ``ROOT.RooFit.WARNING``
    - Description: Configure the logging level for RooFit.

- **-v, --verbose**
    - Action: ``store_true``
    - Default: ``False``
    - Description: Enable verbose logging.

Advanced Settings
-----------------

- **-date, --date**
    - Type: ``str``
    - Default: ``""``
    - Description: Append date string to the output file name.

- **-tag, --tag**
    - Type: ``str``
    - Default: ``""``
    - Description: Add additional string in combine output and log files.

- **-sanityCheck, --sanity-check**
    - Action: ``store_true``
    - Default: ``False``
    - Description: Enable sanity check plots using workspaces.

Step Control
------------

- **-s, --step**
    - Type: ``str``
    - Default: ``dc``
    - Description: Specify which step to run. Choices are: ``dc``, ``cc``, ``ws``, ``rc``, ``fd``, ``ri``, ``fs``, ``rll``, ``corr``, ``plot``, ``all``.

- **-ss, --substep**
    - Type: ``int``
    - Default: ``11``
    - Description: Specify a sub-step.


***Usage Example***


.. code:: bash

   # Datacard creation step for year 2018
   python makeDCsandWSs.py -i HM_inputs_2018UL  -y 2018 -s dc

   # Combine card step for year 2018
   python makeDCsandWSs.py -i HM_inputs_2018UL  -y 2018 -s cc

   # Asymptotic combine command step to get the limit for year 2018
   python makeDCsandWSs.py -i HM_inputs_2018UL  -y 2018 -s rc

   # Asymptotic combine command step to get the limit for year 2018 and for all mass points in parallel using condor
   python makeDCsandWSs.py -i HM_inputs_2018UL  -y 2018 -s rc -c -p

   # Impact plot step for year 2018. Impact plot has 3 steps: InitialFit, doFits, and plotImpacts.
   # Below commands will run each step for all mass points for 2018 using condor.
   # `-p` is used so that it will submit jobs in parallel for all mass points
   # `-ss` is used to specify which sub-step to run.
   # Don't submit next step until the previous step is finished. Otherwise, it won't find the input files and give you errors.
   python makeDCsandWSs.py -i HM_inputs_2018UL  -y 2018 -s ri -ss 1 -c -p
   python makeDCsandWSs.py -i HM_inputs_2018UL  -y 2018 -s ri -ss 2 -c -p
   python makeDCsandWSs.py -i HM_inputs_2018UL  -y 2018 -s ri -ss 3 -c -p

   # To run the impact plot or any other step for once mass point use the option `-mi` and `-mf` to specify the mass point
   python makeDCsandWSs.py -i HM_inputs_2018UL  -y 2018 -s ri -ss 1 -mi 500 -mf 501
   # The above command will run only the mass point 500 GeV

Input Information Required
==========================

To run this tool, you will need to have the following input information:

-  Directory ``HM_inputs_2018UL`` that contains systematic information.
-  Resolution info in directory: ``Resolution``.
-  Templates: ``templates1D`` and ``templates2D``.
-  Directory: ``CMSdata``.
-  Signal Efficiency: ``SigEff``.

Please make sure that you have all of these directories and files
available and that they are properly formatted before running the tool.

Additional Information
======================

Here are some additional details to keep in mind when running this tool:

-  In ``HM_inputs_*``, you should prepare 12 systematics files
   ((resolved, merged) *(b_tagged, un-tagged, vbf_tagged)* (ee, mumu)).
   Now, you can just go into these ``.txt`` files and change the value
   of systematics.
-  ``-a`` appends a name for the cards directory. For example, ``-a``
   test will create ``cards_test`` to store all datacards. When you run
   this tool, it is better to keep the option ``-a`` the same as ``-y``.
   For example, in ``cards_2016``, ``cards_2017``, and ``cards_2018``.
