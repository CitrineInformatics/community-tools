#### standard packages ####
from os import environ
from time import sleep

#### third party libraries ####
from citrination_client import CitrinationClient
from citrination_client.models.design import Target
from citrination_client.models.design.constraints import *

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

for column in view.columns:
    print(column.name)

