import json

# Load JSON data from two files
with open("datacards_HIG_23_001/cards_2018_WithAllJES_MZZ450/figs/limits_Summary_2018_30mar_blind__HCG.json", "r") as f1:
    data1 = json.load(f1)

with open("datacards_HIG_23_001/cards_2018_WithAllJES/figs/limits_Summary_2018_28mar_blind__HCG.json", "r") as f2:
    data2 = json.load(f2)

# Function to calculate the percentage difference
def percentage_difference(a, b):
    return abs(a - b) / ((a + b) / 2) * 100

# Compare "exp0" values and print the percentage difference
for key in data1.keys():
    exp0_data1 = data1[key]["exp0"]
    exp0_data2 = data2[key]["exp0"]

    difference = percentage_difference(exp0_data1, exp0_data2)
    print("Difference in 'exp0' for {}: {:.2f}%".format(key, difference))
