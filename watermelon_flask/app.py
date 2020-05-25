from flask import Flask, request, json, jsonify
from gensim.models import Word2Vec
import pandas as pd
from song2vec import Song2Vec
import sys

app = Flask(__name__)


modelPath = '/home/ubuntu/watermelon/song2vec/'
dataPath  = '/home/ubuntu/watermelon/data/'


if len(sys.argv)>1 and sys.argv[1] == 'dev':
    modelPath = 'C:/melon/'
    dataPath  = 'C:/melon/'

model = Song2Vec(path=modelPath)


songDf = pd.read_json(dataPath + 'song_meta.json')

myPlaylist = []

# genreDf = pd.DataFrame(pd.read_json(dataPath + 'genre_gn_all.json', encoding='utf-8', typ='series'), columns=['genre'])
# genreDfIndex = list(genreDf.index)
# genreNameList = genreDf['genre'].tolist()
# playlistDf = pd.read_json(dataPath +'train.json')

# # tag
# tag = []
# for i in playlistDf.tags :
#     tag += i
    
# tagUnique = list(set(tag))

# @app.route("/selectMode")
# def selectMode() :
#     req = request.get_json()
#     return_str = req['userRequest']['utterance']
#     return_str = str(return_str).strip()

#     if return_str == '메뉴':
#         res = {
#             'version': "2.0",
#             'template': {
#                 'outputs': [{
#                     'simpleText': {
#                         'text': '무엇을 하시겠습니까 ?'
#                     }
#                 }],
#                 'quickReplies': [{
#                     'label': '노래추가',
#                     'action': 'add_music',
#                     'messageText': '노래 추가'
#                 },
#                 {
#                     'label': '추   천',
#                     'action': 'recommend',
#                     'messageText': '추천'
#                 }]
#             }
#         }

#         return jsonify(res)



# def getSongId() :
    
#     req = request.get_json()
#     return_str = req['userRequest']['utterance']
#     userSongName = str(return_str).strip()
#     userSongName = userSongName.lower()

#     try :
#         artist, song = userSongName.split('-')
#     except ValueError :

#         res = {
#             'version': "2.0",
#             'template': {
#                 'outputs': [{
#                     'simpleText': {
#                         'text': 'Value error !!!  올바른 형식으로 입력하시오'
#                     }
#                 }],
#                 'quickReplies': [{
#                     'label': 'getSongId',
#                     'action': 'getSongId',
#                     'messageText': '다시 입력하기'
#                 }]
#             }
#         }

#         return jsonify(res)

#     # 입력받은 가수와 제목으로 df 구성
#     findArtistDf = songDf[songDf.artist_name_basket.str.contains(artist.strip())].sort_values(by='song_name')
    
#     if len(findArtistDf.song_name.str.replace(' ', '').str.contains(song.strip())) > 0 :
#         findSongDf = findArtistDf[findArtistDf.song_name.str.replace(' ', '').str.contains(song.strip())]
#     else :
#         findSongDf = findArtistDf


    
    # userSelect = 999999999
    
    # # 검색된 노래가 2개 이상일 경우 선택받는다
    # if len(findSongDf) > 1 :
        
    #     # 길이순 재 정렬
    #     idx = findSongDf['song_name'].str.len().sort_values().index
    #     findSongDf = findSongDf.reindex(idx)
            
    #     print('무슨 노래입니까 ?', end='\n\n')

    #     saaList = []

    #     for i in range(5) :  # len(findSongDf)

    #         song = findSongDf.iloc[i].song_name
    #         artist = findSongDf.iloc[i].artist_name_basket
    #         album = findSongDf.iloc[i].album_name
    #         saaList.append([aong, artist, album])
        
#         res = {
#             'version': "2.0",
#             'template': {
#                 'outputs': [{
#                     'listCard': {
#                         'header' : {
#                             'title' : '무슨 노래입니까?'
#                         },
#                         'items' : [
#                             {
#                             'title' : saaList[0][1]+saaList[0][0],
#                             'description' : saaList[0][2]
#                             },
#                             {
#                             'title' : saaList[1][1]+saaList[1][0],
#                             'description' : saaList[1][2]
#                             },
#                             {
#                             'title' : saaList[2][1]+saaList[2][0],
#                             'description' : saaList[2][2]
#                             },
#                             {
#                             'title' : saaList[3][1]+saaList[3][0],
#                             'description' : saaList[3][2]
#                             },
#                             {
#                             'title' : saaList[4][1]+saaList[4][0],
#                             'description' : saaList[4][2]
#                             },
#                         ]
    
#                     }
#                 }],
#                 'quickReplies': [{
#                     'label': 'getSongId',
#                     'action': 'getSongId',
#                     'messageText': '다시 입력하기'
#                 }]
#             }
#         }

#         while userSelect >= len(findSongDf) :
#             userSelect = int(input('번호를 입력하시오.')) - 1
        
        
#         print("\n%s 의 ['%s'] 곡이 추가되었습니다." %(findSongDf.iloc[userSelect].artist_name_basket,
#                                           findSongDf.iloc[userSelect].song_name))
        
#         return findSongDf.iloc[userSelect].id
#    # 검색된 노래가 하나일 경우 
#     else :
#         print("\n%s 의 ['%s'] 곡이 추가되었습니다." %(findSongDf.artist_name_basket.tolist()[0], findSongDf.song_name.tolist()[0]))
        
#         return findSongDf.id.tolist()[0]


@app.route("/")
def hello():
    
    print('print')

    return 'hello'




@app.route("/message", methods=['POST'])
def message():
    req = request.get_json()
    return_str = req['userRequest']['utterance']
    return_str = str(return_str).strip()

    # 필요한 변수들 
    global songDf
    global myPlaylist


    if return_str == '시작':
        res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': '무엇을 하시겠습니까 ?'
                    }
                }],
                'quickReplies': [{
                    'label': '음악추가',
                    'action': 'message',
                    'messageText': '음악추가',

                },
                {
                    'label': '음악추천',
                    'action': 'message',
                    'messageText': '음악추천',

                }]
            }
        }

        return jsonify(res)

    if return_str == '음악추가':
        res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': '추가하실 노래를 가수 - 제목 형식으로 입력하시오'
                    }
                }]
            }
        }

        return jsonify(res)

    elif return_str.find('-') != -1 :

        artist, song = return_str.split('-')

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

        saaList = []
        txt = ''
        quickReplies = []

        for i in range(7) :  # len(findSongDf)

            song = findSongDf.iloc[i].song_name
            artist = findSongDf.iloc[i].artist_name_basket
            album = findSongDf.iloc[i].album_name
            songId = findSongDf.iloc[i].name
            # saaList.append([song, artist, album])

            txt += '{}번 {} - {} / {}\n\n'.format((i+1), artist, song, album)  # song_name 출력 
             
            quickReplies. append({
                    'label': str(i+1),
                    'action': 'message',
                    'messageText': str(i+1),
                    'extra' : str(songId)})

        res = {
                'version': "2.0",
                'template': {
                    'outputs': [{
                        'simpleText': {
                            'text': txt  # song_name 출력 
                        }
                    }],
                    'quickReplies': quickReplies  # 몇번째 노래 ? 
                    }
                }

        return jsonify(res)


    elif return_str == '음악추천':
        res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': '음악추천 페이지'
                    }
                }]
            }
        }

        return jsonify(res)


# 메인 함수
if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1] == 'dev':
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, threaded=True)
