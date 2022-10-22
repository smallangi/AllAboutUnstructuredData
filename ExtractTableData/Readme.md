This function extract Table data using Form Recognizer and generate Excel with all the tables. 

* Each table on a page gets stored to a sheet in the Excel document. Sheet name corresponds to page number in the document
* Sometimes there are key value pairs on the page that needs to be captured in the table. If you need that feature leverage the add_key_value_pairs flag
* Form recognizer extracts column and row spans. We took advantage of it to present the data as it is represented in the table. 



# Extable table by table into Excel    

The function requires the `FORMS_RECOGNIZER_ENDPOINT` and `FORMS_RECOGNIZER_KEY` property set in the appsettings to the appropriate Form Recognizer resource endpoint and key.

To deploy the function:
1. In the Azure portal, create a Forms Recognizer resource.

