#include <iostream>
#include <iomanip>
#include <cmath>
#include <string>
#include <vector>
#include <fstream>
#include <cstdlib>
#include "TMatrixD.h"
#include "TVectorD.h"
#include "TFile.h"
#include "TTree.h"
#include "TChain.h"
#include "TString.h"
#include "TMath.h"
#include "TSystem.h"
#include "TGraphErrors.h"
#include "TGraphAsymmErrors.h"
#include "TSpline.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TH3F.h"
#include "TVirtualFitter.h"
#include "TMinuit.h"
#include "TF1.h"
#include "TPaveText.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TColor.h"
#include "TDirectory.h"
#include "RooRealVar.h"
#include "RooPlot.h"
#include "RooArgList.h"
#include "RooTFnBinding.h"

using namespace std;


#ifndef __CINT__
#include "RooGlobalFunc.h"
#endif
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "RooGaussian.h"
#include "TCanvas.h"
#include "RooPlot.h"
#include "TAxis.h"
using namespace RooFit;

#include "FitFunction.h"

FitFunction::FitFunction(){

}

FitFunction::~FitFunction(){

}


double FitFunction::getVal(double x, double par0, double par1, double par2, double par3, double par4, double par5, double par6){


       double* x_arr; double * par;
       x_arr[0] = x;
       par[0] = par0; par[1] = par[1]; par[2] = par2; 
       par[3] = par3; par[4] = par4; par[5] = par5; par[6] = par6;

       return fitFunction(x_arr, par);

}

