# Graph RAG



## GraphRAG Solution Accelerator deployment in Gov
These are the steps as of 2/27/2025. 
Thanks to Tim Meyers, Josh Bradley and Mary Wahl!!

GraphRAG SA : https://github.com/Azure-Samples/graphrag-accelerator

- Update deploy.parameters.json file in ./infra (add the following as is)
"AISEARCH_ENDPOINT_SUFFIX": "search.azure.us",
"AISEARCH_AUDIENCE": "https://search.azure.us",
"CLOUD_NAME":"AzureUSGovernment",
"COGNITIVE_SERVICES_AUDIENCE":https://cognitiveservices.azure.us/.default

- In apim.bicep you have to make the following change:  2024-06-01-preview API version needs to become 2023-09-01-preview

- Make changes to biceps file as mentioned by RichardHallgren here [https://github.com/Azure-Samples/graphrag-accelerator/issues/230]

- Deployment process

az cloud set --name "AzureUSGovernment"     
az login    
cd infra        
bash deploy.sh -g -p deploy.parameters.json  


- Redeploymnet steps
    - Make changes and rerun deployment script
    - Chek resourcegrouop --> deployment slots for update


## Indexing 
All of the uploaded documents, parquet files(that contains Graph data extracted) and indexing log will be stored in the Storage account containers.
Check the indexing log in the storage account to follow the indexing process. There are 11 steps in the indexing workflow. 
#### Auto Tuning of Prompts
It makes sense to tune the promts based on your data and query use case. If you decide to use auto tuning option, make sure to validate the prompts generated. As of now there is a bug [https://github.com/Azure-Samples/graphrag-accelerator/issues/256]

Note!! Always make sure to test the indexing with small data set before ingesting large volume of data. 

### Index Details
#### Original Data Details
- Original Data: All PDFs. Total size 550MB
- Extracted the text using markitdown [https://github.com/microsoft/markitdown] . Size of the text data 18.2MB
- Num of tokens of the input text data: 4159393

#### Index Duration
- Text size of our data set: 18.2MB
- LLM model: GPT 4o Mini with 2KTPM Capacity
- Duration: we indexed this datatwice. Once it took 18.5 hrs and the other time it took 16 hrs. 
- Dependent factors: LLM model and its capacity, Prompts(entities and relationships to be extracted). Number of Entity Types defined: 21 
#### Extracted Graph Details
- No of Nodes:30925 , No of Edges: 43K
- No of Community Levels: 5 (0-4)
- No of communities at each level: 0-58, 1-1090, 2-4291, 3-1388, 4-17
Note: There is a bug related to extracted entity types. GraphRAG extracts more entity types than defined

## Query

Therea are two options. Global and Local. 
- Global : User query runs through all Community reports at a specific level. No Vector search involved. Just the user query, GPT Model and Community reports as context!! So if the right entities and relationships are not extracetd, you will see poor results!!! 

- Local : This is lot more involved. As of now there is a bug that it hallunicantes!! https://github.com/Azure-Samples/graphrag-accelerator/issues/260 

### Web app for Query
There seems to an issue with getting the front end webapp deployed. 
We put together a simple Query Web App based on StreamLit, that is shared here. 


## Contributors
- Josh Bradley
- Tim Meyers
- Mary Wahl
- Rich Posada

