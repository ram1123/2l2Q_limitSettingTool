from utils import *
import ROOT

def check_object_validity(obj, name):
    if obj:
        logger.debug("{} is valid".format(name))
    else:
        logger.error("{} is invalid".format(name))
        raise ValueError("{} is invalid".format(name))

def getTH1F(name, fs = None, category = None):
    # FIXME: I should use member variables (fs) instead of passing them as arguments
    histName = None
    if fs is None and category is None:
        histName = name
    else:
        histName = name + "_" + fs + "_" + category
    logger.debug("histName: {}".format(histName))
    hist = ROOT.TH1F(histName, histName, self.bins, self.low_M, self.high_M)
    return hist

def save_histograms(hist, template = None, output_file_name = None):
    c1 = ROOT.TCanvas("c1", "c1", 800, 800)
    hist.SetLineColor(ROOT.kRed)
    hist.SetMarkerColor(ROOT.kRed)
    hist.Draw()

    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend.AddEntry(hist, "smoothed", "l")

    if template is not None:
        template.SetLineColor(ROOT.kBlue)
        template.SetMarkerColor(ROOT.kBlue)
        template.Draw("same")
        legend.AddEntry(template, "template", "l")

    legend.Draw()
    if output_file_name is None:
        output_file_name = hist.GetName() + ".png"
    c1.SaveAs(output_file_name)
    c1.SetLogy()
    c1.SaveAs(output_file_name.replace(".png", "_log.png"))

def get_histogram(file, hist_name):
    hist = file.Get(hist_name)
    if not hist:
        logger.error("Histogram not found: {}".format(hist_name))
        raise LookupError("Histogram not found: {}".format(hist_name))
    return hist

def create_up_down_hist(hist):
    # list of histograms, one for each bin
    up_hist_list = []
    down_hist_list = []

    for i in range(0, hist.GetNbinsX()):
        if hist.GetBinContent(i) < 1:
            up_hist = hist.Clone()
            down_hist = hist.Clone()
            up_hist.SetName(hist.GetName() + "_" + str(i)+ "_up")
            up_hist.SetTitle(hist.GetTitle() + "_" + str(i)+ "_up")
            down_hist.SetName(hist.GetName() + "_" + str(i)+ "_down")
            down_hist.SetTitle(hist.GetTitle() + "_" + str(i)+ "_down")

            if hist.GetBinContent(i) == 0.0:
                up_hist.SetBinContent(i, 0.000001)
                down_hist.SetBinContent(i, 0)
            else:
                up_hist.SetBinContent(i, hist.GetBinContent(i) + hist.GetBinErrorUp(i))
                down_hist.SetBinContent(i, max(0.0, hist.GetBinContent(i) - hist.GetBinErrorLow(i)))

            up_hist_list.append(up_hist)
            down_hist_list.append(down_hist)

    return up_hist_list, down_hist_list

def plot_rooDataHist(data_list, mass_var):
    """
    Plot a list of RooDataHist objects on a frame and save the plot as a PNG and PDF file.

    Parameters:
    data_list (list): A list of RooDataHist objects to plot.
    mass_var (RooRealVar): The mass variable for the x-axis of the plot.
    """
    canvas = ROOT.TCanvas("canvas", "canvas", 800, 800)
    canvas.cd()
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)

    # Create a frame for the plot
    # frame = mass_var.frame(ROOT.RooFit.Range(self.low_M, self.high_M))
    # low, high = mass_var.getRange("fullsignalrange")
    # print("low, high: {}, {}".format(low, high))
    low, high = 0.0, 4000.0
    frame = mass_var.frame(ROOT.RooFit.Range(low, high))

    # Plot each data histogram on the frame and add it to the legend
    for i, data_hist in enumerate(data_list):
        data_hist.plotOn(
            frame,
            ROOT.RooFit.MarkerColor(i + 1),
            ROOT.RooFit.LineColor(i + 1),
            ROOT.RooFit.Name(data_hist.GetName()),
        )
        legend.AddEntry(data_hist, data_hist.GetName(), "l")

    frame.Draw()
    legend.Draw()

    # Save the plot as a PNG and PDF file
    # fig_name = "{0}/figs/mzz_mH{1}_{2}_{3}".format(
    # self.outputDir, self.mH, self.year, self.appendName
    # )
    fig_name = "mzz_mH{0}_{1}".format(mass_var.getVal(), mass_var.GetName())
    canvas.SaveAs(fig_name + ".png")
    # canvas.SaveAs(fig_name + ".pdf")

    # Also save a logY version of the plot
    frame.SetMinimum(0.00001)
    canvas.SetLogy()
    canvas.SaveAs(fig_name + "_logY.png")
    canvas.SaveAs(fig_name + "_logY.pdf")
    del canvas

def plot_and_save(data_hist, pdf, zz2l2q_mass, key, outputDir):
    """
    Plot the RooDataHist and RooHistPdf and save the plot as a PNG file.

    Parameters:
        data_hist (ROOT.RooDataHist): The data histogram to plot.
        pdf (ROOT.RooHistPdf): The PDF to plot.
        key (str): A key to uniquely identify the histogram and PDF.
    """
    # Create a RooPlot object for the zz2l2q_mass range
    frame = zz2l2q_mass.frame(
        ROOT.RooFit.Title("Plot of Data and PDF for {}".format(key))
    )

    # Plot the data histogram on the frame
    data_hist.plotOn(
        frame, ROOT.RooFit.MarkerColor(ROOT.kBlue), ROOT.RooFit.Name("data")
    )

    # Plot the PDF on the same frame
    pdf.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.Name("pdf"))

    # Create a canvas to draw the plot
    canvas = ROOT.TCanvas(
        "canvas_{}".format(key), "Canvas for {}".format(key), 800, 600
    )
    frame.Draw()  # Draw the frame on the canvas

    # Save the canvas as a PNG file
    canvas.SaveAs("{}/figs/plot_{}.png".format(outputDir, key))

    # set minimum and maximum y-axis values
    frame.SetMinimum(0.0001)
    canvas.SetLogy()
    canvas.SaveAs("{}/figs/plot_{}_logY.png".format(outputDir, key))

    # Clean up to prevent memory issues
    del canvas, frame
