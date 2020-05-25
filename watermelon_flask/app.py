from flask import Flask, request, json, jsonify
from gensim.models import Word2Vec
import pandas as pd

app = Flask(__name__)

a = 0

model = Word2Vec.load('/home/ubuntu/watermelon/song2vec/song2vec.model')

songDf = pd.read_json('/home/ubuntu/watermelon/data/song_meta.json')

genreDf = pd.read_json('/home/ubuntu/watermelon/data/genre_gn_all.json')
genreDfIndex = list(genreDf.index)
genreNameList = genreDf['genre'].tolist()

playlistDf = pd.read_json('/home/ubuntu/watermelon/data/train.json')

# tag
tag = []
for i in playlistDf.tags :
    tag += i
    
tagUnique = list(set(tag))

@app.route("/selectMode")
def selectMode() :
    req = request.get_json()
    return_str = req['userRequest']['utterance']
    return_str = str(return_str).strip()

    if return_str == '메뉴':
        res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': '무엇을 하시겠습니까 ?'
                    }
                }],
                'quickReplies': [{
                    'label': '노래추가',
                    'action': 'message',
                    'messageText': '처음으로'
                },
                {
                    'label': '추   천',
                    'action': 'message',
                    'messageText': '처음으로'
                }]
            }
        }

        return jsonify(res)



def getSongId() :
    
    req = request.get_json()
    return_str = req['userRequest']['utterance']
    userSongName = str(return_str).strip()
    userSongName = userSongName.lower()

    try :
        artist, song = userSongName.split('-')
    except ValueError :

        res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': 'Value error !!!  올바른 형식으로 입력하시오'
                    }
                }],
                'quickReplies': [{
                    'label': 'getSongId',
                    'action': 'getSongId',
                    'messageText': '다시 입력하기'
                }]
            }
        }

        return jsonify(res)

    # 입력받은 가수와 제목으로 df 구성
    findArtistDf = songDf[songDf.artist_name_basket.str.contains(artist.strip())].sort_values(by='song_name')
    
    if len(findArtistDf.song_name.str.replace(' ', '').str.contains(song.strip())) > 0 :
        findSongDf = findArtistDf[findArtistDf.song_name.str.replace(' ', '').str.contains(song.strip())]
    else :
        findSongDf = findArtistDf


    
    userSelect = 999999999
    
    # 검색된 노래가 2개 이상일 경우 선택받는다
    if len(findSongDf) > 1 :
        
        # 길이순 재 정렬
        idx = findSongDf['song_name'].str.len().sort_values().index
        findSongDf = findSongDf.reindex(idx)
            
        print('무슨 노래입니까 ?', end='\n\n')

        saaList = []

        for i in range(5) :  # len(findSongDf)

            song = findSongDf.iloc[i].song_name
            artist = findSongDf.iloc[i].artist_name_basket
            album = findSongDf.iloc[i].album_name
            saaList.append([aong, artist, album])
        
        res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'listCard': {
                        'header' : {
                            'title' : '무슨 노래입니까?'
                        },
                        'items' : [
                            {
                            'title' : saaList[0][1]+saaList[0][0]
                            'description' : saaList[0][2]
                            },
                            {
                            'title' : saaList[1][1]+saaList[1][0]
                            'description' : saaList[1][2]
                            },
                            {
                            'title' : saaList[2][1]+saaList[2][0]
                            'description' : saaList[2][2]
                            },3
                            {4
                            'title' : saaList[3][1]+saaList[3][0]
                            'description' : saaList[3][2]
                            },
                            {
                            'title' : saaList[4][1]+saaList[4][0]
                            'description' : saaList[4][2]
                            },
                        ]
    
                    }
                }],
                'quickReplies': [{
                    'label': 'getSongId',
                    'action': 'getSongId',
                    'messageText': '다시 입력하기'
                }]
            }
        }

        while userSelect >= len(findSongDf) :
            userSelect = int(input('번호를 입력하시오.')) - 1
        
        
        print("\n%s 의 ['%s'] 곡이 추가되었습니다." %(findSongDf.iloc[userSelect].artist_name_basket,
                                          findSongDf.iloc[userSelect].song_name))
        
        return findSongDf.iloc[userSelect].id
   # 검색된 노래가 하나일 경우 
    else :
        print("\n%s 의 ['%s'] 곡이 추가되었습니다." %(findSongDf.artist_name_basket.tolist()[0], findSongDf.song_name.tolist()[0]))
        
        return findSongDf.id.tolist()[0]


@app.route("/")
def hello():
    
    global a
    global songDf

    a += 1


    return str(a) + songDf['song_name'][a]

@app.route("/message", methods=['POST'])
def message():
    req = request.get_json()
    return_str = req['userRequest']['utterance']
    return_str = str(return_str).strip()

    if return_str == 'test':
        res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': 'test 성공입니다.'
                    }
                }],
                'quickReplies': [{
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                }]
            }
        }

        return jsonify(res)


# 메인 함수
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
