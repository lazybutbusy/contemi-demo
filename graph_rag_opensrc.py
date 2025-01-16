import os
from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete, gpt_4o_complete
from lightrag.llm import ollama_model_complete, ollama_embedding
from lightrag.utils import EmbeddingFunc
import glob

#########
# Uncomment the below two lines if running in a jupyter notebook to handle the async nature of rag.insert()
# import nest_asyncio
# nest_asyncio.apply()
#########

# WORKING_DIR = "./contemi_openai"

# if not os.path.exists(WORKING_DIR):
#     os.mkdir(WORKING_DIR)

# rag = LightRAG(
#     working_dir=WORKING_DIR,
#     llm_model_max_async=8,
#     llm_model_func=gpt_4o_mini_complete,  # Use gpt_4o_mini_complete LLM model
#     # llm_model_func=gpt_4o_complete  # Optionally, use a stronger model
# )

WORKING_DIR = "./contemi_opensrc"

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

# Initialize LightRAG with Ollama model
rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_max_async=2,
    llm_model_func=ollama_model_complete,  # Use Ollama model for text generation
    llm_model_name='phi4', # Your model name
    llm_model_kwargs={"options": {"num_ctx": 30720}},
    # Use Ollama embedding function
    embedding_func=EmbeddingFunc(
        embedding_dim=768,
        max_token_size=8192,
        func=lambda texts: ollama_embedding(
            texts,
            embed_model="nomic-embed-text"
        )
    ),
)

# with open('./website_content/index.txt') as f:
#     rag.insert(f.read())
# with open('./website_content/nova-post-trade-team.txt') as f:
#     rag.insert(f.read())

n_chunk = 10
files = glob.glob('./website_content/*.txt')
chunks = [files[i: i+n_chunk] for i in range(0, len(files), n_chunk)]
for idx, files in enumerate(chunks):
    print(f"Chunk Index: {idx}")
    lst_f = []
    for file in files:
        with open(file) as f:
            lst_f.append(f.read())
    rag.insert(lst_f)

# # Perform naive search
# print(rag.query("What are the top themes in this story?", param=QueryParam(mode="naive")))

# # Perform local search
# print(rag.query("What are the top themes in this story?", param=QueryParam(mode="local")))

# # Perform global search
# print(rag.query("What are the top themes in this story?", param=QueryParam(mode="global")))

# # Perform hybrid search
# print(rag.query("What are the top themes in this story?", param=QueryParam(mode="hybrid")))

# Perform mix search (Knowledge Graph + Vector Retrieval)
# Mix mode combines knowledge graph and vector search:
# - Uses both structured (KG) and unstructured (vector) information
# - Provides comprehensive answers by analyzing relationships and context
# - Supports image content through HTML img tags
# - Allows control over retrieval depth via top_k parameter
# print(rag.query("What is this company's line of business?", param=QueryParam(mode="mix")))

print(rag.query("Tell me about this company ?", param=QueryParam(mode="hybrid", top_k = 100, max_token_for_text_unit = 6000, max_token_for_global_context = 6000, max_token_for_local_context = 6000)))