import subprocess


def create_custom_dot_file(original_dot_file, custom_dot_file):
    with open(original_dot_file, "r") as original, open(custom_dot_file, "w") as custom:
        custom.write("digraph G {\n")
        # rankdir=LR; # Left to right
        # custom.write("    rankdir=LR;\n")
        # custom.write("    ratio=fill;\n")  # Use splines
        custom.write('    size="10,150!";\n')  # Increase the page size
        custom.write("    node [shape=box, fontsize=12, width=1];\n") # Increase node size
        custom.write("    edge [fontsize=12];\n")
        custom.write("    dpi=1300;\n")
        custom.write("    splines=true;\n")
        custom.write("    sep=0.1;\n")
        # custom.write("    nodesep=0.1;\n")
        # custom.write("    ranksep=0.1;\n")
        custom.write("    ranksep=2.0;\n")  # Increase rank separation
        custom.write("    nodesep=1.0;\n")  # Increase node separation
        custom.write("    overlap=prism;\n")  # Handle overlap better other options: false, compress, scale, prism
        for line in original:
            if line.strip() and not line.strip().startswith("digraph G {"):
                custom.write(line)
        # custom.write("}\n")


def convert_dot_to_pdf(dot_file, output_pdf, use_sfdp=False):
    """Convert a .dot file to .pdf using an intermediate PostScript file."""
    ps_file = dot_file.replace(".dot", ".ps")
    command = (
        ["sfdp", "-Gsize=50,50!", "-Gdpi=300", "-Tps", dot_file, "-o", ps_file]
        if use_sfdp
        else ["dot", "-Gsize=50,50!", "-Gdpi=300", "-Tps", dot_file, "-o", ps_file]
    )

    try:
        subprocess.run(command, check=True)
        print("Successfully converted .dot to .ps with custom size and DPI")
    except subprocess.CalledProcessError as e:
        print("Failed to convert .dot to .ps: {}".format(e))
        return

    try:
        subprocess.run(["ps2pdf", ps_file, output_pdf], check=True)
        print("Successfully converted .ps to .pdf")
    except subprocess.CalledProcessError as e:
        print("Failed to convert .ps to .pdf: {}".format(e))


# Example usage
original_dot_file = "datacards_HIG_23_001/cards_2018_new/HCG/1000/model_mumuqq_Merged_b_tagged_13TeV.dot"
custom_dot_file = "custom_model.dot"
output_pdf = "custom_model.pdf"

create_custom_dot_file(original_dot_file, custom_dot_file)
convert_dot_to_pdf(custom_dot_file, output_pdf, use_sfdp=False)
