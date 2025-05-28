# Excel related use cases(Draft)

In many organizations, user's task with Excel data. This excel may be the original data source or generated from a DB by an application. From the user perspective, the task starts with Excel data. 

## Excel Data Details
These Excel documents could be single sheet or multi sheet. Some of the multi sheet scenarios, the schema would be same across all sheets(like each unit data or quarter data etc). These excels may all types of columns including Text column that contains reasona text like summary, description etc. 

## Use Cases
User might need to perform the following type of tasks in order to accomplish their organizational or mission related action items
- Extract relevant data from the excel
    - Get me all the movies of Action Genre directed by Clint Eastwood
- Extract aggregated insights
    - What is the total profit of all action movies relased in 2010
- Generating Pivot table
- Tasks based on Text column
    - summarize all the movies relased this month
    - are there any re-occuring themes in the action movies relased last year
    - Compare Movie1 with Movie2


## Approaches
There are multiple options available to tackle these use cases

- [Excel CoPilot](https://techcommunity.microsoft.com/blog/excelblog/unlock-the-power-of-copilot-in-excel-now-generally-available/4242810)
- Copilot Studio
- Azure AI : Multiple options here
    - Load the Excel data into a SQL Table. Convert the User query into SQL query using LLM, execute the generated query to get result from SQL table and then post process the result along with the initial query to generate appropriate response. This can be done in two ways
        - All using Prompt engineering and AOAI SDK.
        - Leveraging AOAI function calling!! 
   - What ever we discussed in above appropach can be done by loading the excel data into Pandas data frame and using LLM to generate Pandas SQL. There are some differeces between Pandas SQL and Database SQL. 
   - Leveraging Code intepretor.  


## Contributors
* Ashish Talati
