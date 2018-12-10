"""Allow users to implement their analysis in a notebook."""
import os
import json

def get_source(
        notebook_path,
        save=False,
        filename=""):
    """Get source code from a python notebook.
    Parameters
    -------------
    notebook_path :: String #path to the python notebook (.ipynb file.)
    save :: Boolean # if the source code should be saved to disk
    filename :: String # file to be saved to
    ~                  # if not provided, notebook's name will be used
    ~                  #(.py instead of of .ipynb)
    Returns
    -------------
    String # source code from the python notebook,
    """
    with open(
            notebook_path,
            'r') as notebook:
        notebook_content=\
            json.load(
                notebook)
    cell_sources=[
        cell.get("source", "")
        for cell in notebook_content.get("cells", [])
        if cell.get("cell_type", "") == "code"]
    source=\
        "\n\n".join([
            "".join(
                source_lines)
            for source_lins in cell_sources])
    if save:
        filename=\
            filename if filename else\
            "{}.py".format('.'.split(notebook_path)[0])
        output_dir=\
            
        with open(
                os.path.join(
                    os.path.dirname(
                        notebook_path),
                    filename),
                'w') as output_file:
            output_file.write(source)

    return source
        
        

