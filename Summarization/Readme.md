# Summarization 

There are two types of Summarization scenarios
1. Generic summarization. This is all about going through the entire document and giving overall summary.
2. Insights based summary. In this case, it is about generating summary around specific insights from the document. Ex: Generating summary based on risks or issues identified in the document. 

In the first case you can leverage generic summarization template available out there and customize a bit to get what you need. For the second scenario, you would need to spend time on the prompt template to get what you need. 

Genering summary for large documents can be a tricky. Folliwng are the approaches one can take to generate summary. First three are well documented here https://python.langchain.com/docs/use_cases/summarization . There are many articles that talk pro/cons of these 3 approaches. Followinag are some of the main points based on my research and expriences 

1. Stuff 
    * This is the best option, if the text is with in token limit of the LLM model.
    * Some times you have an option to remove unnecessary text from the document to get the total text within the token limit. 
2. Map Reduce
    * When Stuff approach is not feasible, this seems to be a popular option. This is because it is faster than Refine. With Map Reduce approach you are processing document chunks in parallel as opposed to sequential in Refine approach. 
    * Note that some information may be lost during final call(merging all generated summaries into final one). You have two prompt templates. One for the individual chunks and one for final merge. Pay attention to the merge(reduce) prompt template.
    * Chunkin strategy also makes strong impact here. Chunking based on specif token count may lose important context. Best is to chunk at section level. Leverage Azure Document Intelligence's layout model for this. 
3. Map Rerank
    * This is similar to Map Reduce from "Map" approach perpsective but vary afterwards. 
    * Document is chunked and summary is generated for each chunk along with a confidence score. In second step you will use the confidence scores to prioritize the summaries and generate final summary.
    * This approach is maily relevnt when you are extracting insights (or an answer) from the document
4. Refine
    * It can retrieve and incorporate more relevant context compared to Map Reduce approach.
    * Note that this takes more time as the chunks are processed sequentially. This is the biggest draw back if you have too many chunks to process. 
    * follow the same chunking strategy as mentioned above
4. Chain of Density
    * This is based on this research paper https://arxiv.org/abs/2309.04269
    * This is maily meant for the Generic Summarization scenario mentioned above. 
    * It generates high quality enity-dense summary. Definetely check it out. 
    * GPT-4 worked out well compared to GPT3.5 in this case. 
5. Best Representation Vectors
    * This is detailed here https://pashpashpash.substack.com/p/tackling-the-challenge-of-document
    * At high level the approach is
        * Document is spllit into multiple chunks(use sections to chunk) and vectorize the chunks
        * Use K-means clustering to identify key topic clusters within these vectors
        * The representative vectors of these clusters are sequentially sorted by where they appear in the document and fed into an LLM to generate a cohesive and comprehensive summary
    * Cost effective as you make a single call to LLM    
6. RAG Approach
    * This is helpful when you are generating summary on specific topic/theme and the relevant text is in multiple docuents.
    * Note that you need to pass on all relevant chunks from documents to generate quality summary.   


