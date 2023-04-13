import logging

import azure.functions as func
import fitz
import os
from PIL import Image
from pptx import Presentation
from azure.storage.blob import BlobServiceClient
import io
import sys


def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    filename=os.path.basename(myblob.name)
    file_name=filename.split('.')[0]
    file_type=filename.split('.')[1].lower()
    logging.info("Starting the process for :" + filename)


    #scanned, hybrid, original
    pdf_conversion=os.environ["pdf_conversion"]
    pdf_page_limit=os.environ["pdf_page_limit"]

    #scanned, original
    office_conversion="scanned"

    scannedpdf_output_storage = os.environ["transv2sa_STORAGE"]
    output_container_name = os.environ["output_container_name"]
    blob_service_client = BlobServiceClient.from_connection_string(scannedpdf_output_storage)
    container_client=blob_service_client.get_container_client(output_container_name)
 
    if(file_type == "pdf"):
        #Open PDF file
        pdf_file = fitz.open("pdf", myblob.read())
        #Get the number of pages in PDF file
        page_nums = len(pdf_file)
        page_num=0
        num_only_text=0
        num_only_image=0
        num_text_image=0
        num_blank=0
        
        if(pdf_conversion in[ "all", "scanned"]):
            logging.info("Processing PDF: Scanned Option")

            new_doc_textimages = fitz.open()
            file_part=1
            #Extract all images information from each page
            for page_num in range(page_nums):
                page = pdf_file[page_num]
                file_inprocess=True
                logging.info("Page Num::::::-------------------------------------------"+ str(page_num+1))
                if(len(page.get_text()) >0 and len(page.get_images())==0):
                    logging.info("Only text and no Images")
                    num_only_text +=1
                elif(len(page.get_text()) ==0 and len(page.get_images())>0):
                    logging.info("Only Images and no Text")
                    logging.info("No of Images on the page:"+ str(len(page.get_images())))
                    num_only_image +=1
                elif(len(page.get_text()) ==0 and len(page.get_images())==0):
                    logging.info("Blank Page")
                    num_blank +=1
                elif(len(page.get_text()) >0 and len(page.get_images())>0):
                    logging.info("Text Plus Image")
                    logging.info("No of Images on the page:"+ str(len(page.get_images())))
                    num_text_image +=1
                #create image of the page and add it to new doc
                pix = page.get_pixmap(dpi=200)
                opage = new_doc_textimages.new_page(width=page.rect.width, height=page.rect.height)
                opage.insert_image(opage.rect, pixmap=pix)
                if( ( (page_num+1) % int(pdf_page_limit)) ==0): 
                    pdf_bytes=new_doc_textimages.convert_to_pdf()
                    blob_client = container_client.get_blob_client(file_name +"--scanned-Part" +str(file_part)+".pdf")
                    blob_client.upload_blob(pdf_bytes, overwrite=True)
                    new_doc_textimages = fitz.open()
                    file_inprocess=False
                    file_part +=1
            
            if(file_inprocess==True):
                pdf_bytes=new_doc_textimages.convert_to_pdf()
                #following creates large file
                # pdf_bytes=new_doc_textimages.tobytes()
                blob_client = container_client.get_blob_client(file_name +"--scanned-Part" +str(file_part)+".pdf")
                blob_client.upload_blob(pdf_bytes, overwrite=True)
            new_doc_textimages.close()

        if(pdf_conversion in[ "all", "original"]):
            logging.info("Processing PDF: Original doc Option")
            for page_num in range(page_nums):
                page = pdf_file[page_num]
                logging.info("Page Num::::::-------------------------------------------"+ str(page_num+1))
                if(len(page.get_text()) >0 and len(page.get_images())==0):
                    logging.info("Only text and no Images")
                    num_only_text +=1
                elif(len(page.get_text()) ==0 and len(page.get_images())>0):
                    logging.info("Only Images and no Text")
                    logging.info("No of Images on the page:"+ str(len(page.get_images())))
                    num_only_image +=1
                elif(len(page.get_text()) ==0 and len(page.get_images())==0):
                    logging.info("Blank Page")
                    num_blank +=1
                elif(len(page.get_text()) >0 and len(page.get_images())>0):
                    logging.info("Text Plus Image")
                    logging.info("No of Images on the page:"+ str(len(page.get_images())))
                    num_text_image +=1
            #copy the original doc to output folder
            destination_blob_client = blob_service_client.get_blob_client(output_container_name, filename)
            destination_blob_client.start_copy_from_url(myblob.uri)

            # Wait for the copy operation to complete
            destination_blob_properties = destination_blob_client.get_blob_properties()
            while destination_blob_properties.copy.status != 'success':
                destination_blob_properties = destination_blob_client.get_blob_properties()
            logging.info(f'File {filename} copied successfully to container {output_container_name} as {filename}')
        
        if(pdf_conversion in[ "all", "hybrid"]):
            logging.info("Processing PDF: Hybrid Option")      
            new_doc_textonly = fitz.open()
            new_doc_textimages = fitz.open()
            page_num=0
            num_only_text=0
            num_only_image=0
            num_text_image=0
            num_blank=0
            file_part=1
            
            #Extract all images information from each page
            for page_num in range(page_nums):
                page = pdf_file[page_num]
                file_inprocess=True
                logging.info("Page Num::::::-------------------------------------------"+ str(page_num+1))
                if(len(page.get_text()) >0 and len(page.get_images())==0):
                    logging.info("Only text and no Images")
                    num_only_text +=1
                    new_doc_textonly.insert_pdf(pdf_file, from_page = page_num, to_page = page_num)
                elif(len(page.get_text()) ==0 and len(page.get_images())>0):
                    logging.info("Only Images and no Text")
                    logging.info("No of Images on the page:"+ str(len(page.get_images())))
                    num_only_image +=1
                    pix = page.get_pixmap(dpi=200)
                    opage = new_doc_textimages.new_page(width=page.rect.width, height=page.rect.height)
                    opage.insert_image(opage.rect, pixmap=pix) 
                elif(len(page.get_text()) ==0 and len(page.get_images())==0):
                    logging.info("Blank Page")
                    num_blank +=1
                    new_doc_textonly.insert_pdf(pdf_file, from_page = page_num, to_page = page_num)
                elif(len(page.get_text()) >0 and len(page.get_images())>0):
                    logging.info("Text Plus Image")
                    logging.info("No of Images on the page:"+ str(len(page.get_images())))
                    num_text_image +=1
                    pix = page.get_pixmap(dpi=200)
                    opage = new_doc_textimages.new_page(width=page.rect.width, height=page.rect.height)
                    opage.insert_image(opage.rect, pixmap=pix) 
                if (( (num_text_image+num_only_image) !=0 ) and ( ( (num_text_image+num_only_image) % int(pdf_page_limit)) ==0) ):
                    pdf_ti_bytes=new_doc_textimages.convert_to_pdf()
                    blob_client = container_client.get_blob_client(file_name +"--ImagePages"+str(file_part)+".pdf")
                    blob_client.upload_blob(pdf_ti_bytes,overwrite=True)
                    new_doc_textimages = fitz.open()
                    file_inprocess=False
                    file_part +=1
            
            if(new_doc_textimages.page_count >0 and file_inprocess==True):
                pdf_ti_bytes=new_doc_textimages.convert_to_pdf()
                blob_client = container_client.get_blob_client(file_name +"--ImagePages"+str(file_part)+".pdf")
                blob_client.upload_blob(pdf_ti_bytes,overwrite=True)
            new_doc_textimages.close()

            if(new_doc_textonly.page_count >0):
                pdf_to_bytes=new_doc_textonly.tobytes(garbage=3, deflate=True)
                blob_client = container_client.get_blob_client(file_name +"--textonlyPages.pdf")
                blob_client.upload_blob(pdf_to_bytes,overwrite=True)
            new_doc_textonly.close()

            

        print ("Num of Text Only Pages:::" + str(num_only_text))
        print ("Num of Image Only Pages:::" + str(num_only_image))
        print ("Num of Text and Image Pages:::" + str(num_text_image))
        print ("Num of Blank Pages:::" + str(num_blank))


    elif(file_type in[ "html", "xlsx","mp4","docx","pptx","doc"]):
        logging.info("Processing -- " + file_type )
        #copy the original doc to output folder
        destination_blob_client = blob_service_client.get_blob_client(output_container_name, filename)
        destination_blob_client.start_copy_from_url(myblob.uri)

        # Wait for the copy operation to complete
        destination_blob_properties = destination_blob_client.get_blob_properties()
        while destination_blob_properties.copy.status != 'success':
            destination_blob_properties = destination_blob_client.get_blob_properties()

        logging.info(f'File {filename} copied successfully to container {output_container_name} as {filename}')

    elif(file_type in[ "jpg", "bmp","png"]):
        logging.info("Processing image file")
        #img_file = fitz.open(file_path)
        img_file = fitz.open(file_type, myblob.read())
        new_pdf = fitz.open()
        for page in img_file:
            pix = page.get_pixmap(dpi=200)
            opage = new_pdf.new_page(width=page.rect.width, height=page.rect.height)
            opage.insert_image(opage.rect, pixmap=pix) 
        
        pdf_bytes=new_pdf.convert_to_pdf()
        blob_client = container_client.get_blob_client(file_name +".pdf")
        blob_client.upload_blob(pdf_bytes,overwrite=True)
        new_pdf.close()


 







