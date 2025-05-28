# Excel-Related Use Cases(Draft)

In many organizations, users work extensively with Excel data. This Excel file might either be the original data source or generated from a database by an application. From the user's perspective, their task typically begins with the Excel data.

## Excel Data Details

These Excel documents can be either single-sheet or multi-sheet. In some multi-sheet scenarios, the schema is consistent across all sheets (e.g., each sheet may represent data for a specific unit or quarter). These Excel files may include a variety of column types, including **text columns** that contain free-form text such as summaries, descriptions, and comments.

## Use Cases

Users may need to perform various types of tasks with Excel data to support their organizational or mission-specific objectives:

- **Extract relevant data from Excel**
  - Example: _Get me all the action genre movies directed by Clint Eastwood._

- **Extract aggregated insights**
  - Example: _What is the total profit of all action movies released in 2010?_
  - Example: _How many movies fall under each genere forthe movies released between 1990 to 2000?_


- **Generate pivot tables**
- Example: _Generate a pivot table that shows the average revenue for each movie genre_
- Example: _Create a pivot table with genres as rows and average movie revenue as values_

- **Analyze and process text columns**
  - Example: _Summarize all the movies released this month._
  - Example: _Are there any recurring themes in the action movies released last year?_
  - Example: _Compare Movie1 with Movie2._

- **Charts/Themes/insights**
- Example: _Which genres make the most money on average._
- Example: _Analyze if action movies are profitable year over year between 2000 to 2010._
## Approaches

Several approaches can be used to solve these use cases effectively:

- [**Excel Copilot**](https://techcommunity.microsoft.com/blog/excelblog/unlock-the-power-of-copilot-in-excel-now-generally-available/4242810)  
   

- **Copilot Studio**  

- **Azure AI**: Offers multiple ways to handle Excel-based use cases:
  - **SQL Table + LLM Integration**  
    - Load Excel data into a SQL table.
    - Use a large language model (LLM) to convert natural language queries into SQL.
    - Execute the generated query to retrieve results, then post-process and generate the final response leveraging LLM based on both the SQL result and the original user query.
    - This can be implemented in two ways:
      - Using prompt engineering with the Azure OpenAI SDK.
      - Using **Azure OpenAI Function Calling** for structured, programmatic task execution.
  
  - **Pandas DataFrame + LLM (Pandas SQL)**  
    - Load Excel data into a Pandas DataFrame.
    - Use an LLM to generate Pandas-compatible SQL queries.
    - Execute and interpret results within Python.
    - **Note**: Pandas SQL syntax differs slightly from traditional database SQL; be aware of these differences when designing prompts or queries.

- **Azure AI Foundry Agent Service Code Interpreter**
    - [Link](https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/code-interpreter)
    - Code Interpreter allows the agents to write and run Python code in a sandboxed execution environment. With Code Interpreter enabled, your agent can run code to generate relevant insights


    ## Use Cases
- Ashish Talati
