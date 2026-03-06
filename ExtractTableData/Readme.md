# Extract Table Data from Forms 

Documents can contain Table data. Example: Earning reports, Purchase order forms, Technical and Operational manuals etc contain critical data in tables. You may need to extract this table data into Excel for various scenarios. 
* Extract each table into a specific worksheet in Excel
* Extract the data from all the similar tables and aggregate that data into single table

 This function extract Table data using Form Recognizer's built in model and generate Excel file with all the extracted tables. Following is the expected behavior

* Each table on a page gets extracted and stored to a sheet in the Excel document. Sheet name corresponds to page number in the document. 
* Sometimes there are key value pairs on the page that needs to be captured in the table. If you need that feature leverage the add_key_value_pairs flag
* Form recognizer extracts column and row spans. We took advantage of it to present the data as it is represented in the actual table. 



# Deployment    


To deploy the function:
1. Create a Forms Recognizer resource.
2. Copy the form recognizer URL and key for use in the appsettings.
3. Clone this repository
4. Open the ExtractTableData folder in VS Code and deploy the function.
5. Once the function is deployed, set the required application settings 
    * FORMS_RECOGNIZER_ENDPOINT  
    * FORMS_RECOGNIZER_KEY
    * output_storage_acct : Connection string to the Azure Storage account where you want to store the Excel output.
    * excel_output_folder : Azure Blob Storage destination for the generated Excel files. This is an **application setting** (environment variable), **not** a request body parameter. Use the format `<container>` or `<container>/<folder>`. Examples:
        * `forms` → stores the Excel file directly in the **"forms"** container (blob name: `myfile.xlsx`)
        * `forms/output` → stores the Excel file inside the **"output"** virtual folder of the **"forms"** container (blob name: `output/myfile.xlsx`)
        * `forms/2024/reports` → stores the Excel file inside the **"2024/reports"** virtual folder of the **"forms"** container (blob name: `2024/reports/myfile.xlsx`)

    > **Note:** Make sure the container (the first part before any `/`) already exists in your storage account before running the function.



## Sample Input for the function:

The request body accepts the following parameters. **`excel_output_folder` is NOT a request body parameter** — it must be configured as an application setting (see deployment steps above).

```json
{
    "formUrl": "https://<storage-account>.blob.core.windows.net/<container>/<document>",
    "tabletype": "individual",
    "addkeyvaluepairs": "True"
}
```
Input Parameters: 
* formUrl : The URL of the document to be processed. The document must be accessible from the function (e.g. a blob URL with a SAS token or public access).
* tabletype : The only supported value as of now is "individual". Plan is to add support for "aggregated" table that aggregates the data from all the tables in the document assuming that all the tables are similar.
* addkeyvaluepairs : Some times the page that contains the table might have Key Value pairs and we need to add them to the table. If that is the case set the value of addkeyvaluepairs to True, else set it to False.

## [Sample data](./SampleData)
We provided two sample documents to play with. 
* PurchaseOrderForm.pdf . This document has key value pairs for each table that makes sense to capature that as part of the table
    *  PurchaseOrderForm-WithKeyValuePairs.xlsx --> This is the output with addkeyvaluepairs set to True
    *  PurchaseOrderForm-WithKeyValuePairs.xlsx --> This is the output with addkeyvaluepairs set to False
* earningreport.pdf . This document does not have key value pairs for each table that makes sense to capture.
    * earningreport.xlsx -> This is the output with addkeyvaluepairs set to False

## Note

* If there is a page with no tables, no sheet will be created for that page
* Removed check box extrcated text (":selected:", ":unselected:") from the table. Update the code to reflect different behaviour. 
* if the cell does not have any alpha numeric text, skipped the cell. Update the code to reflect different behaviour. 

## How to leverage this
* leverage this to generate Excel file with the required table data
* Integrate this with Power Automate so that end users can use this seamlessely from O365(Email, SharePoint or Teams)
* You can also customize this to generate aggregated table 
