import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings, BlobSasPermissions
import os
from pdf2image  import convert_from_path, convert_from_bytes
import img2pdf
from PIL import Image
import io
from datetime import datetime, timedelta


def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    
    filename=os.path.basename(myblob.name)
    filename_noextension=filename.split('.')[0]
    logging.info("Starting the process for :" + filename)
    scannedpdf_output_storage = os.environ["smlangtranslationsa_STORAGE"]
    scannedpdf_output_container = os.environ["scannedpdf_output_container"]

    blob_service_client = BlobServiceClient.from_connection_string(scannedpdf_output_storage)


    
    
    logging.info("Start: PDF to Image conversion")
    pages = convert_from_bytes(myblob.read())
    logging.info("Done: PDF to Image conversion")
    image_bytes = []
    file_part=1
    page_num=1
    file_inprocess=True
    container_client=blob_service_client.get_container_client(scannedpdf_output_container)
    content_settings = ContentSettings(content_type='application/octet-stream')
    for page in pages:      
        with io.BytesIO() as output:
            page.save(output, 'JPEG')
            image_bytes.append(output.getvalue())
            file_inprocess=True

        if( (page_num % 130) ==0):
            logging.info("start: Image to PDF")
            pdf_bytes = img2pdf.convert(image_bytes)
            logging.info("End: Image to PDF")
            logging.info("start: Upload scanned Doc")
            container_client.upload_blob(name=filename_noextension+"-Part" +str(file_part)+".pdf",data=pdf_bytes,overwrite=True, content_settings=content_settings)
            logging.info("Done: Upload scanned Doc")
            image_bytes = []
            file_inprocess=False
            file_part +=1      
            
        page_num +=1
        
    if(file_inprocess==True):
        logging.info("start: Image to PDF")
        pdf_bytes = img2pdf.convert(image_bytes)
        logging.info("End: Image to PDF")
        logging.info("start: Upload scanned Doc")
        container_client.upload_blob(name=filename_noextension+"-Part" +str(file_part)+".pdf",data=pdf_bytes,overwrite=True, content_settings=content_settings)
        logging.info("Done: Upload scanned Doc")

    logging.info("Done: Completed creating Scanned doc: " + filename)