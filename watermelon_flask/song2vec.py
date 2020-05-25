from gensim.models import KeyedVectors
import pickle
import numpy as np



class Song2Vec():
    def __init__(self, path):
        self.model = None
        self.tagSets = {}
        self.tagIdx = {}
        self.genreSets = {}
        self.genreIdx = {}

        if path:
            self.model = KeyedVectors.load(path)
            self.tagSets = self.loadData(path + 'tagSets.bin')
            self.tagIdx  = self.loadData(path + 'tagIdx.bin')
            self.genreSets  = self.loadData(path + 'genreSets.bin')
            self.genreIdx   = self.loadData(path + 'genreIdx.bin')
    
    def loadData(self, path):
        with open(path, 'rb') as f:
            data = pickle.load(f) # 단 한줄씩 읽어옴
            return data

    def itemToIdx(self, items, typIdx):
        return set([typIdx[item] for item in items])

    def getCosSimilar(self, items, typIdx, typSets):
        res = []
        iset = itemToIdx(items, typIdx)
        for s in typSets:
            if len(s):
                res.append(len(iset & s)/(np.sqrt(len(s))*np.sqrt(len(iset))))
            else:
                res.append(0)
        return np.array(res)

    def getRecommendation(self, songs=[], tags=[], genres=[], nTags=3, nGenres=3):
        songVec = np.zeros(shape=(100,))
        tagVec = np.zeros(shape=(100,))
        genreVec = np.zeros(shape=(100,))

        if songs:
            songVec += song2vec.wv[[str(song) for song in songs]].mean(axis=0)
        if tags:
            cos = getCosSimilar(tags, tagIdx, tagSets)
            totalsim = 0
            for i in cos.argsort()[-nTags:]:    
                vec = song2vec.wv[[str(song) for song in train.loc[i, 'songs']]].mean(axis=0)
                tagVec += cos[i]*vec
                totalsim += cos[i]
            tagVec /= totalsim

        if genres:
            cos = getCosSimilar(genres, genreIdx, genreSets)
            totalsim = 0
            for i in cos.argsort()[-nGenres:]:    
                vec = song2vec.wv[[str(song) for song in train.loc[i, 'songs']]].mean(axis=0)
                genreVec += cos[i]*vec
                totalsim += cos[i]
            genreVec /= totalsim
        topN = song2vec.similar_by_vector(songVec+tagVec+genreVec)

        return topN   