import pandas as pd
import numpy as np
from gensim.models import Word2Vec
import os
import sys

# Ensure parent directory is in path so we can import preprocessing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from preprocessing.tokenizer import tokenize_text
except ImportError:
    # Fallback tokenizer
    def tokenize_text(x): return x.split(), x.lower().split()

MODEL_PATH = os.path.join(os.path.dirname(__file__), "word2vec.model")
model = None

def train_or_load_w2v(dataset_path: str):
    """Train Word2Vec on the dataset or load existing model."""
    global model
    if os.path.exists(MODEL_PATH):
        model = Word2Vec.load(MODEL_PATH)
        return model
        
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path} for Word2Vec training.")
        return None
        
    df = pd.read_csv(dataset_path, nrows=25000)
    sentences = []
    
    if 'message' in df.columns:
        all_text = df['message'].dropna().astype(str).tolist()
    else:
        all_text = df.iloc[:, -1].dropna().astype(str).tolist()
        
    for text in all_text:
        _, clean_tokens = tokenize_text(text)
        if clean_tokens:
            sentences.append(clean_tokens)
            
    if sentences:
        # Use more robust, higher-dimension embeddings and enough epochs
        model = Word2Vec(
            sentences=sentences,
            vector_size=150,
            window=5,
            min_count=2,
            workers=4,
            epochs=20,
            sg=1,
        )
        model.save(MODEL_PATH)
        print("Word2Vec model trained and saved.")
    return model

def get_sentence_vector(text: str):
    """Convert sentence into average word vector."""
    global model
    if model is None:
        if os.path.exists(MODEL_PATH):
            model = Word2Vec.load(MODEL_PATH)
        else:
            return np.zeros(150)
    
    _, clean_tokens = tokenize_text(text)
    vectors = []
    for token in clean_tokens:
        if token in model.wv.key_to_index:
            vectors.append(model.wv[token])
            
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        return np.zeros(model.vector_size)
