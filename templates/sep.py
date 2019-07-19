#!/usr/bin/env python3
import nbformat
import re
import sys

from copy import deepcopy

## Handle CLI
if len(sys.argv) == 1:
    print("Usage:")
    print("    ./sep.py [master.ipynb] (assignment.ipynb) (solution.ipynb)")
    print("Arguments")
    print("    master.ipynb     = name of master jupyter notebook file")
    print("Optional Arguments")
    print("    assignment.ipynb = name to write assignment")
    print("    solution.ipynb   = name to write solution")
    print("Note: If optional names not given, sep will first try to replace")
    print("      'master' with the strings 'assignment' and 'solution', and")
    print("      will post-fix if 'master' is not found")

else:
    # Handle command line arguments
    filename_orig = sys.argv[1]

    if len(sys.argv) > 2:
        filename_assignment = sys.argv[2]
    else:
        ## Replace 'master' if possible
        if filename_orig.find("master") > -1:
            filename_assignment = filename_orig.replace("master", "assignment")
        ## Post-fix if 'master' not found
        else:
            filename_assignment = filename_orig.replace(
                ".ipynb",
                "_assignment.ipynb"
            )

    if len(sys.argv) > 3:
        filename_solution = sys.argv[3]
    else:
        ## Replace 'master' if possible
        if filename_orig.find("master") > -1:
            filename_solution = filename_orig.replace("master", "solution")
        ## Post-fix if 'master' not found
        else:
            filename_solution = filename_orig.replace(
                ".ipynb",
                "_solution.ipynb"
            )

## Load the notebook
nb_orig       = nbformat.read(filename_orig, as_version = 3)
nb_assignment = deepcopy(nb_orig)
nb_solution   = deepcopy(nb_orig)

for id_worksheet in range(len(nb_orig["worksheets"])):
    worksheet_orig       = nb_orig["worksheets"][id_worksheet]

    for id_cell in range(len(worksheet_orig["cells"])):
        cell_orig       = worksheet_orig["cells"][id_cell]

        ## Switch based on cell type
        if cell_orig["cell_type"] == "markdown":
            assignment_text = cell_orig["source"]
            solution_text   = cell_orig["source"]
        elif cell_orig["cell_type"] == "code":
            assignment_text = cell_orig["input"]
            solution_text   = cell_orig["input"]
        elif cell_orig["cell_type"] == "heading":
            assignment_text = ""
            solution_text   = ""
        else:
            raise ValueError("Unrecognized cell type {}".format(cell_orig["cell_type"]))

        ## Assignment processing
        ##################################################
        ##   Remove task headers
        assignment_text = re.sub(
            '<!-- task-(begin|end) -->\n+',
            '',
            assignment_text
        )
        assignment_text = re.sub(
            '# task-(begin|end)\n+',
            '',
            assignment_text
        )

        ##   Delete between solution headers
        assignment_text = re.sub(
            '<!-- solution-begin -->(\n|.)*?<!-- solution-end -->\n?',
            '',
            assignment_text
        )
        assignment_text = re.sub(
            '# solution-begin(\n|.)*?# solution-end',
            '',
            assignment_text
        )

        ## Solution processing
        ##################################################
        ##   Remove solution headers
        solution_text = re.sub(
            '<!-- solution-(begin|end) -->\n+',
            '',
            solution_text
        )
        solution_text = re.sub(
            '# solution-(begin|end)\n+',
            '',
            solution_text
        )

        ##   Delete between task headers
        solution_text = re.sub(
            '<!-- task-begin -->(\n|.)*?<!-- task-end -->\n?',
            '',
            solution_text
        )
        solution_text = re.sub(
            '# task-begin(\n|.)*?# task-end',
            '',
            solution_text
        )

        ## Write the results
        ## Switch based on cell type
        if cell_orig["cell_type"] == "markdown":
            nb_assignment["worksheets"][id_worksheet]["cells"][id_cell]["source"] = \
                assignment_text
            nb_solution["worksheets"][id_worksheet]["cells"][id_cell]["source"] = \
                solution_text
        elif cell_orig["cell_type"] == "code":
            nb_assignment["worksheets"][id_worksheet]["cells"][id_cell]["input"] = \
                assignment_text
            nb_solution["worksheets"][id_worksheet]["cells"][id_cell]["input"] = \
                solution_text
        elif cell_orig["cell_type"] == "heading":
            nb_assignment["worksheets"][id_worksheet]["cells"][id_cell]["source"] = \
                cell_orig["source"]
            nb_solution["worksheets"][id_worksheet]["cells"][id_cell]["source"] = \
                cell_orig["source"]

## Output
nbformat.write(
    nb_assignment,
    filename_assignment,
    version = 4
)

nbformat.write(
    nb_solution,
    filename_solution,
    version = 4
)
