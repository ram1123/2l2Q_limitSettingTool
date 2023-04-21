# Introduction

This is a command line tool designed to perform a high mass Higgs search analysis using the combine software. It includes options for creating datacards, combining them, and running combine on the resulting cards to produce various results including limit values and impact plots.

# Installation

## Setup Higgs combine tool

**Step-1:** Combine setup inheritted from [https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/)

```bash
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
```

**Step-2:** Get the custom tool for datacard creation and limit computation

  ```bash
  cd $CMSSW_BASE/src
  git clone git@github.com:ram1123/2l2q_limitsettingtool.git -b main
  ```

# Usage

The tool is run from the command line with various options. Here is a list of available options:

- `-i`, `--input`: Specify the input directory (default: "")
- `-d`, `--is2D`: Specify if the input is 2D template or 1D (default: 1)
- `-mi`, `--MassStartVal`: Specify the starting mass value (default: 500)
- `-mf`, `--MassEndVal`: Specify the ending mass value (default: 3001)
- `-ms`, `--MassStepVal`: Specify the step value (default: 50)
- `-a`, `--append`: Append a name for the cards directory (default: "")
- `-f`, `--fracVBF`: Specify the fraction of VBF (default: 0.5%)
- `-y`, `--year`: Specify the year to run or run for all three years. Options: 2016, 2017, 2018, all (to run all 3 year), run2 (for combination of all 3 years).
- `-s`, `--step`: Specify which step to run. Options: dc (DataCardCreation), cc - (CombineCards), rc (RunCombine), ri (run Impact), rll (run loglikelihood with and - without syst), fast (FastScan) or all (default: dc)
- `-c`, `--ifCondor`: Set to 1 to run combine command for all mass points in parallel using - condor (default: False)
- `-b`, `--blind`: Set to False to run unblinded (default: True)
- `-allDatacard`, `--allDatacard`: Set to True if limit values or impact plots are needed for - each datacard written in file [ListOfDatacards.py](ListOfDatacards.py) (default: False)
- `-bOnly`, `--bOnly`: Set to True to perform background only fit (default: False)
- `-v`, `--verbose`: Set to True to print status messages to stdout (default: False)
- `--log-level:` Set the logging level. Options: DEBUG, INFO, WARNING, ERROR (default: - `WARNING`)
- `--dry-run:` Set to True to print the command without actually running it (default: False)
- `-p`, `--parallel`: Set to True to run jobs in parallel (default: False)
- `-date`, `--date`: Specify a date string (default: "")
- `-tag`, `--tag`: Specify a tag string (default: "")

Here is few example command:

```bash
# Run datacard step for year 2018. For now all 3 years datacard can't be created. There is some issue that need to be addressed
python makeDCsandWSs.py -y 2018 -s dc

# Run 2018 datacard/workspace creation step
python makeDCsandWSs.py -i HM_inputs_2018UL  -y 2018 -a 2018 -s dc
# Run 2018 combine card step
python makeDCsandWSs.py -i HM_inputs_2018UL  -y 2018 -a 2018 -s cc
# Run 2018 asymptotic combine command step to get the limit
python makeDCsandWSs.py -i HM_inputs_2018UL  -y 2018 -a 2018 -s rc

# To run all steps (except datacard creation one) and for all years, using condor (`-c`) and use parallel processing (`-p`) to submit the jobs
time(python makeDCsandWSs.py -s all -y all -p -c)

# To run all steps (except datacard creation one) and for all years and on all datacards specified in file `ListOfDatacards.py`, using condor (`-c`) and use parallel processing (`-p`) to submit the jobs
time(python makeDCsandWSs.py -s all -y all -p -c --allDatacard)
```

# Input Information Required

To run this tool, you will need to have the following input information:

- Directory `HM_inputs_2018UL` that contains systematic information.
- Resolution info in directory: `Resolution`.
- Templates: `templates1D` and `templates2D`.
- Directory: `CMSdata`.
- Signal Efficiency: `SigEff`.

Please make sure that you have all of these directories and files available and that they are properly formatted before running the tool.

# Additional Information

Here are some additional details to keep in mind when running this tool:

- In `HM_inputs_*`, you should prepare 12 systematics files ((resolved, merged) * (b_tagged, un-tagged, vbf_tagged) * (ee, mumu)). Now, you can just go into these `.txt` files and change the value of systematics.
- `-a` appends a name for the cards directory. For example, `-a` test will create `cards_test` to store all datacards. When you run this tool, it is better to keep the option `-a` the same as `-y`. For example, in `cards_2016`, `cards_2017`, and `cards_2018`.

