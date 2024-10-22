#include <fstream>
#include <iostream>
#include <streambuf>
#include "TFile.h"
#include "RooWorkspace.h"

// void PrintWorkspaceToTextFile(const char *rootFilePath, const char *textFilePath)
void PrintWorkspaceToTextFile(const char *rootFilePath)
{

    // if .root not in the rootFilePath, add it
    TString fullRootFilePath = TString(rootFilePath);
    TString fulltextFilePath = TString("workspace_") + TString(rootFilePath) + (".txt");
    if (fullRootFilePath.EndsWith(".root") == false)
    {
        fullRootFilePath = TString("datacards_HIG_23_001/cards_2018_") + TString(fullRootFilePath) + "/HCG/1000/hzz2l2q_13TeV_xs.root";
        std::cout << "rootFilePath: " << fullRootFilePath << std::endl;
    }
    else
    {
        fullRootFilePath = TString(rootFilePath);
        fulltextFilePath = TString("workspace_output.txt");
    }

    // Open the ROOT file
    TFile *file = TFile::Open(fullRootFilePath);
    if (!file || file->IsZombie())
    {
        std::cerr << "Error opening file: " << rootFilePath << std::endl;
        return;
    }

    // Get the workspace from the file
    RooWorkspace *workspace = (RooWorkspace *)file->Get("w");
    if (!workspace)
    {
        std::cerr << "Workspace 'w' not found in the file." << std::endl;
        file->Close();
        return;
    }

    // Open a text file to redirect the output
    std::ofstream text_file(fulltextFilePath);
    if (!text_file.is_open())
    {
        std::cerr << "Error opening text file: " << fulltextFilePath << std::endl;
        file->Close();
        return;
    }

    // Backup the current buffer of std::cout
    std::streambuf *original_cout_buffer = std::cout.rdbuf();

    // Redirect std::cout to the text file
    std::cout.rdbuf(text_file.rdbuf());

    // Print the workspace content, output goes to the text file
    workspace->Print();

    // Restore the original std::cout buffer
    std::cout.rdbuf(original_cout_buffer);

    // Close the text file and the ROOT file
    text_file.close();
    file->Close();

    std::cout << "Workspace has been printed to: " << fulltextFilePath << std::endl;
}
