def chunk_pages(pages, chunk_size=1000, overlap=180):
    chunks=[]
    for page_num, text in pages:
        text=' '.join(text.split())
        if not text: continue
        start=0
        while start < len(text):
            end=min(len(text), start+chunk_size)
            piece=text[start:end].strip()
            if piece: chunks.append({'text':piece,'page':page_num})
            if end==len(text): break
            start=max(0,end-overlap)
    return chunks
