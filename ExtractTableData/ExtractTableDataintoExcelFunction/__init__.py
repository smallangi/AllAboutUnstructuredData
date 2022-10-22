import logging
import json
import os
import logging
import datetime, time
from json import JSONEncoder
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import pandas as pd
import io



class DateTimeEncoder(JSONEncoder):
    #Override the default method    
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()



def generate_excel(result,filename, csvoutputstorage, csvoutputfolder, add_keyvalue_pairs):
    if(add_keyvalue_pairs):
        kvp=get_key_value_pairs(result)
    formtables = {}
    blob_service_client = BlobServiceClient.from_connection_string(csvoutputstorage)
    container_client=blob_service_client.get_container_client(csvoutputfolder)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book
    merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 2})

    current_page_num=None
    table_num=1
    for table in result.tables:
        column_row_spans = []
        tableList = [[None for x in range(table.column_count)] for y in range(table.row_count)] 

        for cell in table.cells:
            cellvalue=None
            #only add the cell data if it has some alphanumeric text
            if  (sum( c.isalnum() for c in cell.content) >0):
                #replace selection marks data
                cellvalue=cell.content.replace(":unselected:", "").replace(":selected:", "")
                if(cell.row_span>1 and cell.column_span>1):
                    column_row_spans.append([cell.row_index, cell.column_index, cell.row_index+cell.row_span-1,cell.column_index+cell.column_span-1, cellvalue ])
                elif(cell.row_span>1 and cell.column_span==1):
                    column_row_spans.append([cell.row_index, cell.column_index, cell.row_index+cell.row_span-1,cell.column_index, cellvalue ])
                elif(cell.column_span>1 and cell.row_span==1):
                    column_row_spans.append([cell.row_index, cell.column_index, cell.row_index,cell.column_index+cell.column_span-1, cellvalue ])
                    
            tableList[cell.row_index][cell.column_index] = cellvalue
        
        if current_page_num is None:
            current_page_num = table.bounding_regions[0].page_number
        elif (current_page_num is not None) and (current_page_num == table.bounding_regions[0].page_number):
            table_num +=1
        elif (current_page_num is not None) and (current_page_num != table.bounding_regions[0].page_number):
            table_num =1
            current_page_num = table.bounding_regions[0].page_number


        excel_sheet_name=str(current_page_num) + '_' + str(table_num)
        df = pd.DataFrame.from_records(tableList)
        #set the header row
        df.columns = df.iloc[0] 
        df = df[1:]
        #remove empty rows
        df = df[df.any(1)]        
        #write to excel only if dataframe has some data
        if not(df.empty):
            if(add_keyvalue_pairs and current_page_num in kvp ):
                for key in kvp[current_page_num]:
                    if not(key in df.columns ):
                        df[key]= kvp[current_page_num][key]
            df.to_excel(writer, sheet_name=excel_sheet_name, index=False)
            worksheet = writer.sheets[excel_sheet_name]
            if( len(column_row_spans) >0):  
                for x in column_row_spans:
                    worksheet.merge_range(x[0],x[1],x[2],x[3],x[4], merge_format)


    #excel output
    excelname=filename +'.xlsx'
    writer.save()
    logging.info("writing excel for : " + excelname)
    container_client.upload_blob(name=excelname,data=output.getvalue(),overwrite=True)

    return 'Individual table per sheet has been generated sucecssfully in Excel:' +excelname




def get_key_value_pairs(result):
    kvp = {}
    pagekvp = {}
    pagelen= len(result.pages)
    pagenum=None
    currpagenum=None
    for kv_pair in result.key_value_pairs:
        if pagenum is None:
            pagenum=kv_pair.key.bounding_regions[0].page_number
        elif (pagenum is not None) and (pagenum != kv_pair.key.bounding_regions[0].page_number):
            pagekvp[pagenum]=kvp
            kvp = {}
            pagenum=kv_pair.key.bounding_regions[0].page_number

        if kv_pair.key:
            if kv_pair.value:
                kvp[kv_pair.key.content] = kv_pair.value.content
    pagekvp[pagenum]=kvp
    return pagekvp



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Invoked Table extraction function...')
    try:
        body = json.dumps(req.get_json())

        if body:
            logging.info(body)
            result = compose_response(body)
            logging.info("Result to return: " + result)
            return func.HttpResponse(result, mimetype="application/json")
        else:
            return func.HttpResponse(
                "Invalid body",
                status_code=400
            )
    except ValueError:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )
def compose_response(json_data):
    values = json.loads(json_data)
    
    # Prepare the Output before the loop
    result = {}
    #result["output"] = []

    endpoint = os.environ["FORMS_RECOGNIZER_ENDPOINT"]
    key = os.environ["FORMS_RECOGNIZER_KEY"]
    output_storage_acct = os.environ["output_storage_acct"]
    excel_output_folder = os.environ["excel_output_folder"]

    output_record = analyze_document( output_storage_acct, excel_output_folder,endpoint=endpoint, key=key,  data=values)        
    result['Output'] = output_record

    return json.dumps(result, ensure_ascii=False, cls=DateTimeEncoder)

def analyze_document( output_storage_acct, excel_output_folder, endpoint, key, data):
    try:
        formUrl = data["formUrl"]
        pathname, extension = os.path.splitext(formUrl)
        #Filename location may vary across various Azure Clouds.
        filename = pathname.split('/')[4]
        document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)   
        )
        model="prebuilt-document"
        poller = document_analysis_client.begin_analyze_document_from_url(model,formUrl)
        result = poller.result()
        table_type='individual'
        add_keyvalue_pairs = False
        if(data["addkeyvaluepairs"] == "True"):
            add_keyvalue_pairs = True

        if (data["tabletype"].isspace())==False:
            table_type= data["tabletype"] 
        if(table_type == 'individual'):            
            output_record = generate_excel(result,filename, output_storage_acct, excel_output_folder, add_keyvalue_pairs)
        else:
            output_record = "This function only support individual table per page asof now. Goal is to add aggregated table feature soon"
        
        

    except Exception as error:
        output_record =   "Error: " + str(error)
        

    logging.info("Output record: " + output_record)
    return output_record

        