double FitFunction::fitFunction(double* x_arr, double* par){
  const double d_epsilon = 1e-14;
  double x = x_arr[0];

  // If we say the form of the polynomial is [0] + [1]*x + [2]*x2 + [3]*x3 + [4]*x4...,
  // use the highest two orders for matching at the nodes and free the rest.
  const int nfcn=3;
//  const int nfcn=2;
  const int polyndof=3/*5*/; // Change this to 4 for a cubic if you want.

  // Do not touch!
  const int nnodes=nfcn-1; // How many nodes are in between
  const int ndof_endfcn = polyndof-1; // 2: 1 degree for the function value
  const int ndof_middlefcn = polyndof-2; // +1 for slope of the other node
  int npars_reduced[nfcn];
  for (int index=0; index<nfcn; index++){
    if (index==0 || index==nfcn-1) npars_reduced[index] = ndof_endfcn;
    else npars_reduced[index] = ndof_middlefcn;
  }

  double node[nnodes]; // First [0,...,nnodes-1] parameters are nodes
  double pars_full[nfcn][polyndof]={ { 0 } }; // The full coefficients array

  for (int ip=0; ip<nnodes; ip++){
    node[ip] = par[ip];
  }
  // Check for the nodes to be consecutive
  for (int ip=0; ip<nnodes; ip++){
    for (int ip2=ip+1; ip2<nnodes; ip2++){
      if (node[ip]>node[ip2]) return d_epsilon;
    }
  }
  int pos_ctr = nnodes;
  for (int index=0; index<nfcn; index++){
    for (int ipar=0; ipar<npars_reduced[index]; ipar++){
//    pars_full[index][ipar] = par[pos_ctr];
      if (!(index==(nfcn-1) && ipar==(npars_reduced[index]-1))) pars_full[index][ipar] = par[pos_ctr];
      else pars_full[index][ipar+1] = par[pos_ctr]; // Special case to avoid singular matrix. This corresponds to having the x^n contribution free instead of x^(n-1)
      pos_ctr++;
    }
  }

  double xton[nnodes][polyndof]; // Array of node^power
  double nxtom[nnodes][polyndof]={ 0 }; // Array of power*node^(power-1)
  for (int inode=0; inode<nnodes; inode++){
    for (int ipow=0; ipow<polyndof; ipow++){
      if (ipow==0) xton[inode][ipow]=1; // nxtom==0
      else if (ipow==1){
        xton[inode][ipow]=node[inode];
        nxtom[inode][ipow]=1;
      }
      else{
        xton[inode][ipow]=pow(node[inode], ipow);
        nxtom[inode][ipow]=((double)ipow)*pow(node[inode], ipow-1);
      }
    }
  }

  double ysbar_nodes[2*nnodes]={ 0 };
  double coeff_ysbar[2*nnodes][2*nnodes]={ { 0 } };
  int cstart=-1;
  for (int inode=0; inode<nnodes; inode++){
    int i=inode;
    int j=i+1;
    double sign_i = 1, sign_j=-1;
    for (int ip=0; ip<npars_reduced[i]; ip++){
      ysbar_nodes[inode] += sign_i*pars_full[i][ip]*xton[inode][ip];
      ysbar_nodes[nnodes+inode] += sign_i*pars_full[i][ip]*nxtom[inode][ip];
    }
    for (int ip=0; ip<npars_reduced[j]; ip++){
      if (!(j==(nfcn-1) && ip==(npars_reduced[j]-1))){
        ysbar_nodes[inode] += sign_j*pars_full[j][ip]*xton[inode][ip];
        ysbar_nodes[nnodes+inode] += sign_j*pars_full[j][ip]*nxtom[inode][ip];
      }
      else{
        ysbar_nodes[inode] += sign_j*pars_full[j][ip+1]*xton[inode][ip+1];
        ysbar_nodes[nnodes+inode] += sign_j*pars_full[j][ip+1]*nxtom[inode][ip+1];
      }
    }

    if (cstart>=0){
      coeff_ysbar[inode][cstart] = -sign_i*xton[inode][polyndof-2];
      coeff_ysbar[nnodes + inode][cstart] = -sign_i*nxtom[inode][polyndof-2];
    }
    coeff_ysbar[inode][cstart+1] = -sign_i*xton[inode][polyndof-1];
    coeff_ysbar[nnodes + inode][cstart+1] = -sign_i*nxtom[inode][polyndof-1];
    coeff_ysbar[inode][cstart+2] = -sign_j*xton[inode][polyndof-2];
    coeff_ysbar[nnodes + inode][cstart+2] = -sign_j*nxtom[inode][polyndof-2];
    if ((cstart+3)<2*nnodes){
      coeff_ysbar[inode][cstart+3] = -sign_j*xton[inode][polyndof-1];
      coeff_ysbar[nnodes + inode][cstart+3] = -sign_j*nxtom[inode][polyndof-1];
    }
    cstart+=2;
  }

  TVectorD polyvec(2*nnodes, ysbar_nodes);
  TMatrixD polycoeff(2*nnodes, 2*nnodes);
  polycoeff.SetMatrixArray(*coeff_ysbar);
  double testdet=0;
  TMatrixD polycoeff_inv = polycoeff.Invert(&testdet);
  if (testdet!=0){
    TVectorD unknowncoeffs = polycoeff_inv*polyvec;
    pos_ctr=0;
    for (int index=0; index<nfcn; index++){
      for (int ip=npars_reduced[index]; ip<polyndof; ip++){
        if (!(index==(nfcn-1) && ip==npars_reduced[index])) pars_full[index][ip] = unknowncoeffs[pos_ctr];
        else pars_full[index][ip-1] = unknowncoeffs[pos_ctr];
        pos_ctr++;
      }
    }

    int index_chosen=0;
    for (int index=0; index<nnodes-1; index++){
      if (x>=node[index] && x<node[index+1]){
        index_chosen = index+1;
        break;
      }
    }
    if (x>=node[nnodes-1]) index_chosen = nfcn-1;

    double res = 0;
    for (int ip=0; ip<polyndof; ip++) res += pars_full[index_chosen][ip]*pow(x, ip);
    return res;
  }
  else{
    cerr << "Something went wrong, and the determinant is 0!" << endl;
    return d_epsilon;
  }
}

