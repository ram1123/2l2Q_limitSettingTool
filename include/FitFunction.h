#ifndef FITFUNCTION_H
#define FITFUNCTION_H


#include <iostream>
#include <cstdlib>
#include <cmath>
#include <fstream>
#include <string>

#include "TROOT.h"
#include "TF1.h"
#include "TGraph.h"
#include "TCanvas.h"



class FitFunction
{

 public:

  FitFunction();
  ~FitFunction();

 double fitFunction(double* x_arr, double* par);

 double getVal(double x, double p0, double p1, double p2, double p3, double p4, double p5, double p6);

 private:

  std::string fileName;

};

#endif
