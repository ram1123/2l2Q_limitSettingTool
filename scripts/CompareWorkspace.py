import ROOT
import pandas as pd
import sys

def extract_pdfs_and_functions(workspace):
    """
    Extracts PDFs and functions from the RooWorkspace.
    Returns two dictionaries: one for PDFs and one for Functions.
    Each dictionary contains the names of the objects as keys and their parameter values as a list.
    """
    pdfs = {}
    functions = {}

    # Extract PDFs
    iter_pdfs = workspace.allPdfs().createIterator()
    pdf = iter_pdfs.Next()
    while pdf:
        # print("=="*20)
        # Store the PDF name and its parameters
        pdf_name = pdf.GetName()
        # print("==> PDF: ", pdf_name)

        params = pdf.getParameters(ROOT.RooArgSet())
        # print("==> Params: ", params)

        param_values = []
        for p in params:
            if isinstance(p, ROOT.RooRealVar):
                param_values.append((p.GetName(), p.getVal()))
            elif isinstance(p, ROOT.RooCategory):
                param_values.append((p.GetName(), p.getLabel()))  # Get label for RooCategory
            else:
                param_values.append((p.GetName(), "Unknown Type"))
        # pdfs[pdf_name] = param_values
        # print(f"PDF: {pdf_name} {param_values}")
        # print(f"pdf: {pdfs}")
        # print(f"evaluated_value: {evaluated_value}")
        # sys.exit()
        # param_values.append(evaluated_value)
        evaluated_value = pdf.getVal(ROOT.RooArgSet())
        param_values.append(("Evaluated Value", evaluated_value))  # Add evaluated value to the list
        pdfs[pdf_name] = param_values
        pdf = iter_pdfs.Next()


    # Extract Functions
    iter_funcs = workspace.allFunctions().createIterator()
    func = iter_funcs.Next()
    while func:
        # Store the function name and its parameters
        func_name = func.GetName()
        params = func.getParameters(ROOT.RooArgSet())
        param_values = []
        for p in params:
            if isinstance(p, ROOT.RooRealVar):
                param_values.append((p.GetName(), p.getVal()))
            elif isinstance(p, ROOT.RooCategory):
                param_values.append((p.GetName(), p.getLabel()))  # Get label for RooCategory
            else:
                param_values.append((p.GetName(), "Unknown Type"))
        # functions[func_name] = param_values
        evaluated_value = func.getVal(ROOT.RooArgSet())
        param_values.append(("Evaluated Value", evaluated_value))  # Add evaluated value to the list
        functions[func_name] = param_values

        # add the value of the function
        # functions[func_name].append(func.getVal(ROOT.RooArgSet()))

        func = iter_funcs.Next()

    return pdfs, functions

