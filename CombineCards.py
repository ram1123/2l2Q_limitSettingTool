import os

def RunCommand(command):
    # print("#"*51)
    print(command)
    os.system(command)

os.chdir('cards_2018/HCG/500/')

# t_values = ['Resolved', 'Merged']
t_values = ['Resolved']

AllCardsCombination = 'combineCards.py  -s '
for t in t_values:
    RunCommand("rm hzz2l2q_mumuqq_{}_13TeV.txt".format(t))
    RunCommand("rm hzz2l2q_eeqq_{}_13TeV.txt".format(t))
    RunCommand("rm hzz2l2q_{}_13TeV_xs.txt".format(t))
    RunCommand("rm hzz2l2q_{}_13TeV_xs.root".format(t))

    for fs in ["eeqq_{}".format(t), "mumuqq_{}".format(t)]:
        RunCommand("combineCards.py hzz2l2q_{FinalState}_untagged_13TeV.txt hzz2l2q_{FinalState}_b-tagged_13TeV.txt hzz2l2q_{FinalState}_vbf-tagged_13TeV.txt > hzz2l2q_{FinalState}_13TeV.txt".format(FinalState = fs))

    RunCommand("combineCards.py hzz2l2q_mumuqq_{Category}_13TeV.txt hzz2l2q_eeqq_{Category}_13TeV.txt > hzz2l2q_{Category}_13TeV_xs.txt".format(Category = t))

    for cat in ["untagged", "b-tagged", "vbf-tagged"]:
        RunCommand("combineCards.py hzz2l2q_eeqq_{Category}_{Tag}_13TeV.txt hzz2l2q_mumuqq_{Category}_{Tag}_13TeV.txt > hzz2l2q_{Category}_{Tag}_13TeV.txt".format(Category = t,  Tag = cat))

    AllCardsCombination = AllCardsCombination +' hzz2l2q_{Category}_13TeV_xs.txt'.format(Category = t)
RunCommand("#"*51)

AllCardsCombination = AllCardsCombination +' > hzz2l2q_13TeV_xs_NoNuisance.txt'
AllCardsWithNuisance = (AllCardsCombination.replace('-s','  ')).replace('_NoNuisance','')

RunCommand(AllCardsWithNuisance)
RunCommand(AllCardsCombination)
