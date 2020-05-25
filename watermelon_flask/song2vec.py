from gensim.models import KeyedVectors
import numpy as np

class Song2Vec():
    def __init__(self, path):  
        self.model = None
        
        if path:
            self.model = KeyedVectors.load(path)
        

    def itemToIdx(self, items, typIdx):    
        return set([typIdx[item] for item in items])

    