def compare_pdfs_and_functions(pdfs1, pdfs2, functions1, functions2):
    """
    Compare the PDFs and Functions between two workspaces.
    Compare the evaluated values and parameter values, and output the differences.
    """
    comparison_data = []

    # Compare PDFs
    all_pdfs = set(pdfs1.keys()).union(set(pdfs2.keys()))  # Handle PDFs that exist in only one workspace
    for pdf_name in all_pdfs:
        params1 = pdfs1.get(pdf_name, ["Missing in Workspace 1"])
        params2 = pdfs2.get(pdf_name, ["Missing in Workspace 2"])

        # Get the evaluated values for each workspace
        eval_value1 = [p[1] for p in params1 if p[0] == "Evaluated Value"]
        eval_value2 = [p[1] for p in params2 if p[0] == "Evaluated Value"]

        # If both evaluated values are present, compute the difference
        if eval_value1 and eval_value2:
            diff = eval_value2[0] - eval_value1[0]
        else:
            diff = "N/A"

        comparison_data.append([
            f"PDF: {pdf_name}",
            params1,
            params2,
            f"{eval_value1[0]:.5f}" if eval_value1 else "Missing",
            f"{eval_value2[0]:.5f}" if eval_value2 else "Missing",
            f"{diff:.5f}" if isinstance(diff, (float, int)) else diff
        ])

    # Compare Functions
    all_functions = set(functions1.keys()).union(set(functions2.keys()))  # Handle functions that exist in only one workspace
    for func_name in all_functions:
        params1 = functions1.get(func_name, ["Missing in Workspace 1"])
        params2 = functions2.get(func_name, ["Missing in Workspace 2"])

        # Get the evaluated values for each workspace
        eval_value1 = [p[1] for p in params1 if p[0] == "Evaluated Value"]
        eval_value2 = [p[1] for p in params2 if p[0] == "Evaluated Value"]

        # If both evaluated values are present, compute the difference
        if eval_value1 and eval_value2:
            diff = eval_value2[0] - eval_value1[0]
        else:
            diff = "N/A"

        comparison_data.append([
            f"Function: {func_name}",
            params1,
            params2,
            f"{eval_value1[0]:.5f}" if eval_value1 else "Missing",
            f"{eval_value2[0]:.5f}" if eval_value2 else "Missing",
            f"{diff:.5f}" if isinstance(diff, (float, int)) else diff
        ])

    # Convert the comparison data into a DataFrame
    df = pd.DataFrame(comparison_data, columns=[
        "Object",
        "Workspace 1 Parameters",
        "Workspace 2 Parameters",
        "Workspace 1 Evaluated Value",
        "Workspace 2 Evaluated Value",
        "Difference"
    ])

    return df

def compare_pdfs_and_functions_old(pdfs1, pdfs2, functions1, functions2):
    """
    Compare the PDFs and Functions between two workspaces.
    Returns a summary DataFrame with the differences.
    """
    comparison_data = []

    # Compare PDFs
    all_pdfs = set(pdfs1.keys()).union(set(pdfs2.keys()))  # Handle PDFs that exist in only one workspace
    for pdf_name in all_pdfs:
        params1 = pdfs1.get(pdf_name, ["Missing in Workspace 1"])
        params2 = pdfs2.get(pdf_name, ["Missing in Workspace 2"])

        for p1, p2 in zip(params1, params2):
            param_name1, val1 = p1 if isinstance(p1, tuple) else (p1, None)
            param_name2, val2 = p2 if isinstance(p2, tuple) else (p2, None)
            comparison_data.append([
                f"PDF: {pdf_name}",
                params1, params2,
                val1 if val1 is not None else "N/A",
                val2 if val2 is not None else "N/A",
                # val2 - val1 if isinstance(val1, (float, int)) and isinstance(val2, (float, int)) else "N/A" upto 5 decimal places
                val2 - val1 if isinstance(val1, (float, int)) and isinstance(val2, (float, int)) else "N/A"
            ])
            print(f"PDF: {pdf_name} {params1} {params2} {val1} {val2} {val2 - val1 if isinstance(val1, (float, int)) and isinstance(val2, (float, int)) else 'N/A'}")

    # Compare Functions
    all_functions = set(functions1.keys()).union(set(functions2.keys()))  # Handle functions that exist in only one workspace
    for func_name in all_functions:
        params1 = functions1.get(func_name, ["Missing in Workspace 1"])
        params2 = functions2.get(func_name, ["Missing in Workspace 2"])

        for p1, p2 in zip(params1, params2):
            param_name1, val1 = p1 if isinstance(p1, tuple) else (p1, None)
            param_name2, val2 = p2 if isinstance(p2, tuple) else (p2, None)
            comparison_data.append([
                f"Function: {func_name}",
                params1, params2,
                val1 if val1 is not None else "N/A",
                val2 if val2 is not None else "N/A",
                val2 - val1 if isinstance(val1, (float, int)) and isinstance(val2, (float, int)) else "N/A"
            ])

    # Convert the comparison data into a DataFrame
    df = pd.DataFrame(comparison_data, columns=["Object", "Workspace 1 Parameters", "Workspace 2 Parameters", "Workspace 1 Value", "Workspace 2 Value", "Difference"])

    # # Compare PDFs
    # all_pdfs = set(pdfs1.keys()).union(set(pdfs2.keys()))  # Handle PDFs that exist in only one workspace
    # for pdf_name in all_pdfs:
    #     params1 = dict(pdfs1.get(pdf_name, []))
    #     params2 = dict(pdfs2.get(pdf_name, []))
    #     param_keys = set(params1.keys()).union(set(params2.keys()))

    #     for param_name in param_keys:
    #         val1 = params1.get(param_name, "Missing in Workspace 1")
    #         val2 = params2.get(param_name, "Missing in Workspace 2")
    #         if isinstance(val1, (float, int)) and isinstance(val2, (float, int)):
    #             diff = val2 - val1
    #         else:
    #             diff = "N/A"
    #         comparison_data.append([f"PDF: {pdf_name}", param_name, val1, val2, diff])

    # # Compare Functions
    # all_functions = set(functions1.keys()).union(set(functions2.keys()))  # Handle functions that exist in only one workspace
    # for func_name in all_functions:
    #     params1 = dict(functions1.get(func_name, []))
    #     params2 = dict(functions2.get(func_name, []))
    #     param_keys = set(params1.keys()).union(set(params2.keys()))

    #     for param_name in param_keys:
    #         val1 = params1.get(param_name, "Missing in Workspace 1")
    #         val2 = params2.get(param_name, "Missing in Workspace 2")
    #         if isinstance(val1, (float, int)) and isinstance(val2, (float, int)):
    #             diff = val2 - val1
    #         else:
    #             diff = "N/A"
    #         comparison_data.append([f"Function: {func_name}", param_name, val1, val2, diff])

    # # Convert the comparison data into a DataFrame
    # df = pd.DataFrame(comparison_data, columns=["Object", "Parameter", "Workspace 1 Value", "Workspace 2 Value", "Difference"])

    return df

