# Machine Learning
*Authors: Enze Chen*

In this guide, we will cover how to configure a machine learning (ML) model from a data view using the Citrination web UI. ML is an automated process that identifies relationships in your data between a set of inputs and a set of outputs. The Citrination platform simplifies the user experience and generates powerful ML models with informative reports for analysis. Building a ML model also enables [Prediction and Design](07_predict_design.md), which is covered in a later guide.

## Learning outcomes
After reading this guide^, you should be familiar with:
* Choosing the set of inputs and output for a ML model
* Assessing model quality through Model Reports     
^*Note*: This guide is dense and will likely take many read-throughs before things start to fully click. Turns out, ML is [h](https://machinelearningmastery.com/applied-machine-learning-is-hard/)[a](https://developers.google.com/machine-learning/problem-framing/hard)[r](http://ai.stanford.edu/~zayd/why-is-machine-learning-hard.html)[d](https://www.forbes.com/sites/janakirammsv/2018/01/01/why-do-developers-find-it-hard-to-learn-machine-learning/#7d62eccf6bf6); when applied to materials science, it might be [even harder](https://youtu.be/28Ue_jteKI4?t=254).

## Background knowledge
To get the most out of this guide, it is helpful to be familiar with:
* How to create [data views](https://citrination.com/data_views/) on Citrination ([guide](03_data_view.md)).
* Basic machine learning. This is understandably vague and requires prerequisites in and of itself.
  * [This YouTube video](https://www.youtube.com/watch?v=nWk6QlwvXok), made by Julia Ling, gives an introduction to ML for materials science.
  * [This visual](http://www.r2d3.us/visual-intro-to-machine-learning-part-1/) is also a gentle introduction.

## Configure ML
You might recall in the [Data Views guide](03_data_views.md) that we deferred configuring ML services at the time—this guide picks up right where we left off. If you navigate to the view you created, and click on "Machine Learning Configuration," you will be asked to set column types for each of the properties in your view.

![ML config](fig/51_ml_config.png "ML config")

It is helpful to expand the description ("Show More") and read about the various parameters on this page. Down below, each property has its Descriptor Type (Categorical, Real, Organic, Inorganic, Alloy), Parameter Type (Input, Output, Latent variable, Ignore), and Values listed. If you would like to change a setting, click "edit" next to the corresponding property. We'll do this for "Property Crystallinity" because we want it as an Input rather than Output.

![Set columns](fig/52_set_col_types.png "Set columns")

The above menu will open up, allowing you to change the Variable Type to "Input." Depending on the Descriptor Type, this menu will show different options. *Categorical* descriptors will have all the categories listed for you to include (all are included by default), while *Real* descriptors will have a range of values for you to include. When you're all done—the other properties are fine, though you should always check each one—click "Okay" to collapse the menu, and finally "Save" at the very top.

## Model training
"Training" is the term that refers to a ML model learning the relationships in the data given. Blue progress bars will display at the top of your screen indicating which step it's currently on.

![Model training](fig/55_model_training.png "Model training")

Green boxes will appear at the top of the page informing you of when certain services are ready. Some services, like Model Reports, take longer than others, like Predict services. While you're waiting, if you navigate to the **Summary** page for your view, you will see the column headers listed with their configured settings for ML. You can always return to the Configuration page to change the property types.

![ML summary](fig/53_ml_summary.png "ML summary")

## Model reports

![Reports summary](fig/54_reports_summary.png "Reports summary")


### Feature statistics

![Pearson correlation](fig/54_reports_pearson.png "Pearson correlation")


![t-SNE plot](fig/54_reports_tsne.png "t-SNE plot")


### Model performance

![Model summary](fig/55_model_summary.png "Model summary")


![Feature importance](fig/55_model_features.png "Feature importance")


![Model performance](fig/55_model_performance.png "Model performance")


### Performance plots

![Predicted vs. Actual plot](fig/56_plot_pva.png "Predicted vs. Actual plot")


![Distribution of residuals](fig/56_plot_residual.png "Distribution of residuals")



## Conclusion
Whew! This concludes our lengthy discussion of ML on Citrination. At this point, you should be familiar with:
* Choosing the set of inputs and output for a ML model
* Assessing model quality through Model Reports

With your ML model in hand, you're now equipped to perform [Prediction and Design](07_predict_design.md) services through the UI. These are core elements of [Citrine's sequential learning framework](https://citrine.io/platform/sequential-learning/) and enable you to leverage the power of materials informatics to do better research, faster. As always, if you have further questions, please do not hesitate to [Contact Us](https://citrine.io/contact/).
