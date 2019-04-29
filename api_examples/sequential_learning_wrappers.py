'''
Authors: Eddie Kim, Enze Chen
This file contains wrapper functions that are used in the sequential learning API tutorial notebook. Detailed docstrings with method fuctions and parameters are given below.
'''

import json
from collections import OrderedDict
from time import sleep
from typing import Callable, List, Tuple, Optional

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.contour import QuadContourSet
import seaborn as sns
from citrination_client import (CitrinationClient, DataQuery, DatasetQuery,
                                Filter, PifSystemReturningQuery,
                                RealDescriptor)
from citrination_client.models.design import Target
from citrination_client.views.data_view_builder import DataViewBuilder
from pypif import pif
from pypif.obj import *

circle_size=75
star_size=100


def write_dataset_from_func(test_function:Callable[[np.ndarray], float],
                        filename:str, input_vals:List[np.ndarray]) -> None:
    '''Given a function, write a dataset evaluated on given input values

    :param test_function: Function for generating dataset
    :type test_function: Callable[[np.ndarray], float]
    :param filename: Name of file for saving CSV dataset
    :type filename: str
    :param input_vals: List of input values to eval function over
    :type input_vals: np.ndarray
    :return: Doesn't return anything
    :rtype: None
    '''

    pif_systems = []
    for i, val_row in enumerate(input_vals):
        system = System()
        system.names = f'{test_function.__name__}_{i}'
        system.properties =  []

        for j, x_val in enumerate(val_row):
            func_input = Property()
            func_input.name = f"x{j+1}"
            func_input.scalars = x_val
            system.properties.append(func_input)

        func_output = Property()
        func_output.name = f"y"
        func_output.scalars = test_function(val_row)
        system.properties.append(func_output)
        pif_systems.append(system)

    with open(filename, "w") as f:
        f.write(pif.dumps(pif_systems, indent=4))


def upload_data_and_get_id(client:CitrinationClient,
                        dataset_name:str,
                        dataset_local_fpath:str,
                        create_new_version:Optional[bool] = False,
                        given_dataset_id:Optional[int] = None) -> int:
    '''Uploads data to a new/given dataset and returns its ID

    :param client: Client API object to pass in
    :type client: CitrinationClient
    :param dataset_name: Name of dataset
    :type dataset_name: str
    :param dataset_local_fpath: Local data filepath
    :type dataset_local_fpath: str
    :param create_new_version: Whether or not to make a new version
    :param create_new_version: bool
    :param given_dataset_id: ID if using existing dataset, defaults to None
    :param given_dataset_id: int
    :return: ID of the dataset
    :rtype: int
    '''


    if given_dataset_id is None:
        dataset = client.data.create_dataset(dataset_name)
        dataset_id = dataset.id
    else:
        dataset_id = given_dataset_id
        if create_new_version:
            client.data.create_dataset_version(dataset_id)

    client.data.upload(dataset_id, dataset_local_fpath)
    assert (client.data.matched_file_count(dataset_id) >= 1), "Upload failed."
    return dataset_id


def build_view_and_get_id(client:CitrinationClient, dataset_id:int,
                        view_name:str, input_keys:List[str],
                        output_keys:List[str], view_desc:str = "",
                        wait_time:int = 2, print_output:bool = False) -> int:
    '''Builds a new data view and returns the view ID

    :param client: Client object
    :type client: CitrinationClient
    :param dataset_id: Dataset to build view from
    :type dataset_id: int
    :param view_name: Name of the new view
    :type view_name: str
    :param input_keys: Input key names
    :type input_keys: List[str]
    :param output_keys: Output key names
    :type output_keys: List[str]
    :param view_desc: Description for the view, defaults to ""
    :param view_desc: str, optional
    :param wait_time: Wait time in seconds before polling API
    :type wait_time: int
    :param print_output: Whether or not to print outputs
    :type print_output: bool
    :return: ID of the view
    :rtype: int
    '''

    dv_builder = DataViewBuilder()
    dv_builder.dataset_ids([str(dataset_id)])
    dv_builder.model_type('default') # random forest

    for key_name in input_keys:
        if 'formula' in key_name:
            desc_x = InorganicDescriptor(key=key_name,
                                         threshold=1)
            dv_builder.add_descriptor(descriptor=desc_x,
                                      role='input')
        else:
            desc_x = RealDescriptor(key=key_name,\
                                    lower_bound=-9999.0,\
                                    upper_bound=9999.0)
            dv_builder.add_descriptor(desc_x, role='input')


    for key_name in output_keys:
        desc_y = RealDescriptor(key=key_name,\
        						lower_bound=-9999.0,\
        						upper_bound=9999.0)
        dv_builder.add_descriptor(desc_y, role='output')

    dv_config = dv_builder.build()

    _wait_on_ingest(client, dataset_id, wait_time, print_output)

    dv_id = client.data_views.create(
        configuration=dv_config,
        name=view_name,
        description=view_desc
    )
    return dv_id


