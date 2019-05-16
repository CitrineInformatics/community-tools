=======================
design-space-enumerator
=======================


This is a tool for the enumeration of inorganic material design spaces.


Description
===========

Enumerate a design space from a list of elements. This version only supports
building of a design space of equiatomic compositions.



.. list-table:: optional arguments
   :widths: 25 25
   :header-rows: 0

   * - -h, --help                                              
     - show this help message and exit               
   * - --version                                               
     - show program's version number and exit        
   * - -e ELEMENTS, --elements ELEMENTS                        
     - list of elemebts as -e Al -e Br ...                 
   * - -n NUM_ELEMENTS                                         
     - Number of elements in the chemical formula    
   * - -dfp DESIGN_FILEPATH, --designfilepath DESIGN_FILEPATH  
     - file path to a CSV of elements to enumerate   
   * - -sfp SAVE_FILEPATH, --savefilepath SAVE_FILEPATH        
     - file path to save design space as CSV         
   * - -k API_STRING, --apikey API_STRING                      
     - Citrination API key environment variable name 
   * - -s SITE, --site SITE                                    
     - Citrination site url                          
   * - -sv, --save                                             
     - Use csv file to store data                    
   * - -cn, --citrination                                      
     - Use citrination to store data                 
   * - -ds DATASET_ID, --dataset DATASET_ID                    
     - Citrination dataset ID to store data at       
   * - -v, --verbose                                           
     - set loglevel to INFO                          
   * - -vv, --very-verbose                                     
     - set loglevel to DEBUG
   
Note
====

This project has been set up using PyScaffold 3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
