import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two numeric vectors."""
    if len(vec1.shape) == 1:
        vec1 = vec1.reshape(1, -1)
    if len(vec2.shape) == 1:
        vec2 = vec2.reshape(1, -1)
        
    if not np.any(vec1) or not np.any(vec2):
        return 0.0
        
    return cosine_similarity(vec1, vec2)[0][0]
