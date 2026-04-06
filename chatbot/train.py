import os
import sys

# Append current directory to catch subpackages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from embeddings.word2vec import train_or_load_w2v
from intent.ngrams import train_ngram
from response.generator import generator

DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset", "chatbot_conversations.csv")

def main():
    print("Starting pre-training logic...")
    if not os.path.exists(DATASET_PATH):
        print(f"Error: No dataset found at {DATASET_PATH}. Please provide the CSV file.")
        return
        
    print("1. Training Word2Vec model...")
    train_or_load_w2v(DATASET_PATH)
    
    print("2. Training N-Gram Model...")
    train_ngram(DATASET_PATH)
    
    print("3. Training TF-IDF vectorizer...")
    generator.load_and_train(DATASET_PATH)
    
    print("Pre-training complete. You can now start the server with `python app.py`!")

if __name__ == '__main__':
    main()
