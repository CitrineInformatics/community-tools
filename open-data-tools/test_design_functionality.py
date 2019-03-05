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

#### Submit a design request
design_uuid = model_client.submit_design_run(data_view_id ,
                                             num_candidates = 20,
                                             effort = 10,
                                             target=Target('Property r0_sphere', 10),
                                             constraints=[],
                                             sampler="Default"
                                             ).uuid

#### Wait for design to finish
fin = False

while not fin:

    stat = model_client.get_design_run_status(data_view_id, design_uuid)
    sleep(10)
    print('design finished: {} ({}/100)'.format(stat.finished(), stat.progress))

    if int(stat.progress) == 100:
        fin = True

results = model_client.get_design_run_results(data_view_id, design_uuid)

#### Print results
for i, result in enumerate(results.best_materials):
    print('Result {}\n{}\n'.format(i,result))
# for item in result:
# print(item)
# print(result['descriptor_values']['Uncertainty in Property pop1_specie0_r0'])
# print(result['citrine_score'])
