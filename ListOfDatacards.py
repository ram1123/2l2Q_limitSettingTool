datacardList = [
    # "hzz2l2q_13TeV_xs.txt",
    # "hzz2l2q_13TeV_xs_NoNuisance.txt",

    #"hzz2l2q_Merged_13TeV_xs.txt",
    #"hzz2l2q_Merged_vbf_tagged_13TeV.txt",
    #"hzz2l2q_Merged_b_tagged_13TeV.txt",
    #"hzz2l2q_Merged_untagged_13TeV.txt",

    #"hzz2l2q_Resolved_13TeV_xs.txt",
    #"hzz2l2q_Resolved_vbf_tagged_13TeV.txt",
    #"hzz2l2q_Resolved_b_tagged_13TeV.txt",
    #"hzz2l2q_Resolved_untagged_13TeV.txt",

    #"hzz2l2q_eeqq_Merged_13TeV.txt",
    "hzz2l2q_eeqq_Merged_b_tagged_13TeV.txt",
    #"hzz2l2q_eeqq_Merged_untagged_13TeV.txt",
    #"hzz2l2q_eeqq_Merged_vbf_tagged_13TeV.txt",
    #"hzz2l2q_eeqq_Resolved_13TeV.txt",
    #"hzz2l2q_eeqq_Resolved_b_tagged_13TeV.txt",
    #"hzz2l2q_eeqq_Resolved_untagged_13TeV.txt",
    #"hzz2l2q_eeqq_Resolved_vbf_tagged_13TeV.txt",

    #"hzz2l2q_mumuqq_Merged_13TeV.txt",
    #"hzz2l2q_mumuqq_Merged_b_tagged_13TeV.txt",
    #"hzz2l2q_mumuqq_Merged_untagged_13TeV.txt",
    #"hzz2l2q_mumuqq_Merged_vbf_tagged_13TeV.txt",
    #"hzz2l2q_mumuqq_Resolved_13TeV.txt",
    #"hzz2l2q_mumuqq_Resolved_b_tagged_13TeV.txt",
    #"hzz2l2q_mumuqq_Resolved_untagged_13TeV.txt",
    #"hzz2l2q_mumuqq_Resolved_vbf_tagged_13TeV.txt"
]

Condor_queue = {    # This list is Not in use
    1: "espresso",  # 20min
    2: "microcentury", # 1 hr
    3: "longlunch", # 2 hr
    4: "workday",   # 8 hr
    5: "tomorrow",  # 1 day
    6: "testmatch"  # 3 day
}

datacardList_condor = {
    "hzz2l2q_13TeV_xs.txt": "workday",
    "hzz2l2q_13TeV_xs_NoNuisance.txt": "microcentury",

    "hzz2l2q_Merged_13TeV_xs.txt": "microcentury",
    "hzz2l2q_Merged_vbf_tagged_13TeV.txt": "microcentury",
    "hzz2l2q_Merged_b_tagged_13TeV.txt": "microcentury",
    "hzz2l2q_Merged_untagged_13TeV.txt": "microcentury",

    "hzz2l2q_Resolved_13TeV_xs.txt": "microcentury",
    "hzz2l2q_Resolved_vbf_tagged_13TeV.txt": "microcentury",
    "hzz2l2q_Resolved_b_tagged_13TeV.txt": "microcentury",
    "hzz2l2q_Resolved_untagged_13TeV.txt": "microcentury",

    "hzz2l2q_eeqq_Merged_13TeV.txt": "espresso",
    "hzz2l2q_eeqq_Merged_b_tagged_13TeV.txt": "espresso",
    "hzz2l2q_eeqq_Merged_untagged_13TeV.txt": "espresso",
    "hzz2l2q_eeqq_Merged_vbf_tagged_13TeV.txt": "espresso",
    "hzz2l2q_eeqq_Resolved_13TeV.txt": "espresso",
    "hzz2l2q_eeqq_Resolved_b_tagged_13TeV.txt": "espresso",
    "hzz2l2q_eeqq_Resolved_untagged_13TeV.txt": "espresso",
    "hzz2l2q_eeqq_Resolved_vbf_tagged_13TeV.txt": "espresso",

    "hzz2l2q_mumuqq_Merged_13TeV.txt": "espresso",
    "hzz2l2q_mumuqq_Merged_b_tagged_13TeV.txt": "espresso",
    "hzz2l2q_mumuqq_Merged_untagged_13TeV.txt": "espresso",
    "hzz2l2q_mumuqq_Merged_vbf_tagged_13TeV.txt": "espresso",
    "hzz2l2q_mumuqq_Resolved_13TeV.txt": "espresso",
    "hzz2l2q_mumuqq_Resolved_b_tagged_13TeV.txt": "espresso",
    "hzz2l2q_mumuqq_Resolved_untagged_13TeV.txt": "espresso",
    "hzz2l2q_mumuqq_Resolved_vbf_tagged_13TeV.txt": "espresso",
}

