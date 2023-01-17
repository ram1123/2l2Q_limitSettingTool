import os

ifNuisance = True

datacard = "hzz2l2q_13TeV_xs.txt" if  ifNuisance else "hzz2l2q_13TeV_xs_NoNuisance.txt"
def RunCommand(command):
    print("#"*51)
    print(command)
    os.system(command)

os.system('cd cards_2018/HCG/')
os.chdir("./cards_2018/HCG/")

for type in ["2D"]:
    print(type)
    # for n in range(0, 50):
    for n in range(0, 1):
        mH = 500 + 50*n
        print("mH value: {}".format(mH))
        os.chdir("./{}/".format(mH))
        RunCommand("combine -n mH{mH}_exp -m {mH} -M AsymptoticLimits  {datacard}  --rMax 1 --rAbsAcc 0 --run blind > {type}_mH{mH}_exp.log".format(type = type, mH = mH, datacard = datacard))
        os.chdir("../")