def compare_workspace_files(file1_path, file2_path):
    """
    Compare two ROOT files containing RooWorkspace objects.
    """
    # Open the first ROOT file and extract the workspace
    file1 = ROOT.TFile.Open(file1_path)
    workspace1 = file1.Get("w")

    # Open the second ROOT file and extract the workspace
    file2 = ROOT.TFile.Open(file2_path)
    workspace2 = file2.Get("w")

    if not workspace1 or not workspace2:
        print("Error: Could not find workspace 'w' in one of the files.")
        return

    # Extract PDFs and functions from both workspaces
    print("Reading workspace from file: ", file1_path)
    pdfs1, functions1 = extract_pdfs_and_functions(workspace1)

    print("Reading workspace from file: ", file2_path)
    pdfs2, functions2 = extract_pdfs_and_functions(workspace2)

    # Compare PDFs and Functions
    comparison_df = compare_pdfs_and_functions(pdfs1, pdfs2, functions1, functions2)

    # Print the comparison in a table format
    if comparison_df.empty:
        print("No differences found between the PDFs and Functions in the two workspaces.")
    else:
        print("Comparison of PDFs and Functions:")
        # print(comparison_df.to_string(index=False))
        # Save the comparison to a CSV file
        comparison_df.to_csv("workspace_comparison.csv", index=False)
        # Save to CSV only those rows where the difference is not zero or N/A or missing values
        comparison_df[comparison_df["Difference"] != 0].to_csv("workspace_comparison_nonzero.csv", index=False)

    # Close the files
    file1.Close()
    file2.Close()

# Example usage:
# compare_workspace_files("workspace_v1.root", "workspace_v2.root")
compare_workspace_files("datacards_HIG_23_001/cards_2018_MainBr_TempOct16/HCG/1000/hzz2l2q_13TeV_xs.root", "datacards_HIG_23_001/cards_2018_DevUpdateSysFromJialin_Oct16/HCG/1000/hzz2l2q_13TeV_xs.root")