def run_sequential_learning(client:CitrinationClient, view_id:int, dataset_id:int,
                        num_candidates_per_iter:int,
                        design_effort:int, wait_time:int,
                        num_sl_iterations:int, input_properties:List[str],
                        target:List[str], print_output:bool,
                        true_function:Callable[[np.ndarray], float],
                        score_type:str,
                        ax_data:Axes=None,
                        ax_model:Axes=None,
                        ) -> Tuple[List[float], List[float]]:
    '''Runs SL design

    :param client: Client object
    :type client: CitrinationClient
    :param view_id: View ID
    :type view_id: int
    :param dataset_id: Dataset ID
    :type dataset_id: int
    :param num_candidates_per_iter: Candidates in a batch
    :type num_candidates_per_iter: int
    :param design_effort: Effort from 1-30
    :type design_effort: int
    :param wait_time: Wait time in seconds before polling API
    :type wait_time: int
    :param num_sl_iterations: SL iterations to run
    :type num_sl_iterations: int
    :param input_properties: Inputs
    :type input_properties: List[str]
    :param target: ("Output property", {"Min", "Max"})
    :type target: List[str]
    :param print_output: Whether or not to print outputs
    :type print_output: bool
    :param true_function: Actual function for evaluating measured/true values
    :type true_function: Callable[[np.ndarray], float]
    :param score_type: MLI or MEI
    :type score_type: str
    :return: 2-tuple: list of predicted scores/uncertainties; list of measured scores/uncertainties
    :rtype: Tuple[List[float], List[float]]
    '''



    best_sl_pred_vals = []
    best_sl_measured_vals = []

    _wait_on_ingest(client, dataset_id, wait_time, print_output)

    for i in range(num_sl_iterations):

        if print_output:
            print(f"\n---STARTING SL ITERATION #{i+1}---")

        _wait_on_ingest(client, dataset_id, wait_time, print_output)
        _wait_on_data_view(client, dataset_id, view_id, wait_time, print_output)

        # Plot dataset as it is at start of iteration
        # Could include measurements from previous iteration if not first iteration
        if ax_data is not None:
            if i:
                old_point_plot.remove()
                new_point_plot.remove()

            old_point_plot, new_point_plot = \
                plot_dataset_2d(client,
                                dataset_id,
                                'x1',
                                'x2',
                                'y',
                                ax_data=ax_data,
                                first_time=(not i),
                                iteration=i,
                                num_candidates_per_iter=num_candidates_per_iter
                                )

        # Submit a design run
        design_id = client.submit_design_run(
                data_view_id=view_id,
                num_candidates=num_candidates_per_iter,
                effort=design_effort,
                target=Target(*target),
                constraints=[],
                sampler="Default"
            ).uuid

        if print_output:
            print(f"Created design run with ID {design_id}")

        _wait_on_design_run(client, design_id, view_id, wait_time, print_output)

        # Compute the best values with uncertainties as a list of (value, uncertainty)
        if score_type == "MEI":
            candidates = client.get_design_run_results(view_id, design_id).best_materials
        else:
            candidates = client.get_design_run_results(view_id, design_id).next_experiments
        values_w_uncertainties = [
            (
                m["descriptor_values"][target[0]],
                m["descriptor_values"][f"Uncertainty in {target[0]}"]
            ) for m in candidates
        ]

        # Plot model surface and candidates
        if ax_model is not None:
            # Remove existing surface + points
            if i:
                [c.remove() for c in model_surface.collections]
                candidates_on_model.remove()

            model_surface = plot_model_2d(client,
                                        view_id,
                                        ax_model=ax_model,
                                        first_time=(not i)
                                        )
            candidates_on_model = \
                plot_candidates_on_model_2d(candidates,
                                            ax_model=ax_model,
                                            x1_col='x1',
                                            x2_col='x2',
                                            y_col='y')


        # Find and save the best predicted value
        if target[1] == "Min":
            best_value_w_uncertainty = min(values_w_uncertainties, key=lambda x: x[0])
        else:
            best_value_w_uncertainty = max(values_w_uncertainties, key=lambda x: x[0])

        best_sl_pred_vals.append(best_value_w_uncertainty)
        if print_output:
            print(f"SL iter #{i+1}, best predicted (value, uncertainty) = {best_value_w_uncertainty}")

        # Update dataset w/ new candidates
        new_x_vals = []
        for material in candidates:
            new_x_vals.append(np.array(
                [float(material["descriptor_values"][x]) for x in input_properties]
            ))

        temp_dataset_fpath = f"design-{design_id}.json"
        write_dataset_from_func(true_function, temp_dataset_fpath, new_x_vals)
        upload_data_and_get_id(
            client,
            "", # No name needed for updating a dataset
            temp_dataset_fpath,
            given_dataset_id=dataset_id
        )

        _wait_on_ingest(client, dataset_id, wait_time, print_output)

        if print_output:
            print(f"Dataset updated: {len(new_x_vals)} candidates added")

        query_dataset = PifSystemReturningQuery(size=9999,
                            query=DataQuery(
                            dataset=DatasetQuery(
                                id=Filter(equal=str(dataset_id))
                        )))
        query_result = client.search.pif_search(query_dataset)

        if print_output:
            print(f"New dataset contains {query_result.total_num_hits} PIFs")

        # Update measured values in new dataset
        dataset_y_values = []
        for hit in query_result.hits:
            # Assume last prop is output if following this script
            dataset_y_values.append(
                float(hit.system.properties[-1].scalars[0].value)
            )

        if target[1] == "Min":
            best_sl_measured_vals.append(min(dataset_y_values))
        else:
            best_sl_measured_vals.append(max(dataset_y_values))

        # Retrain model w/ wait times
        client.data_views.retrain(view_id)
        _wait_on_data_view(client, dataset_id, view_id, wait_time, print_output)

    # Final plot, last round of measurements
    # Plot dataset as it is at start of iteration
    # Could include measurements from previous iteration if not first iteration

    _wait_on_ingest(client, dataset_id, wait_time, print_output)
    _wait_on_data_view(client, dataset_id, view_id, wait_time, print_output)

    if ax_data is not None:
        if i:
            old_point_plot.remove()
            new_point_plot.remove()

        old_point_plot, new_point_plot = \
            plot_dataset_2d(client,
                            dataset_id,
                            'x1',
                            'x2',
                            'y',
                            ax_data=ax_data,
                            first_time=(not i),
                            iteration=i,
                            num_candidates_per_iter=num_candidates_per_iter
                            )

    if print_output:
        print("SL finished!\n")

    return (best_sl_pred_vals, best_sl_measured_vals)


