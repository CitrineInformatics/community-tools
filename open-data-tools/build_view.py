#### standard packages ####
from os import environ
import ast

#### third party libraries ####
from citrination_client import CitrinationClient
from citrination_client.views.data_view_builder import DataViewBuilder
from citrination_client.views.descriptors import RealDescriptor, CategoricalDescriptor
import pandas as pd

#### Set up a citrination client
client = CitrinationClient(
    environ.get("SLAC_CITRINATION_API_KEY"),
    "https://slac.citrination.com"
)

#### Initialize the client
dataset_id = 118
data_view_id = ''

def get_config():
    """

    :return:
    """
    pass

def check_for_view(client, data_view_id):
    """
    :param: data_view_id: The view of the dataview to use
    :type: str
    :return: check_for_view: either the dataview exists or is created
    :type: bool
    """

    try:
        client.models.get_data_view(data_view_id)

    except Exception as exc:
        data_view_id = build_data_view(client)
        print("Dataview at provided ID does not exist, new view created at {}".format(data_view_id))

    return data_view_id


def build_data_view(client):
    """
    Creates a dataview if one does not exist at the supplied ID

    :param: client: a citrination client object
    :type: CitrinationClient
    :return: view_id: the view id of the created id
    :type: str
    """

    # Create ML configuration
    dv_builder = DataViewBuilder()
    dv_builder.dataset_ids(str(dataset_id))  # ID number for band gaps dataset
    descriptor_df = pd.read_csv('descriptors.csv', header=0)

    # Define descriptors

    def build_descriptor(x):

        col_type = x['column_type']

        if col_type == 'Real':

            descriptor = RealDescriptor(key=x['name'], lower_bound=x['lower_bound'], upper_bound=x['upper_bound'])

            if descriptor.key not in dv_builder.configuration['roles']:
                dv_builder.add_descriptor(descriptor, role=x['role'], group_by_key=x['group_by_key'])

        elif col_type == 'Categorical':

            cats = ast.literal_eval(x['categories'])
            descriptor = CategoricalDescriptor(key=x['name'], categories=cats)

            if descriptor.key not in dv_builder.configuration['roles']:
                dv_builder.add_descriptor(descriptor, role=x['role'])

    descriptor_df.apply(build_descriptor, axis=1)

    # Build the configuration once all the pieces are in place and create dataview
    dv_config = dv_builder.build()
    name = 'pypaws_test_suite_dataview'
    description = 'A dataview set up for SLAC SMASH-ML Pd nanoparticle synthesis'
    print(dv_config)
    data_view_id = client.data_views.create(dv_config, name=name, description=description)

    return data_view_id


if __name__ == "__main__":
    print(check_for_view(client, data_view_id))

