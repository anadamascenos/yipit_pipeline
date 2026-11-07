import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def generate_embeddings(df, name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(name)
    texts = (df["title"].fillna("") + " " + df["summary"].fillna("")).tolist()
    return model.encode(texts, show_progress_bar=False)

def compute_top_similar_articles(df, embs, k=3):
    sim = cosine_similarity(embs)
    res = []
    for i in range(len(df)):
        scores = sim[i]
        sorted_idx = np.argsort(scores)[::-1]
        sim_idx = [idx for idx in sorted_idx if idx != i][:k]
        res.append(df.iloc[sim_idx][("article_id" if "article_id" in df.columns else sim_idx)].tolist())
    return res