def _wait_on_ingest(client:CitrinationClient, dataset_id:int,
                        wait_time:int, print_output:bool=True) -> None:
    # Wait for ingest to finish
    sleep(wait_time)
    while (client.data.get_ingest_status(dataset_id) != "Finished"):
        if print_output:
            print("Waiting for data ingest to complete...")
        sleep(wait_time)


def _wait_on_data_view(client:CitrinationClient, dataset_id:int,
                        view_id:int, wait_time:int,
                        print_output:bool=True) -> None:
    is_view_ready = False
    sleep(wait_time)
    while (not is_view_ready):
        sleep(wait_time)
        design_status = client.data_views.get_data_view_service_status(view_id)
        if (design_status.experimental_design.ready and
        design_status.predict.event.normalized_progress == 1.0):
            is_view_ready = True
            if print_output:
                print("Design ready")
        else:
            print("Waiting for design services...")


def _wait_on_design_run(client:CitrinationClient, design_id:int, view_id:int,
                        wait_time:int, print_output:bool=True) -> None:
    design_processing = True
    sleep(wait_time)
    while design_processing:
        status = client.get_design_run_status(view_id, design_id).status
        if print_output:
            print(f"Design run status: {status}")

        if status != "Finished":
            sleep(wait_time)
        else:
            design_processing = False


