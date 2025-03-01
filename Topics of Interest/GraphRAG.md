# Graph RAG



## GraphRAG Solution Accelerator deployment in Gov
These are the steps as of 2/27/2025. Thanks to Tim Meyers, Josh Bradley and Mary Wahl!!

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

### Auto Tuning of Prompts
It makes sense to tune the promts based on your data and query use case. If you decide to use auto tuning option, make sure to validate the prompts generated. As of now there is a bug [https://github.com/Azure-Samples/graphrag-accelerator/issues/256]

Note!! Always make sure to test the indexing with small data set before ingesting large volume of data. 

### Index Duration

Text size of our data set: 18.2MB
LLM model: GPT 4o Mini with 2KTPM Capacity
Duration: 18.5 hrs
dependent factors: LLM model and its capacity, Prompts(entities and relationships to be extracted) 
