import chromadb
from config import CHROMA_PATH
_client=chromadb.PersistentClient(path=str(CHROMA_PATH))
_collection=_client.get_or_create_collection('chatwithpdf_chunks')

def add_document(doc_id, chunks, vectors):
    ids=[f'{doc_id}_{i}' for i in range(len(chunks))]
    _collection.add(ids=ids, documents=[x['text'] for x in chunks], embeddings=vectors,
                    metadatas=[{'document_id':doc_id,'page':int(x['page']),'chunk_index':i} for i,x in enumerate(chunks)])

def search(vector, document_ids=None, n=5):
    where={'document_id': document_ids[0]} if document_ids and len(document_ids)==1 else ({'document_id': {'$in': document_ids}} if document_ids else None)
    result=_collection.query(query_embeddings=[vector], n_results=n, where=where, include=['documents','metadatas','distances'])
    hits=[]
    for doc,meta,dist in zip(result.get('documents',[[]])[0],result.get('metadatas',[[]])[0],result.get('distances',[[]])[0]):
        hits.append({'text':doc,'page':meta.get('page'),'document_id':meta.get('document_id'),'distance':dist})
    return hits

def delete_document(doc_id):
    _collection.delete(where={'document_id':doc_id})