def plot_dataset_2d(client:CitrinationClient, dataset_id:int,
                    x1_col:str, x2_col:str, y_col:str,
                    ax_data:Axes=None,
                    xlims:List[float]=[-5,5],
                    ylims:List[float]=[-5,5],
                    first_time:bool=False,
                    iteration:int=0,
                    num_candidates_per_iter:int=10,
                    )->(Line2D, Line2D):
    '''Plots a dataset on an x1/x2 axes with color for y
    If not first iteration, mark new measurements as stars

    :param client: Client object
    :type client: CitrinationClient
    :param dataset_id: Dataset ID
    :type dataset_id: int
    :param x1_col: "x1" (string corresponding to a property name in dataset)
    :type x1_col: str
    :param x2_col: "x2" (string corresponding to a property name in dataset)
    :type x2_col: str
    :param y_col: "y" (string corresponding to the target property name in dataset)
    :type y_col: str
    :param ax_data: matplotlib Axes object to be plotted on.
    :type ax_data: Axes
    :param xlims: lower and upper bounds for x axis
    :type xlims: List[float]
    :param ylims: lower and upper bounds for y axis
    :type ylims: List[float]
    :param first_time: whether this is the first instance of this plot being made
    to avoid duplicate colorbar creation
    :type first_time: bool
    :param iteration: current iteration of loop
    :type iteration: int
    :param num_candidates_per_iter: name is self explanatory, passed through from parent function
    :type num_candidates_per_iter: int

    :return: data_point_plot, the plot object of the points that were plotted
    :rtype: (Line2D, Line2D)
    '''
    
    # Get the dataset into a DataFrame
    query_dataset = PifSystemReturningQuery(size=9999,
                        query=DataQuery(
                            dataset=DatasetQuery(
                                id=Filter(equal=str(dataset_id))
                    )))
    query_result = client.search.pif_search(query_dataset)
    result_list = [{prop._name:prop._scalars[0]._value for prop in result._system._properties}
                    for result in query_result._hits]
    df_current = pd.DataFrame(result_list).astype(float)
    df_current['updated_at'] = [hit._updated_at for hit in query_result._hits]
    df_current = df_current.sort_values('updated_at')
    vmin = df_current[y_col].min()
    vmax = df_current[y_col].max()

    # Setup axes
    plt.sca(ax_data)

    # Split into old measurements and new measurements
    if not first_time:
        num_rows = len(df_current)
        num_new = num_candidates_per_iter
        num_old = num_rows-num_new
        df_old = df_current.iloc[:num_old+1]
        df_new = df_current.iloc[-num_new:]
    else:
        df_old = df_current
        

    # Plot points
    old_point_plot = plt.scatter(x1_col, x2_col,
                                c = y_col,
                                data = df_old,
                                cmap = plt.cm.plasma,
                                marker = 'o',
                                s = circle_size,
                                alpha = 0.75,
                                vmin=vmin,
                                vmax=vmax)
    
    # Add labels if first time generating the plot
    if first_time:
        plt.colorbar(label='toy function value')
        plt.xlabel(x1_col)
        plt.ylabel(x2_col)
        plt.xlim(xlims)
        plt.ylim(ylims)
        plt.title('Initial Data')
        plt.legend(['measurements'])
        new_point_plot = plt.scatter([],[])

    else:
        new_point_plot = plt.scatter(x1_col, x2_col,
                                    c = y_col,
                                    data = df_new,
                                    cmap = plt.cm.plasma,
                                    marker = '*',
                                    s = star_size,
                                    alpha = 1,
                                    edgecolor='w',
                                    vmin=vmin,
                                    vmax=vmax)
        plt.title(f'Measurements, iter. {iteration}')
        plt.legend(['old measurements', 'new measurements'])


    ax_data.figure.canvas.draw()

    return old_point_plot, new_point_plot


def plot_model_2d(client:CitrinationClient,
                    view_id:int,
                    ax_model:Axes=None,
                    x1lims:List[float]=[-5,5],
                    x2lims:List[float]=[-5,5],
                    dgrid:float=0.1,
                    first_time:bool=False)->QuadContourSet:
    '''Plots a model surface on x1/x2 axes with color for y

    :param client: Client object
    :type client: CitrinationClient
    :param view_id: view ID
    :type view_id: int
    :param ax_model: matplotlib Axes object to be plotted on.
    :type ax_model: Axes
    :param x1lims: lower and upper bounds for x1 mesh
    :type x1lims: List[float]
    :param x2lims: lower and upper bounds for x2 mesh
    :type x2lims: List[float]
    :param dgrid: discretization for meshgrid (both x and y)
    :type dgrid: float
    :param first_time: whether this is the first instance of this plot being made
    to avoid duplicate colorbar creation
    :type first_time: bool

    :return: model_surface
    :rtype: QuadContourSet (matplotlib plot object)
    '''
    
    # Get the first two column names of the DataView
    dv_descriptors = client.data_views.get(view_id)['configuration']['descriptors'][::-1]
    input_keys = [d['descriptor_key'] for d in dv_descriptors[:-1]]

    # Create an x1/x2 meshgrid to run predictions on
    x1_range = np.arange(x1lims[0],x1lims[1],dgrid)
    x2_range = np.arange(x2lims[0],x2lims[1],dgrid)
    xx_grid = np.meshgrid(x1_range, x2_range)

    # Convert the xx_grid arrays into proper candidates for Citrination
    # (list of dicts)
    candidate_grid = [{input_keys[0]:x1_val,
                       input_keys[1]:x2_val}
                      for x1_val, x2_val in zip(xx_grid[0].ravel(),
                                                xx_grid[1].ravel())
                      ]

    # Run predict services over the grid and get back a grid
    # of predicted values same shape as xx_grid arrays
    predictions_grid = client.models.predict(str(view_id), candidate_grid)
    pred_vals_list = [pred._values['Property y']._value for pred in predictions_grid]
    pred_vals_grid = np.array(pred_vals_list).reshape(xx_grid[0].shape)

    # Setup axes and plot model
    plt.sca(ax_model)
    model_surface = plt.contourf(xx_grid[0],
                                xx_grid[1],
                                pred_vals_grid,
                                cmap=plt.cm.plasma)

    # Add colorbar and labels if this is the first time making the plot
    if first_time:
        plt.colorbar()
        plt.xlabel(r'$x_1$'); plt.ylabel(r'$x_2$')
        plt.xlim(x1lims); plt.ylim(x2lims)
        plt.title("Model's Predicted Response Surface")

    ax_model.figure.canvas.draw()
    
    return model_surface


