import os

def RunCommand(command):
    print("#"*11)
    print(command)
    os.system(command)
    print('')

def RemoveFile(FileName):
    if os.path.exists(FileName):
        os.remove(FileName)
    else:
        print("File, {}, does not exist".format(FileName))

def make_directory( sub_dir_name, verbose = True):
    if not os.path.exists(sub_dir_name):
        if verbose: print("{}{}\nCreate directory: {}".format('\t\n', '#'*51, sub_dir_name))
        os.makedirs(sub_dir_name)
    else:
        if verbose: print('Directory '+sub_dir_name+' already exists. Exiting...')
