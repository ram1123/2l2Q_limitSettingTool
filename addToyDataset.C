void addToyDataset(const char * toyFileName, const char * toyName, const char* outputFileName) {
  gSystem->Load("libHiggsAnalysisCombinedLimit.so");

  // the workspace with the required POIs
  //TFile workspace(toyFileName);
  //RooWorkspace * myWS = workspace.Get("w");

  // the file with the toy 
  TFile fileWithToy(toyFileName);
  RooAbsData * toyDataset = (RooAbsData *) fileWithToy.Get(Form("toys/%s",toyName));

  if (!toyDataset) {
    cout << "Error: toyDataset " << Form("toys/%s",toyName)
         << " not found in file " << toyFileName << endl;
    return;
  }
  toyDataset->SetName(Form("%s",toyName));
  //toyDataset->SetName("data_obs");
  // import (the two for completness
  TFile workspace(outputFileName);
  RooWorkspace * newWS = workspace.Get("w");  


  RooRealVar* m = newWS->var("CMS_zz4l_mass");
  RooCategory* c = newWS->cat("CMS_channel");
  newWS->import(*toyDataset->reduce(RooArgSet(*m,*c)));
  // write on a new workspace file
  newWS->writeToFile(outputFileName);
}

