#include "RooWorkspace.h"
#include "RooPlot.h"
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "TCanvas.h"
#include "TFile.h"

void plotDataFromWorkspace() {

  // Open the ROOT file containing the workspace
  TFile* f = new TFile("datacards_HIG_23_001/cards_2018/HCG/1500/hzz2l2q_13TeV_xs.root");

  // Retrieve workspace from ROOT file
  RooWorkspace* ws = (RooWorkspace*) f->Get("w");

  // Retrieve the dataset from the workspace
  RooDataSet* data_obs = (RooDataSet*) ws->data("data_obs");

  // Create a canvas for the plots
  TCanvas* c1 = new TCanvas("c1","c1",800,600);
  c1->Divide(2,2);  // Create a 2x2 grid on the canvas

  // Plotting CMS_channel
  c1->cd(1);
  RooRealVar* CMS_channel = ws->var("CMS_channel");
  RooPlot* frame1 = CMS_channel->frame();
  data_obs->plotOn(frame1);
  frame1->Draw();

  // Plotting zz2l2q_mass
  c1->cd(2);
  RooRealVar* zz2l2q_mass = ws->var("zz2l2q_mass");
  RooPlot* frame2 = zz2l2q_mass->frame();
  data_obs->plotOn(frame2);
  frame2->Draw();

  // Plotting Dspin0
  c1->cd(3);
  RooRealVar* Dspin0 = ws->var("Dspin0");
  RooPlot* frame3 = Dspin0->frame();
  data_obs->plotOn(frame3);
  frame3->Draw();

  // Plotting zz2lJ_mass
  c1->cd(4);
  RooRealVar* zz2lJ_mass = ws->var("zz2lJ_mass");
  RooPlot* frame4 = zz2lJ_mass->frame();
  data_obs->plotOn(frame4);
  frame4->Draw();

  c1->Update();

  // Save the canvas to a file
  c1->SaveAs("data_obs_plots.png");

}

int main() {
  plotDataFromWorkspace();
  return 0;
}