# dict having the expected range for the limit plot corresponding to each datacard
# the range is defined as [min, max]
datacardList_limitRange = {
    "hzz2l2q_13TeV_xs.txt": [0.0001, 10000],
    "hzz2l2q_13TeV_xs_NoNuisance.txt": [0.0001, 1],

    "hzz2l2q_Merged_13TeV_xs.txt": [0.0001, 1.0],
    "hzz2l2q_Merged_vbf_tagged_13TeV.txt": [0.001, 10000.0],
    "hzz2l2q_Merged_b_tagged_13TeV.txt": [0.01, 1000.0],
    "hzz2l2q_Merged_untagged_13TeV.txt": [0.001, 1000.0],

    "hzz2l2q_Resolved_13TeV_xs.txt": [0.001, 500.0],
    "hzz2l2q_Resolved_vbf_tagged_13TeV.txt": [0.1, 500.0],
    "hzz2l2q_Resolved_b_tagged_13TeV.txt": [0.001, 500.0],
    "hzz2l2q_Resolved_untagged_13TeV.txt": [0.001, 500.0],

    "hzz2l2q_eeqq_Merged_13TeV.txt": [0.0001, 1.0],
    "hzz2l2q_eeqq_Merged_b_tagged_13TeV.txt": [0.01, 10000.0],
    "hzz2l2q_eeqq_Merged_untagged_13TeV.txt": [0.001, 1000.0],
    "hzz2l2q_eeqq_Merged_vbf_tagged_13TeV.txt": [0.01, 1000.0],
    "hzz2l2q_eeqq_Resolved_13TeV.txt": [0.001, 500.0],
    "hzz2l2q_eeqq_Resolved_b_tagged_13TeV.txt": [0.001, 500.0],
    "hzz2l2q_eeqq_Resolved_untagged_13TeV.txt": [0.001, 500.0],
    "hzz2l2q_eeqq_Resolved_vbf_tagged_13TeV.txt": [0.1, 1000.0],

    "hzz2l2q_mumuqq_Merged_13TeV.txt": [0.0001, 1.0],
    "hzz2l2q_mumuqq_Merged_b_tagged_13TeV.txt": [0.01, 10000.0],
    "hzz2l2q_mumuqq_Merged_untagged_13TeV.txt": [0.001, 10000.0],
    "hzz2l2q_mumuqq_Merged_vbf_tagged_13TeV.txt": [0.001, 100000.0],
    "hzz2l2q_mumuqq_Resolved_13TeV.txt": [0.001, 500.0],
    "hzz2l2q_mumuqq_Resolved_b_tagged_13TeV.txt": [0.01, 500.0],
    "hzz2l2q_mumuqq_Resolved_untagged_13TeV.txt": [0.001, 500.0],
    "hzz2l2q_mumuqq_Resolved_vbf_tagged_13TeV.txt": [0.1, 500.0],
}
