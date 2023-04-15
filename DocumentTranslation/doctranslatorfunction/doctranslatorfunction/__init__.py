import logging
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient
import azure.functions as func


def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    source_blob_url = myblob.uri

    endpoint = os.environ["translator_endpoint"]
    key = os.environ["translator_key"]
    target_blob_url = os.environ["target_blob_url"]


    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
    logging.info("Begin Translation for: " + myblob.name)

    poller = client.begin_translation(source_blob_url, target_blob_url,  "es", source_language="nl",storage_type="File")
    logging.info(f"Created translation operation with ID: {poller.id}")
    logging.info("Waiting until translation completes...")
    result = poller.result()

    for document in result:
        logging.info(f"Document ID: {document.id}")
        logging.info(f"Document status: {document.status}")
        if document.status == "Succeeded":
            logging.info(f"Source document location: {document.source_document_url}")
            logging.info(f"Translated document location: {document.translated_document_url}")
            logging.info(f"Translated to language: {document.translated_to}\n")
        elif document.error:
            logging.info(f"Error Code: {document.error.code}, Message: {document.error.message}\n")