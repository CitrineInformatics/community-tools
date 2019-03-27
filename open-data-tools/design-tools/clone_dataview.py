#### standard packages ####
from os import environ

#### third party libraries ####
from citrination_client import CitrinationClient
from citrination_client.views.data_view_builder import DataViewBuilder


#### Set up a citrination client
client = CitrinationClient(
    environ.get("SLAC_CITRINATION_API_KEY"),
    "https://slac.citrination.com"
)

#### Initialize the client
data_view_id = '117'


def clone_data_view(client, target):
    """
    Creates a dataview if one does not exist at the supplied ID

    :param: client: a citrination client object
    :type: CitrinationClient
    :param: target: metadata of the dataview to be copied
    :type: dict
    :return: view_id: the view id of the created id
    :type: str
    """

    # Create ML configuration
    dv_builder = DataViewBuilder()
    dv_builder.dataset_ids(target['configuration']['dataset_ids'])
    [dv_builder.set_role(key, role.lower()) for key, role in target['configuration']['roles'].items()]
    [dv_builder.add_raw_descriptor(descriptor) for descriptor in target['configuration']['descriptors']]
    dv_config = dv_builder.build()

    view_id = client.data_views.create(dv_config,
                                       name='Copy of {}'.format(target['name']),
                                       description=target['description']
                                       )

    return view_id

if __name__ == "__main__":
    target_dv = client.data_views.get(data_view_id)
    print('Dataview at ID {} cloned to ID {}'.format(data_view_id, clone_data_view(client, target_dv)))

