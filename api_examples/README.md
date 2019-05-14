# API Examples
This folder contains examples (Jupyter notebooks) of how to interface with the [Python Citrination Client](http://citrineinformatics.github.io/python-citrination-client/index.html). You should make sure that you have Python 3 and all packages listed in [`requirements.txt`](../software_setup/requirements.txt) installed properly.

![PyCC capabilities](fig/pycc_capabilities "PyCC capabilities")

## Organization
There are several notebooks in this repository that are part of a series of tutorials, though they can also be standalone references. They are:
1. [DataClient tutorial](1_data_client_api_tutorial.ipynb) - This introduces PyCC and the `DataClient` for uploading and managing datasets.
1. [DataViewsClient tutorial](2_data_views_client_api_tutorial.ipynb) - This introduces the `DataViewsClient` for creating views and ML configurations through the API.
1. [ModelsClient tutorial](3_models_client_api_tutorial.ipynb) - This introduces the `ModelsClient` for analyzing data views and submitting predict and design runs.
1. [Sequential learning tutorial](4_sequential_learning_api_tutorial.ipynb) - This combines all the above elements to create an end-to-end sequential learning demo.
1. [SearchClient tutorial](5_search_client_api_tutorial.ipynb) - This introduces the `SearchClient` for searching for and returning PIF records from Citrination.

The other notebooks demonstrate other important aspects of the Citrination API.

## Additional resources
* More API examples can be found in our public [learn-citrination](https://github.com/CitrineInformatics/learn-citrination) GitHub repo. In particular, the repo contains:
  * `pypif` tutorials: [Intro](https://github.com/CitrineInformatics/learn-citrination/blob/master/WorkingWithPIFs.ipynb) and [Advanced](https://github.com/CitrineInformatics/learn-citrination/blob/master/AdvancedPif.ipynb) notebooks describing the PIF structure and how to use the `pypif` package.
  * [Intro](https://github.com/CitrineInformatics/learn-citrination/blob/master/IntroQueries.ipynb) and [Advanced](https://github.com/CitrineInformatics/learn-citrination/blob/master/AdvancedQueries.ipynb) notebooks explaining how queries are constructed to search for data using the API.
* Screenshot tutorials of our web UI can be found in a [separate folder](../web_ui_examples).
