from config import EMBED_MODEL
from backend.gemini_client import call_gemini, get_gemini_client

def embed(text, task='RETRIEVAL_QUERY'):
    result=call_gemini(lambda: get_gemini_client().models.embed_content(model=EMBED_MODEL, contents=text, config={'task_type':task}))
    return result.embeddings[0].values

def embed_many(texts):
    # Sequential requests are deliberately simple and predictable for this starter.
    return [embed(t, 'RETRIEVAL_DOCUMENT') for t in texts]