def plot_candidates_on_model_2d(candidates:List[dict],
                                ax_model:Axes=None,
                                x1_col:str='x1',
                                x2_col:str='x2',
                                y_col:str='y')->Line2D:
    ''' Plot candidates (just x1/x2) as black stars on model surface

    :param candidates: list of candidate points generated by design run
    :type candidates: List[dict]
    :param ax_model: matplotlib Axes object to be plotted on
    :type ax_model: Axes
    :param x1_col: "x1" (string corresponding to a property name in dataset)
    :type x1_col: str
    :param x2_col: "x2" (string corresponding to a property name in dataset)
    :type x2_col: str
    :param y_col: "y" (string corresponding to the target property name in dataset)
    :type y_col: str

    :return: candidates_on_model, the plot object of the candidate points
    :rtype: Line2D
    '''

    # DataFrame of candidates
    df_cand = pd.DataFrame(candidates)
    df_cand[list(df_cand['descriptor_values'].iloc[0].keys())] = \
        df_cand['descriptor_values'].apply(pd.Series)
    df_cand = df_cand.drop(['descriptor_values', 'constraint_likelihoods'], axis=1)
    df_cand = df_cand.astype(float)

    # Plot the points
    candidates_on_model = \
        plt.scatter(df_cand[f'Property {x1_col}'].values,
                    df_cand[f'Property {x2_col}'].values,
                    marker = '*',
                    facecolor = 'k',
                    edgecolor = 'w',
                    s = star_size)

    ax_model.figure.canvas.draw()

    return candidates_on_model


def plot_sl_results(measured, predicted, init_best):
    # Measured results
    sns.lineplot(
        x=np.arange(1, len(measured)+1),
        y=[round(float(v), 3) for v in measured],
        lw=5,
        estimator=None,
        markers=True,
        color="steelblue",
        label=f"Measured Results",
        legend=False,

    )

    # Predicted results
    predicted_ax = sns.lineplot(
        x=np.arange(1, len(predicted)+1),
        y=[round(float(v[0]), 3) for v in predicted],
        lw=5,
        estimator=None,
        markers=True,
        color="orange",
        label=f"Predicted Results",
        legend=False,

    )

    # Error bars
    predicted_ax.errorbar(
        x=np.arange(1, len(predicted)+1),
        y=[round(float(v[0]), 3) for v in predicted],
        yerr=[round(float(v[1]), 3) for v in predicted],
        lw=5,
        color="green",
        ecolor=["green"]*len(predicted),
        label="Predicted Uncertainty",
        fmt='',
        zorder=-1
    )

    # Best candidate in training set
    sns.lineplot(
        x=np.arange(1, len(predicted)+1),
        y=[init_best] * len(predicted),
        estimator=None,
        markers=False,
        label=f"Best in Training",
        legend=False,
        color="black",
        lw=4,
        alpha=0.7
    )

    plt.xlabel("SL iteration #")
    plt.legend(loc='best')
    # plt.legend(loc='best', bbox_to_anchor=(1.5, 1.0))
    plt.ylabel("Function value")
    plt.ylim([0, float(predicted[0][0])+1])
    plt.title(f"Optimizing using MLI")
    plt.grid(b=False, axis='x')
    plt.show()
