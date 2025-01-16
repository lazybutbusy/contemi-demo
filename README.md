# Contemi-Demo

## Step 1: Crawl website
Run the following script:
```
python crawl_website.py
```

## Step 2: Add OpenAI key
Set the OpenAI API key by running:
```
export OPENAI_API_KEY="sk-..."
```

## Step 3 (Optional): Build Graph-RAG
*Note: This step is optional because the graph has already been built.*
Use the LightRAG library ([GitHub link](https://github.com/HKUDS/LightRAG)) and run:
```
python graph-rag.py
```

## Step 4: Deploy API-server
Based on the Ollama server, run:
```
python server.py
```

## Step 5: Deploy UI
Using Open-WebUI, install it from [Open-Webui]([https://ollama.com/download/linux](https://github.com/open-webui/open-webui)), then run:
```
open-webui serve
```

## Step 6: Connect UI to API-server
1. Open your browser and go to: `http://localhost:8080`
2. In the UI, navigate to: `Setting > Admin Settings > Connections > Ollama API`
3. Add the following URL: [http://localhost:8082/ollama](http://localhost:8082/ollama)
