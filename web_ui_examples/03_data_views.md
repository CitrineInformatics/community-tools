# Data Views
*Authors: Enze Chen*

In this document, we will cover how to create a Data View ("View" for short) on Citrination using the web UI. Views provide a way for users to aggregate the information in a dataset(s) and present it in a more visually appealing way (matrix, plots, etc.). Views also enable [machine learning (ML) services](06_machine_learning.md), which we will cover in a later guide.

## Learning outcomes
After reading this document, you should feel comfortable with:
* Creating new Views using the Citrination UI
* Inspecting data in matrix and plots formats

## Background knowledge
To get the most out of this guide, it is helpful to be familiar with:
* The Physical Information File (PIF) format. This is how data is stored in Citrination, and it is our recommended format for any materials data.
  * [Documentation](http://citrineinformatics.github.io/pif-documentation/schema_definition/index.html)
  * [Publication](https://www.cambridge.org/core/journals/mrs-bulletin/article/beyond-bulk-single-crystals-a-data-format-for-all-materials-structurepropertyprocessing-relationships/AADBAEDA62B0391D708CF02269989E8B)
  * [Example](https://github.com/CitrineInformatics/learn-citrination/blob/master/AdvancedPif.ipynb)
* [Datasets](02_data_management.md) on Citrination.

## Data Views page
Views on Citrination can be accessed through the "Data Views" menu option, which takes you to the page below:   

![Views page](fig/21_views_page.png "Views page")   

This page has three subheadings that lists all the Views shared publicly, privately, and within teams. You can search for specific Views using the search bar on the right, and clicking on the name of the View will take you to the main page for that View. Assuming you're here for the first time, we'll go ahead and click **Create New Data View**.

## Creating a new View
Since Views are built from datasets, the first step in Views creation is selecting which datasets should be included.   

![Select dataset](fig/22_select_dataset.png "Select dataset")   

You have the option to search for specific datasets and select the relevant ones by clicking the boxes on the left. The UI will display how many PIF records are in each dataset. After you have selected at least one dataset, the "NEXT" button at the top will turn blue and clicking it will take you to the next page.   

### Select columns
![Select columns](fig/23_select_columns.png "Select columns")   

From the datasets, Citrination will extract the chemical formula and properties that appear, along with the number of PIF records that have each property (though not how the counts correspond). You have to select at least one of the properties to be a column in your View, and the "Include All" button is a shortcut for selecting everything. After you've selected the desired columns, the "NEXT" button will be enabled, taking you to the next page.

### View summary
![View summary](fig/24_view_summary.png "View summary")   

The next page is the View summary, where you can give your View a name and description. It also shows which datasets are included in this View, so that is a good sanity check. You will have the option to edit the name and description fields later. When everything looks good, you must click "SAVE" to finish making the View.


### Configure ML
At this point, the UI will turn dark and the following pop-up will appear:   

![Configure ML](fig/25_configure_ml.png "Configure ML")   

You have the option of training ML models now, or later. Since this is a fairly involved process, we'll cover it in [a subsequent guide](06_machine_learning.md), and select "Later" for now.

## View matrix
Congratulations on making your first View!

<img src="https://github.com/CitrineInformatics/community-tools/blob/enze/ui-tutorials/web_ui_examples/fig/26_view_matrix.png" alt="View matrix" width="700" height="521">  

![View plot config](fig/27_view_plots1.png "View plot config")

<img src="https://github.com/CitrineInformatics/community-tools/blob/enze/ui-tutorials/web_ui_examples/fig/27_view_plots2.png" alt="View histogram" width="450" height="422">  
