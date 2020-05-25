from gensim.models import KeyedVectors
import pickle
import numpy as np
import pandas as pd 


class Song2Vec():
    def __init__(self, path):
        self.model = None
        self.tagSets = {}
        self.tagIdx = {}
        self.genreSets = {}
        self.genreIdx = {}
        self.playList = None

        if path:
            self.model = KeyedVectors.load(path + 'song2vec-fastload.bin', mmap='r')
            self.tagSets = self.loadData(path + 'tagSets.bin')
            self.tagIdx  = self.loadData(path + 'tagIdx.bin')
            self.genreSets  = self.loadData(path + 'genreSets.bin')
            self.genreIdx   = self.loadData(path + 'genreIdx.bin')
            self.playList = pd.read_pickle(path + 'playList.bin')
    
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
            songVec += self.model.wv[[str(song) for song in songs]].mean(axis=0)
        if tags:
            cos = getCosSimilar(tags, self.tagIdx, self.tagSets)
            totalsim = 0
            for i in cos.argsort()[-nTags:]:    
                vec = self.model.wv[[str(song) for song in playList.loc[i, 'songs']]].mean(axis=0)
                tagVec += cos[i]*vec
                totalsim += cos[i]
            tagVec /= totalsim

        if genres:
            cos = getCosSimilar(genres, self.genreIdx, self.genreSets)
            totalsim = 0
            for i in cos.argsort()[-nGenres:]:    
                vec = self.model.wv[[str(song) for song in playList.loc[i, 'songs']]].mean(axis=0)
                genreVec += cos[i]*vec
                totalsim += cos[i]
            genreVec /= totalsim

        topN = self.model.similar_by_vector(songVec+tagVec+genreVec)

        return topN   