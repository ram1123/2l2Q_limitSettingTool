## Summary of Signal Modeling and RooProdPdf Usage in DatacardClass

### Overview

The `datacardClass` in your code is responsible for creating datacards and workspaces used in high energy physics analyses, particularly for modeling the signal and background processes in the CMS experiment. This class integrates various components, such as histograms, probability density functions (PDFs), and systematic uncertainties, into a comprehensive framework for statistical analysis.

### Signal Modeling (Parameterization)

The final mass parameterization is built from efficiency, resolution, and a 2D conditional template:

$$ P(m_{2l2q}, \mathcal{D}_{bkg}^{kin}) = \epsilon(m_{2l2q}^{gen}) \times \mathcal{R}(m_{2l2q} | m_{2l2q}^{gen}) \times \mathcal{D}_{bkg}^{kin}(m_{2l2q}) $$

- **Efficiency and resolution** are obtained from full simulation.
- The **2D conditional** is built from \( \mathcal{D}_{zjj} \) and \( M_{2l2q} \).

### Key Reasons for Using `RooProdPdf`

1. **Combining Different PDFs**:
   - `RooProdPdf` allows for the combination of different PDFs describing different aspects of the data, such as mass distribution and kinematic discriminant variables.

2. **Conditional PDFs**:
   - Supports conditional PDFs, allowing for modeling the joint probability of multiple variables where some are conditioned on others.

3. **Modular PDF Construction**:
   - Facilitates building complex models in a modular fashion by combining separately defined PDFs.

### Implementation in `datacardClass`

#### Method: `getRooProdPDFofMorphedSignal`

This method combines the PDF for the mass distribution with the PDF for the discriminant variable using `RooProdPdf`.

```python
def getRooProdPDFofMorphedSignal(self, TString_sig, templateSigName):
    # Load and prepare signal templates

    sample_list = ["ggH", "VBF"]
    for sample in sample_list:
        if sample == "ggH":
            tag_temp = "ggH"
        elif sample == "VBF":
            tag_temp = "qqH"

        TemplateName = "sigTemplateMorphPdf_" + sample + "_" + TString_sig + "_" + str(self.year)
        name = "sigCB2d_{}_{}".format(tag_temp, self.year)

        self.rooProdPdf[name] = ROOT.RooProdPdf(
            name,
            name,
            ROOT.RooArgSet(self.signalCBs["signalCB_{}_{}".format(sample, self.channel)]),
            ROOT.RooFit.Conditional(
                ROOT.RooArgSet(self.rooVars[TemplateName]),
                ROOT.RooArgSet(self.rooVars["D"]),
            ),
        )

        # Import the combined PDF into the workspace
        getattr(self.workspace, "import")(self.rooProdPdf[name], ROOT.RooFit.RecycleConflictNodes())
```

- **Inputs**:
  - `self.signalCBs["signalCB_{}_{}".format(sample, self.channel)]`: Mass distribution for the signal process.
  - `self.rooVars[TemplateName]`: PDF for the discriminant variable `D`.
  - `ROOT.RooFit.Conditional`: Specifies that the discriminant variable `D` is conditioned on the mass variable.

#### Method: `getRooProdPDFofMorphedBackgrounds`

This method combines the background histograms with the PDF for the discriminant variable using `RooProdPdf`.

```python
def getRooProdPDFofMorphedBackgrounds(self):
    background_list = ["vz", "ttbar", "zjets"]
    for process in background_list:
        vzTemplateName = "{}_{}_{}".format(process, self.appendName, self.year)
        vzTemplateMVV = self.background_hists["{}_template".format(process.replace("zjets", "zjet"))]

        self.rooDataHist[vzTemplateName] = ROOT.RooDataHist(
            vzTemplateName.replace("zjets", "zjet"),
            vzTemplateName.replace("zjets", "zjet"),
            ROOT.RooArgList(self.zz2l2q_mass),
            vzTemplateMVV,
        )

        vzTemplatePdfName = "{}Pdf".format(vzTemplateName.replace("zjets", "zjet"))
        self.rooDataHist[vzTemplatePdfName] = ROOT.RooHistPdf(
            vzTemplatePdfName,
            vzTemplatePdfName,
            ROOT.RooArgSet(self.zz2l2q_mass),
            self.rooDataHist[vzTemplateName],
        )

        TemplateName = "bkgTemplateMorphPdf_{}_{}_{}".format(process, self.jetType, self.year)
        self.rooVars[TemplateName] = ROOT.FastVerticalInterpHistPdf2D(
            TemplateName,
            TemplateName,
            self.zz2l2q_mass,
            self.rooVars["D"],
            True,
            self.rooArgSets["funcList_zjets"],
            self.rooArgSets["morphVarListBkg"],
            1.0,
            1,
        )

        name = "bkg2d_{}_{}".format(process, self.year)
        self.rooProdPdf[name] = ROOT.RooProdPdf(
            name,
            name,
            ROOT.RooArgSet(self.rooDataHist["{}Pdf".format(vzTemplateName.replace("zjets", "zjet"))]),
            ROOT.RooFit.Conditional(
                ROOT.RooArgSet(self.rooVars[
                    "bkgTemplateMorphPdf_{}_{}_{}".format(process, self.jetType, self.year)
                ]),
                ROOT.RooArgSet(self.rooVars["D"]),
            ),
        )

        # Import the combined PDF into the workspace
        getattr(self.workspace, "import")(self.rooProdPdf[name], ROOT.RooFit.RecycleConflictNodes())
```

- **Inputs**:
  - `self.rooDataHist[vzTemplateName]`: Histogram for the background process.
  - `self.rooVars[TemplateName]`: PDF for the discriminant variable `D`.
  - `ROOT.RooFit.Conditional`: Specifies that the discriminant variable `D` is conditioned on the mass variable.

### Summary

`RooProdPdf` is essential for combining different aspects of the signal and background models, such as the mass distribution and discriminant variables, into a single PDF. This approach ensures a comprehensive and accurate modeling of the data by taking into account multiple dimensions and their interdependencies.
