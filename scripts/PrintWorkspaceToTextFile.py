import ROOT

def PrintWorkspaceToTextFile(rootFilePath, textFilePath):
    # Open the ROOT file
    file = ROOT.TFile.Open(rootFilePath)
    if not file or file.IsZombie():
        print(f"Error opening file: {rootFilePath}")
        return

    # Get the workspace from the file
    workspace = file.Get("w")
    if not workspace:
        print("Workspace 'w' not found in the file.")
        file.Close()
        return

    # Use std::ofstream to write the output directly to the text file
    text_file = ROOT.std.ofstream(textFilePath)

    # Print the workspace content directly into the output stream (text file)
    workspace.Print("", text_file)

    # Close the ROOT file and the output file stream
    text_file.close()
    file.Close()

    print(f"Workspace has been printed to: {textFilePath}")

# Example usage:
# PrintWorkspaceToTextFile("hzz2l2q_13TeV_xs.root", "workspace_output.txt")
# Example usage:
PrintWorkspaceToTextFile("/afs/cern.ch/work/r/rasharma/h2l2Q/EL7_Container/Limit_Extraction_FW/CMSSW_11_3_4/src/2l2Q_limitSettingTool/datacards_HIG_23_001/cards_2018_NewDefault_09Oct2024/HCG/1000/hzz2l2q_13TeV_xs.root", "workspace_output.txt")
