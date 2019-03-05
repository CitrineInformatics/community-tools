#### standard packages ####
from os import environ
from time import sleep

#### third party libraries ####
from citrination_client import CitrinationClient
import pandas as pd

#### Set up a citrination client
client = CitrinationClient(
    environ.get("SLAC_CITRINATION_API_KEY"),
    "https://slac.citrination.com"
)

#### Initialize the client
dataset_id = 111
data_view_id = 97
model_client = client.models


view = model_client.get_data_view(data_view_id)

# get name
# get role
# get type
# get lower
# get upper
descriptor_list = []

for column in view.columns:
    name, role, group_by_key, column_type, categories, units, lower_bound, upper_bound, length, balance_element, basis = [None for i in range(0, 11)]

    name = column.name
    role = column.role
    group_by_key = column.group_by_key
    column_type = column._type

    try:
        categories = column.categories
    except:
        pass
    try:
        units = column.units
    except:
        pass
    try:
        lower_bound = column.lower_bound
    except:
        pass
    try:
        upper_bound = column.upper_bound
    except:
        pass
    try:
        length = column.length
    except:
        pass
    try:
        balance_element = column.balance_element
    except:
        pass
    try:
        basis = column.basis
    except:
        pass

    descriptor = [name,
                  role,
                  group_by_key,
                  column_type,
                  categories,
                  units,
                  lower_bound,
                  upper_bound,
                  length,
                  balance_element,
                  basis]

    descriptor_list.append(descriptor)

cols = ['name','role','group_by_key','column_type','categories','units',
           'lower_bound','upper_bound','length','balance_element','basis']

descriptor_df = pd.DataFrame(descriptor_list).to_csv('descriptors.csv', header=cols, index=False)
