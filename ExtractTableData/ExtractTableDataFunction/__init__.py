import logging
import json
import os
import logging
import datetime, time
from ssl import SSLSocket
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



def generate_excel(result,filename, csvoutputstorage, csvoutputfolder, data):
    #kvp=get_key_value_pairs(result)
    formtables = {}
    blob_service_client = BlobServiceClient.from_connection_string(csvoutputstorage)
    container_client=blob_service_client.get_container_client(csvoutputfolder)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book
    merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 2})

    #with pd.ExcelWriter('filename.xlsx') as writer:
    current_page_num=None
    table_num=1
    for table in result.tables:
        column_row_spans = []
        tableList = [[None for x in range(table.column_count)] for y in range(table.row_count)] 
        confidence_score_table_list = [[None for x in range(table.column_count)] for y in range(table.row_count)] 

        for cell in table.cells:
            cellvalue=None
            if ( cell.content.find('selected') < 0) and (sum( c.isalnum() for c in cell.content) >0):
                cellvalue=cell.content
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



def generate_agg_table(result,filename, csvoutputstorage, csvoutputfolder, data):
    #kvp=get_key_value_pairs(result)
    page_titles=get_page_titles(result)
    formtables = {}
    blob_service_client = BlobServiceClient.from_connection_string(csvoutputstorage)
    container_client=blob_service_client.get_container_client(csvoutputfolder)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book
    aggr_df = pd.DataFrame()

    #with pd.ExcelWriter('filename.xlsx') as writer:
    current_page_num=None
    table_num=1
    for table in result.tables:
        column_row_spans = []
        tableList = [[None for x in range(table.column_count)] for y in range(table.row_count)] 
        num_cols=table.column_count

        header_row_span= table.cells[0].row_span
        col_span=0
        col_num=0
        desc_col=False
        if(table.cells[0].content == 'Item'):
            for cell in table.cells:
                if(cell.row_index < header_row_span ):
                    if(cell.column_index==0):
                        tableList[0][0]="Item"
                        col_span=cell.column_span
                        col_num+=1
                    elif(cell.column_index== col_span and desc_col ==False):
                        if(col_num==1):
                            tableList[0][col_span]="PartNumber"
                        elif(col_num==2):
                            tableList[0][col_span]="Description"
                            desc_col=True
                        col_span+=cell.column_span
                        col_num+=1
                    elif(cell.column_index >col_span-1 and cell.column_index < num_cols and (cell.content not in ['Quantity','Variation'] )):
                        updated_cell=cell.content.replace("Variation","").replace("Quantity","").strip().split()                    
                        if(len(updated_cell) >0):
                            i=0
                            for v in updated_cell:
                                tableList[0][cell.column_index+i]=v
                                i += 1
                else:
                    tableList[cell.row_index][cell.column_index] = cell.content
        
            if current_page_num is None:
                current_page_num = table.bounding_regions[0].page_number
            elif (current_page_num is not None) and (current_page_num == table.bounding_regions[0].page_number):
                table_num +=1
            elif (current_page_num is not None) and (current_page_num != table.bounding_regions[0].page_number):
                table_num =1
                current_page_num = table.bounding_regions[0].page_number

            print('pagenum-----'+ str(current_page_num))
            excel_sheet_name=str(current_page_num) + '_' + str(table_num)
            df = pd.DataFrame.from_records(tableList)
            #set the header row
            df.columns = df.iloc[0] 
            df = df[1:]
            #dealing with two tables in one dataframe. FR Bug
            if(len(list(filter(lambda x: 'Item' in x, df.columns))) >1):
                first_df = pd.DataFrame()
                second_df = pd.DataFrame()
                i=0
                count=0
                for col in df.columns:
                    if(col=='Item'):
                        count+=1
                    if(count==1):
                        first_df[col]=df.iloc[:,i]         
                    elif(count==2):
                        second_df[col]=df.iloc[:,i]
                    i+=1
                df = pd.DataFrame()
                df=pd.concat([df, first_df])
                df=pd.concat([df, second_df])
            
            #remove empty rows
            df = df[df.any(1)] 
            if(None in df.columns):
                df= df.drop([None], axis=1)
            df['PageNum']= current_page_num
            if(current_page_num in page_titles):
                if page_titles[current_page_num].endswith(', continued'):
                    df['Pagetitle']= page_titles[current_page_num].replace(', continued', '')
                else:
                    df['Pagetitle']= page_titles[current_page_num]
            else:
                df['Pagetitle']= 'NoPageTitle'
            #df=df[['PartNumber','PageNum']] 
            aggr_df=pd.concat([aggr_df, df])
 
            
        #write to excel only if dataframe has some data
        # if not(df.empty):
        #     df.to_excel(writer, sheet_name=excel_sheet_name, index=False)         
    if not(aggr_df.empty):
            aggr_df.to_excel(writer, sheet_name=excel_sheet_name, index=False)
    #excel output
    excelname=filename +'-AggregatedTable.xlsx'
    writer.save()
    logging.info("writing excel for : " + excelname)
    container_client.upload_blob(name=excelname,data=output.getvalue(),overwrite=True)

    return 'Aggregated table has been generated sucecssfully in Excel:' +excelname

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
                kvp[kv_pair.key] = kv_pair.value.content
    pagekvp[pagenum]=kvp
    return pagekvp

def get_page_titles(result):
    page_titles = {}
    for paragraph in result.paragraphs:
        if (paragraph.role == 'title' ) :
            page_titles[paragraph.bounding_regions[0].page_number] = paragraph.content
    return page_titles

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
    csv_output_storage = os.environ["logcomsa_STORAGE"]
    csv_output_folder = os.environ["Output_Folder"]

    output_record = analyze_document( csv_output_storage, csv_output_folder,endpoint=endpoint, key=key,  data=values)        
    result['Output'] = output_record

    return json.dumps(result, ensure_ascii=False, cls=DateTimeEncoder)

def analyze_document( csv_output_storage, csv_output_folder, endpoint, key, data):
    try:
        formUrl = data["formUrl"]
        pathname, extension = os.path.splitext(formUrl)
        #Filename location may vary across various Azure Clouds.
        filename = pathname.split('/')[4]
        document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)   
        )
        model="prebuilt-layout"
        poller = document_analysis_client.begin_analyze_document_from_url(model,formUrl)
        result = poller.result()
        table_type='individual'
        if (data["tabletype"].isspace())==False:
            table_type= data["tabletype"] 
        if(table_type == 'individual'):
            output_record = generate_excel(result,filename, csv_output_storage, csv_output_folder, data)
        elif(table_type == 'aggregate'):
            output_record = generate_agg_table(result,filename, csv_output_storage, csv_output_folder, data)
        
        

    except Exception as error:
        output_record =   "Error: " + str(error)
        

    logging.info("Output record: " + output_record)
    return output_record

        
