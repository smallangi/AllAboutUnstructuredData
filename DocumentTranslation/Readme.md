# Translate documents using Azure Document Translation

Azure Document Translation service enables the translation of multiple and complex documents across all supported languages and dialects while preserving the original document structure and data format. However, it currently does not support the translation of text from images in digital documents. To address this, there are two options:
* Convert the digital document into a scanned document in its entirety.
* Split the document into two files and process them separately:
    * One file containing all pages that only have text. The digital pages are preserved in their original form. The Document Translation service takes advantage of the structure/layout information from the digital text page and translates it more accurately than a scanned page.
    * The second file will contain a scanned version of all the pages that contain images. 
    * Note: As we have processed these files by parsing the original document page by page, we have the required information to stitch the translated documents into a single translated document. This codebase does not have that code. We will add that code in the near future. If you have the time to help, please let us know.

## Dealing with various File Types  
You will need to handle different file types as follows:
* PDF
    * Scanned PDF:You do not need to do anything. Translator service translates all the text from the scanned pages.
    * Digital PDF: As mentioned earlier, the Translator service does not translate text from images, but it can translate the remaining text.
    * This solution analyzes each page and creates multiple files based on the content on each page (text only page, text plus image page, image only page, etc.). You can configure this behavior through various parameters. The following files will be created:
        * A copy of the original file as is.
        * A scanned version of the whole document.
        * Two other files: One containing all pages that only have text, and a second file with a scanned version of all the pages that contain image(s).
        * Note: The Azure Document Translator has a limit of 40MB per document. The scanned version of the file is typically larger. Therefore, we split the scanned document into multiple files based on the number of pages (configurable).
* Image Files(BMP,PNG,JPG)
    * We need to convert these files into PDF, and this solution takes care of it.
* Office files (Word, Powerpoint, Excel)
    * The Translator service handles these files in the same way as PDF, meaning it does not translate text from images but translates the remaining text. Therefore, we need to convert/process these files in the same way as PDF. One approach is to convert office files into PDF and leverage the solution we have for PDF. 
    * There are several open-source Python packages available to convert office documents, but some of them require Microsoft Office to be installed on the machine where the code runs. You can explore the following options
        * https://pypi.org/project/aspose-words/
        * https://github.com/AlJohri/docx2pdf
        * You can also leverage Power Apps, as long as the files are stored in OneDrive.



## Solution Approach  
We followed the approach outlined below and have shared all the code in this repository:
![Document Translator solution approach](images/document-translator-workflow.jpg)

Both the functions are [triggered using an event subscription from the storage container.](https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger?pivots=programming-language-python)

## Document Convertor Function

There are multiple python packages that convert digital PDF to Scanned version of PDF. We have played with PyMuPDF and  pdf2image python packages. For each of those packages, we shared the code for Azure functions based on them. 

* The pdf2image function requires Docker because we need to install Poppler utils, which is not available as a Python package. This function only supports converting the PDF document to a scanned version.
* The PyMuPDF-based function has extensive functionality and configurable options. The following are the configurations available:
    * "translatordocs_storage": storage connection string for input and converted data.
    * "pdf_conversion": options include "all", "scanned", "original", or "hybrid".
        * "scanned": creates a scanned version of the document. The name of the scanned file will have "--scanned" appended to the original file.
        * "original": copies the original document.
        * "hybrid":
            * For pages with text-only data, create a file with the digital copy of the pages. The name of the text pages file will have "--textonlyPage" appended to the original file. Note that if the document has no pages with only text, this file will not be created.
            * For pages with images or images and text, create a file with the scanned version of the pages. The name of the image pages file will have "--ImagePages" appended to the original file. Note that if the document has no pages with images, this file will not be created.
        * hybrid: 
            * For pages with text only data, create a file with the digital copy of the pages. Name of the text pages file will have "--textonlyPage" appended to original file. Note that if the document has no pages with only text, this file will not be created.
            * For pages with images or images and text, create a file with the scanned version of the pages. The name of the image pages file will have "--ImagePages" appended to the original file. Note that if the document has no pages with images, this file will not be created.
        * "all": creates all of the above. 
    * "pdf_page_limit": the number of pages in one file for the scanned version.
        * There is a limit of 40MB per file for Azure Document Translator. Adjust this page number based on the type of PDF files you are dealing with.
    * "output_container_name": the output container for converted documents.

### Note
* Hybrid is the best option. This is because Translator can translate digital pages better than images as it can get the proper word block and full layout information. 
* As we process the original file page by page, we can create a mapping file that defines the mapping of the original document page to the converted document's pages (image pages and text-only pages documents). We can use this mapping to stitch these documents and generate the final translated document. However, we have not yet had the opportunity to take care of this. Hopefully, we will find some time soon to complete this task. 

## Document Translator Function

This is a simple function that takes a document and submits it to the Translator service. The Translator service stores the translated document in the specified container.
The following are the configurations: 
* "converteddocs_storage": "storage connecttion string for input documents",,
* "translator_endpoint":"translator service endpoint",
* "translator_key":"translator key",
* "target_blob_url":"target blob url for translated output"

### Note
* Currently, we have hardcoded the target language. You can make it a configurable option.
* We are also leveraging the auto-language detection by the Translator service to identify the source language. You can get better accuracy if you specify the source language. [Refer this link] (https://learn.microsoft.com/en-us/azure/cognitive-services/translator/document-translation/faq#should-i-specify-the-source-language-in-a-request) 
* We generate multiple files when we are dealing with large documents, as mentioned above. Therefore, you need to merge them into a single file. 

## Deployment    

To deploy this solution, follow these steps:
1. Create an Azure Translation Service.
2. Create a Storage account to store the original, converted, and translated documents.
3. Create Azure Functions based on the source code from this repository. [Refer to this article to create functions that leverage storage container's event subscription ](https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger?pivots=programming-language-python)

## Contributors
+ Brandon Rohrer 
+ Krishna Doss Mohan 
+ Narasimhan Kidambi
+ [Nicolas Uthurriague](https://github.com/puthurr)
+ Sreedhar Mallangi 
