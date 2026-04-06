import collections
from nltk.util import ngrams

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from preprocessing.tokenizer import tokenize_text
except ImportError:
    pass

class NGramModel:
    def __init__(self, n=2):
        self.n = n
        self.ngram_counts = collections.defaultdict(int)
        self.context_counts = collections.defaultdict(int)
        self.vocab = set()
        self.vocab_size = 0

    def train(self, texts):
        """Train N-gram model with Laplace smoothing."""
        for text in texts:
            _, clean_tokens = tokenize_text(text)
            self.vocab.update(clean_tokens)
            
            # Generate ngrams
            generated_ngrams = list(ngrams(clean_tokens, self.n, pad_left=True, pad_right=True, left_pad_symbol='<s>', right_pad_symbol='</s>'))
            for gram in generated_ngrams:
                self.ngram_counts[gram] += 1
                context = gram[:-1]
                self.context_counts[context] += 1
                
        # Vocabulary size plus special tokens
        self.vocab_size = len(self.vocab) + 2 

    def predict_next_word(self, context_words):
        """Predict the next word using Laplace smoothing."""
        if not self.vocab:
            return None
            
        if len(context_words) >= self.n - 1:
            context = tuple(context_words[-(self.n-1):])
        else:
            context = tuple(['<s>'] * (self.n - 1 - len(context_words)) + context_words)

        best_word = None
        best_prob = -1
        
        for word in self.vocab:
            gram = context + (word,)
            count = self.ngram_counts.get(gram, 0)
            context_count = self.context_counts.get(context, 0)
            
            prob = (count + 1) / (context_count + self.vocab_size)
            
            if prob > best_prob:
                best_prob = prob
                best_word = word
                
        return best_word

ngram_model = NGramModel(n=3)

def train_ngram(dataset_path: str):
    import pandas as pd
    if not os.path.exists(dataset_path):
        print("Dataset missing for N-Gram training.")
        return
    df = pd.read_csv(dataset_path, nrows=5000)
    
    if 'role' in df.columns and 'message' in df.columns:
        all_text = df[df['role'] == 'user']['message'].dropna().astype(str).tolist()
    elif 'message' in df.columns:
        all_text = df['message'].dropna().astype(str).tolist()
    else:
        all_text = df.iloc[:, -1].dropna().astype(str).tolist()
        
    ngram_model.train(all_text)
    print("N-gram model logic trained.")
