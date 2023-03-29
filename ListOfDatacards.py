datacardList = [
    "hzz2l2q_13TeV_xs.txt",
    "hzz2l2q_13TeV_xs_NoNuisance.txt",

    "hzz2l2q_Merged_13TeV_xs.txt",
    # "hzz2l2q_Merged_vbf_tagged_13TeV.txt",
    # "hzz2l2q_Merged_b_tagged_13TeV.txt",
    # "hzz2l2q_Merged_untagged_13TeV.txt",

    "hzz2l2q_Resolved_13TeV_xs.txt",
    # "hzz2l2q_Resolved_vbf_tagged_13TeV.txt",
    # "hzz2l2q_Resolved_b_tagged_13TeV.txt",
    # "hzz2l2q_Resolved_untagged_13TeV.txt",

    "hzz2l2q_eeqq_Merged_13TeV.txt",
    # "hzz2l2q_eeqq_Merged_b_tagged_13TeV.txt",
    # "hzz2l2q_eeqq_Merged_untagged_13TeV.txt",
    # "hzz2l2q_eeqq_Merged_vbf_tagged_13TeV.txt",
    "hzz2l2q_eeqq_Resolved_13TeV.txt",
    # "hzz2l2q_eeqq_Resolved_b_tagged_13TeV.txt",
    # "hzz2l2q_eeqq_Resolved_untagged_13TeV.txt",
    # "hzz2l2q_eeqq_Resolved_vbf_tagged_13TeV.txt",

    "hzz2l2q_mumuqq_Merged_13TeV.txt",
    # "hzz2l2q_mumuqq_Merged_b_tagged_13TeV.txt",
    # "hzz2l2q_mumuqq_Merged_untagged_13TeV.txt",
    # "hzz2l2q_mumuqq_Merged_vbf_tagged_13TeV.txt",
    "hzz2l2q_mumuqq_Resolved_13TeV.txt",
    # "hzz2l2q_mumuqq_Resolved_b_tagged_13TeV.txt",
    # "hzz2l2q_mumuqq_Resolved_untagged_13TeV.txt",
    # "hzz2l2q_mumuqq_Resolved_vbf_tagged_13TeV.txt"
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
    "hzz2l2q_13TeV_xs.txt": "longlunch",
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
