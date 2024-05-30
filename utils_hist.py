from utils import *
import ROOT
from array import array

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


def smooth_histogram(hist, kernel_width=-1):
    """
    Reference: https://roottalk.root.cern.narkive.com/lbhgatd8/spline-from-histogram-with-missing-bins
    Smooth a ROOT TH1F histogram using a Gaussian kernel.

    Parameters:
    hist (TH1F): The input histogram to be smoothed.
    kernel_width (float): The width of the Gaussian kernel. If set to less than 1, defaults to the bin width of the histogram.

    Returns:
    TH1F: A new histogram with smoothed values.
    """
    if kernel_width < 1:
        kernel_width = hist.GetBinWidth(1)

    nbins = hist.GetNbinsX()
    xmin = hist.GetXaxis().GetXmin()
    xmax = hist.GetXaxis().GetXmax()

    smooth_hist = ROOT.TH1F("{}_smooth".format(hist.GetName()), hist.GetTitle(), nbins, xmin, xmax)

    # print("name: ", hist.GetName())

    for bin in range(1, nbins + 1):
        x = hist.GetBinCenter(bin)
        # continue if the x range is less than 200 GeV
        # if x < 200 and "merged" in hist.GetName():
        #     continue

        # continue if there is no entry in the bin below 500 GeV
        if x < 500 and hist.GetBinContent(bin) == 0:
            continue
        sumw = 0
        sumwy = 0

        for i in range(1, nbins + 1):
            y_i = hist.GetBinContent(i)
            x_i = hist.GetBinCenter(i)

            if y_i == 0:
                continue

            w_i = ROOT.TMath.Gaus((x - x_i) / kernel_width)
            sumw += w_i
            sumwy += w_i * y_i

        smooth_value = sumwy / sumw if sumw != 0 else 0
        smooth_hist.SetBinContent(bin, smooth_value)

    return smooth_hist


def smooth_histogram_with_tkde(hist):
    """
    Smooth a ROOT TH1F histogram using TKDE (Kernel Density Estimation).

    Parameters:
    hist (TH1F): The input histogram to be smoothed.

    Returns:
    TH1F: A new histogram with smoothed values.
    """
    # Get the bin centers and contents from the histogram
    x_values = []
    y_values = []

    for bin in range(1, hist.GetNbinsX() + 1):
        x = hist.GetBinCenter(bin)
        y = hist.GetBinContent(bin)
        if y ==0 and x < 500:
            continue
        x_values.append(x)
        y_values.append(y)

    # Create a TKDE object
    kde = ROOT.TKDE(len(x_values), array("d", x_values), array("d", y_values))

    # Get the smoothed function
    smooth_function = kde.GetFunction()

    # Create a new histogram for the smoothed values
    nbins = hist.GetNbinsX()
    xmin = hist.GetXaxis().GetXmin()
    xmax = hist.GetXaxis().GetXmax()
    smooth_hist = ROOT.TH1F("{}_smooth".format(hist.GetName()), hist.GetTitle(), nbins, xmin, xmax)

    # Fill the smoothed histogram using the KDE
    for bin in range(1, nbins + 1):
        x = hist.GetBinCenter(bin)
        y_smooth = smooth_function.Eval(x)
        smooth_hist.SetBinContent(bin, y_smooth)

    return smooth_hist


def save_histograms(hist1, hist2 = None, output_file_name = None, title1 = None, title2 = None):
    c1 = ROOT.TCanvas("c1", "c1", 800, 800)
    hist1.SetLineColor(ROOT.kRed)
    hist1.SetMarkerColor(ROOT.kRed)
    hist1.Draw()

    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    title_hist1 = hist1.GetTitle() if title1 is None else title1
    legend.AddEntry(hist1, title_hist1)

    if hist2 is not None:
        hist2.SetLineColor(ROOT.kBlue)
        hist2.SetMarkerColor(ROOT.kBlue)
        hist2.Draw("same")
        title_hist2 = hist2.GetTitle() if title2 is None else title2
        legend.AddEntry(hist2, title_hist2)

    #  check the maximum value of the histogram then set the y-axis range
    max_value = max(hist1.GetMaximum(), hist2.GetMaximum())
    hist1.SetMaximum(max_value * 1.2)
    legend.Draw()

    # Also add the integral of the histogram to the plot
    integral = hist1.Integral()
    integral_text = ROOT.TLatex(0.4, 0.6, "Integral ({}): {:.2f}".format(title_hist1, integral))
    integral_text.SetNDC()
    # set color to red
    integral_text.SetTextColor(ROOT.kRed)
    integral_text.Draw()

    integral_template = hist2.Integral()
    integral_text_template = ROOT.TLatex(0.4, 0.5, "Integral ({}): {:.2f}".format(title_hist2, integral_template))
    integral_text_template.SetNDC()
    integral_text_template.SetTextColor(ROOT.kBlue)
    integral_text_template.Draw()

    if output_file_name is None:
        output_file_name = hist1.GetName() + ".png"
    c1.SaveAs(output_file_name)
    c1.SetLogy()
    c1.SaveAs(output_file_name.replace(".png", "_log.png"))

def save_histograms_3(hist1, hist2, hist3, output_file_name = None, title1 = None, title2 = None, title3 = None):
    c1 = ROOT.TCanvas("c1", "c1", 800, 800)
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)

    hist1.SetLineColor(ROOT.kRed)
    hist1.SetMarkerColor(ROOT.kRed)
    hist1.Draw()

    title_hist1 = hist1.GetTitle() if title1 is None else title1
    legend.AddEntry(hist1, title_hist1)

    hist2.SetLineColor(ROOT.kBlue)
    hist2.SetMarkerColor(ROOT.kBlue)
    hist2.Draw("same")

    title_hist2 = hist2.GetTitle() if title2 is None else title2
    legend.AddEntry(hist2, title_hist2)

    hist3.SetLineColor(ROOT.kGreen)
    hist3.SetMarkerColor(ROOT.kGreen)
    hist3.Draw("same")

    title_hist3 = hist3.GetTitle() if title3 is None else title3
    legend.AddEntry(hist3, title_hist3)

    #  check the maximum value of the histogram then set the y-axis range
    max_value = max(hist1.GetMaximum(), hist2.GetMaximum(), hist3.GetMaximum())
    hist1.SetMaximum(max_value * 1.2)
    legend.Draw()

    # Also add the integral of the histogram to the plot
    integral = hist1.Integral()
    integral_text = ROOT.TLatex(0.4, 0.6, "Integral ({}): {:.2f}".format(title_hist1, integral))
    integral_text.SetNDC()
    # set color to red
    integral_text.SetTextColor(ROOT.kRed)
    integral_text.Draw()

    integral_template = hist2.Integral()
    integral_text_template = ROOT.TLatex(0.4, 0.5, "Integral ({}): {:.2f}".format(title_hist2, integral_template))
    integral_text_template.SetNDC()
    integral_text_template.SetTextColor(ROOT.kBlue)
    integral_text_template.Draw()

    integral_template2 = hist3.Integral()
    integral_text_template2 = ROOT.TLatex(0.4, 0.4, "Integral ({}): {:.2f}".format(title_hist3, integral_template2))
    integral_text_template2.SetNDC()
    integral_text_template2.SetTextColor(ROOT.kGreen)
    integral_text_template2.Draw()

    if output_file_name is None:
        output_file_name = hist1.GetName() + ".png"
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
