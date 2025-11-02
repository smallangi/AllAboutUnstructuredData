# Extract Insights from Documents


Organizations deal with various types of documents(Invoices, contracts, proposals, project related documents etc etc). These file types can be Microft Office documents, PDF, images, text files etc etc. We can categorize them as follows

- **Structured**: fixed layout & fields; predictable schema. Examples: W2, Invoices, DoD DD-250 (Material Inspection & Receiving Report). etc
- **Semi Structured**: Tables, Key Value pairs with paragraph text. Examples: Earning Reports, Emails etc
- **Un Structured**: Free-form content with minimal predictable structure. Examples:Agreements, Contracts etc

## Common Scenarios based on documents

Organizations typically interact with documents through several key use cases:
- **Document Discovery**: Locating relevant documents within large repositories
- **Question Answering**: Finding specific information to answer targeted queries
- **Analytics and Reporting**: Extracting data for business intelligence and decision-making
- **Automated Workflows**: Integrating document processing into business processes

## Insights extraction

For each of these use cases, there is one critical common task. That is extracting stcture(insights) from these documents. These insights could be

- **Document Structure** : Sections and Headings. Essential for creating contextual chunks in RAG (Retrieval-Augmented Generation) applications
- **Table related data** : Column and row dat afrom tables defined. Essential for RAG applications(if you need chatbot to answer questions based on the tabular data) and analytics based use cases
- **Key-Value Pairs** : IDs, names, dates, addresses, contacts, amounts/currency, item details, including checkboxes, yes/no options.  
- **Derived Insights** : Deriving insight based on the information in the document. Ex: Classification, tagging etc
- **Document Structure** : 

## Technical Challenges in extracting relevant insights

Document insight extraction faces several technical hurdles that require sophisticated solutions:

### Mixed Content Types
**Scanned Documents**: Legacy documents converted to digital format often contain embedded images alongside text, requiring both OCR (Optical Character Recognition) and image analysis capabilities.

**Hybrid Digital Documents**: Modern documents frequently combine formatted text with charts, diagrams, and photographs. Comprehensive insight extraction demands processing both textual and visual elements.

### Complex Layout Structures
**Multi-Page Tables**: Financial reports and technical specifications often contain tables spanning multiple pages, requiring advanced parsing to maintain data relationships and structure.

**Dynamic Formatting**: Documents from different sources(vendors) may use varying layouts, fonts, and organizational structures, even when covering similar topics.

### Data Quality and Accuracy
**OCR Limitations**: Scanned documents may contain recognition errors, faded text, or poor image quality affecting extraction accuracy.

**Context Preservation**: Maintaining semantic relationships between document elements during extraction is crucial for meaningful analysis.


Now how can one extract the relevant insights from these various types of documents!!!!
## Azure AI Services
Azure provides a comprehensive suite of AI services designed to address document processing challenges through multiple complementary approaches.

- Azure Document intelligence
- Large Language Models
- Azure Content Understanding(Note: Not available in Azure Government yet)

## Implementation Approaches


###  Approach 1: Document Intelligence Only
Extract text using document inteliggence models and parse the info to get what you need!
- Utilizes pre-built models for common document types
- Custom model training for organization-specific formats
- Direct extraction of key-value pairs and tables
- Lower cost for high-volume processing
**Best For**: Structured and semi-structured documents with predictable layouts
- **High OCR Accuracy**: Excellent text recognition even from scanned or low-quality documents

###  Approach 42: Document Intelligence + LLM
1. **Text Extraction**: Azure Document Intelligence extracts text and layout information
2. **Markdown Conversion**: Structured text representation preserving document hierarchy
3. **Insight Generation**: Azure OpenAI processes markdown using structured outputs to extract specific insights
4. **Schema Validation**: Ensures consistent output format across different document types
**Best For**: Documents requiring semantic understanding and context analysis

###  Approach 3: Multi-Modal Image Processing
Generate Images of the file(using PDF2Image or PYmuPDF). Using Azure OpenAI's structured outputs extract the required insights from the attached images
1. **Image Generation**: Convert documents to high-quality images using PDF2Image or PyMuPDF
2. **Visual Analysis**: Azure OpenAI Vision processes images to extract text and visual insights
3. **Structured Extraction**: Generate JSON outputs with predefined schemas
4. **Quality Control**: Validate extracted information for accuracy and completeness
**Best For**: Documents with critical visual elements (charts, diagrams, handwritten notes)


### Approach 4: Comprehensive Multi-Modal Processing
1. **Parallel Processing**: Simultaneously process text and visual elements. Combine 3rd and 4th approaches
2. **Content Fusion**: Combine insights from both processing streams(Text from document inntelligence and Image(s) of the document)
3. **Validation and Reconciliation**: Cross-reference text and visual insights for accuracy
4. **Unified Output**: Generate comprehensive document analysis with both text and image!
**Best For**: Complex documents requiring both textual and visual analysis

### Approach 5: Advanced Content Understanding *(Preview)*
Not yet available in Azure Gov!

Code for all the above approaches will be added soon!

## Lessons Learned

### LLM - Image related issues
We mainly played with GPT models(gpt-4o-mini, gpt-4o and gpt-4.1). 
- gpt-4o-mini's OCR accuracy is very low. we ran into several accuracy issues with high quality images too. 
- gpt-4o is lot better than gpt-4o-mini when it comes to OCR accuracy. We ran into much fewer OCR errors.
- gpt-4.1 is much better than gpt-4o. So far with our limited testing, we did not run into any issues. 

### Limitations on Image size that can be sent to GPT models
There is limitation in number and total size of images one can be send to GPT models. This may vary  from GPT model to model. For the gpt-4o-mini, gpt-4o and gpt-4.1 models, 20MB per image, with a max of 10 images per request. Details [here](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/gpt-with-vision)

Note: There is price for Image input tokens too. Details [here](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/overview#image-input-tokens)

### Size of image generated
We played with both with PDF2Image or PyMuPDF. PDF2Image gives only one option: dpi. PyMuPDF gives two options to generate image(dpi and zoom). Following are based on tests with PyMuPDF 
- with default dpi: Image size- 99.3KB   , Image dimensions- 612*792
- with 300 dpi: Image size- 552KB   , Image dimensions- 2550*3300
- with Zoom 2*2 : Image size- 248KB   , Image dimensions- 1836*2376

We saw better results with higher resolution(What were we thinking 😄 ). with our limited testing, 300dpi seems to be the sweet spot!! 

## Contributors
- Mary Wahl
- James Croft
- Narasimhan Kidambi
- Trey Logel

