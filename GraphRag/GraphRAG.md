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


### Indexing 
All of the uploaded documents, parquet files(that contains Graph data extracted) and indexing log will be stored in the Storage account containers.
Check the indexing log in the storage account to folowing indexing process. There are 11 steps in the indexing workflow. 
#### Auto Tuning of Prompts
It makes sense to tune the promts based on your data and query use case. If you decide to use auto tuning option, make sure to validate the prompts generated. As of now there is a bug [https://github.com/Azure-Samples/graphrag-accelerator/issues/256]

Note!! Always make sure to test the indexing with small data set before ingesting large volume of data. 

### Index Duration

Text size of our data set: 18.2MB
LLM model: GPT 4o Mini with 2KTPM Capacity
Duration: 18.5 hrs
dependent factors: LLM model and its capacity, Prompts(entities and relationships to be extracted) 


## Query

Therea are two options. Global and Local. 
- Global : User query runs through all Community reports at a specific level. No Vector search involved. Just the user query, GPT Model and Community reports as context!! So if the right entities and relationships are not extracetd, you will see poor results!!! 

- Local : This is lot more involved. As of now there is a bug that it hallunicantes!! https://github.com/Azure-Samples/graphrag-accelerator/issues/260 

### Web app for Query
There seems to an issue with getting the front end webapp deployed. It is easy put together a webapp for query using Streamlit. 
will be added soon!
## Contributors
- Josh Bradley
- Mary Wahl
- Tim Meyers
