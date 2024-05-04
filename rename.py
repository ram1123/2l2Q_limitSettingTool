import os

# 设置文件夹路径
folder_path = '/afs/cern.ch/work/g/guoj/Combine/CMSSW_11_3_4/src/2l2Q_limitSettingTool/datacards_HIG_23_001/cards_run2_deepjet_fracvbf0_fVBF0.0/figs/impacts'  # 替换为您的文件夹路径

# 遍历文件夹
for filename in os.listdir(folder_path):
    if "26feb" in filename and filename.endswith('.pdf'):
        # 构建新文件名
        new_filename = filename.replace("26feb_blind_SBHypothesis_", "24may_blind_")
        # 构建完整的文件路径
        old_file = os.path.join(folder_path, filename)
        new_file = os.path.join(folder_path, new_filename)
        # 重命名文件
        os.rename(old_file, new_file)
        print(f"Renamed '{filename}' to '{new_filename}'")
