from flask import Flask, request, json, jsonify
from gensim.models import Word2Vec
import pandas as pd
from song2vec import Song2Vec
import sys
import pickle

app = Flask(__name__)

modelPath = '/home/ubuntu/watermelon/song2vec/'
dataPath = '/home/ubuntu/watermelon/data/'

if len(sys.argv) > 1 and sys.argv[1] == 'dev':
    modelPath = 'C:/melon/'
    dataPath = 'C:/melon/'

model = Song2Vec(path=modelPath)

songDf = pd.read_json(dataPath + 'song_meta.json')


def loadUser(userId):
    try:
        with open(f'users/{userId}.bin', 'rb') as f:
            user = pickle.load(f)  #
            return user
    except FileNotFoundError:
        user = {'userId': userId, 'myPlaylist': []}
        return user
    except:
        return False


def saveUser(userId, user):
    try:
        with open(f'users/{userId}.bin', 'wb') as f:
            pickle.dump(user, f)
        return True
    except:
        return False


def makeQuickReply(outputText, labels, action, messages=None, blockId=None, extra=None):
    res = {
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': f'{outputText}'
                }
            }],
            'quickReplies': []
        }
    }

    for i in range(len(labels)):
        actionType = action[i] if type(action) is list else action
        item = {
            'label': labels[i],
            'action': actionType,
            'messageText': messages[i] if messages else labels[i]
        }
        if actionType == 'block':
            item['blockId'] = blockId
        if extra:
            item['extra'] = extra[i]
        res['template']['quickReplies'].append(item)

    return res


def findSongById(sid, df=songDf):
    song = df.iloc[sid].song_name
    artist = df.iloc[sid].artist_name_basket
    return f'{song}-{artist}'


# genreDf = pd.DataFrame(pd.read_json(dataPath + 'genre_gn_all.json', encoding='utf-8', typ='series'), columns=['genre'])
# genreDfIndex = list(genreDf.index)
# genreNameList = genreDf['genre'].tolist()
# playlistDf = pd.read_json(dataPath +'train.json')

# # tag
# tag = []
# for i in playlistDf.tags :
#     tag += i

# tagUnique = list(set(tag))


@app.route("/")
def hello():
    print('print')

    return 'hello'


# 블록 id 확인
@app.route("/block", methods=['POST'])
def block():
    req = request.get_json()
    return_str = req['userRequest']
    return_str = str(return_str)

    res = {
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': return_str
                }
            }]
        }
    }

    return jsonify(res)


@app.route("/message", methods=['POST'])
def message():
    req = request.get_json()
    return_str = req['userRequest']['utterance']
    return_str = str(return_str).strip()

    # 필요한 변수들 
    global songDf

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
                        'text': '추가하실 노래를 \n가수 - 제목\n형식으로 입력해주세요'
                    }
                }]
            }
        }

        return jsonify(res)

    elif return_str.find('-') != -1:

        artist, song = return_str.split('-')

        # 입력받은 가수와 제목으로 df 구성

        findArtistDf = songDf[songDf.artist_name_basket.str.replace(' ', '').str.contains(artist.replace(' ', '').lower())].sort_values(by='song_name')
        
        if len(findArtistDf.song_name.str.replace(' ', '').str.contains(song.replace(' ', '').lower())) > 0 :
            findSongDf = findArtistDf[findArtistDf.song_name.str.replace(' ', '').str.contains(song.replace(' ', '').lower())]
        else :
            findSongDf = findArtistDf

        # 길이순 재 정렬
        idx = findSongDf['song_name'].str.len().sort_values().index
        findSongDf = findSongDf.reindex(idx)

        txt = '몇번째 음악을 추가하시겠습니까?\n\n'
        quickReplies = []
        if len(findSongDf) > 1 :
            for i in range(len(findSongDf)):

                song = findSongDf.iloc[i].song_name
                artist = findSongDf.iloc[i].artist_name_basket
                album = findSongDf.iloc[i].album_name
                songId = findSongDf.iloc[i].name

                txt += '{}번 {} - {} / {}\n\n'.format((i + 1), artist, song, album)  # song_name 출력

                quickReplies.append({
                    'label': str(i + 1),
                    'action': 'block',
                    'messageText': f'{i + 1}번 노래가 추가되었습니다.',
                    'blockId': '5ecb168c031ba400011698b3',
                    'extra': {'songId': str(songId)},
                })

                if i == 9:
                    break

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

        else : 
            res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': '원하시는 음악을 찾을 수 없습니다.'
                    }
                }],
                'quickReplies': [{
                    'label': '음악추가',
                    'action': 'message',
                    'messageText': '음악추가',
                },
                {
                    'label': '돌아가기',
                    'action': 'message',
                    'messageText': '시작',

                }]
            }
        }

        return jsonify(res)


    elif return_str == '음악추천':
        req = request.get_json()
        userId = req['userRequest']['user']['id']
        userId = str(userId).strip()
        user = loadUser(userId)

        pred = model.getRecommendation(songs=user['myPlaylist'])

        txt = ''

        for songId, prop in  pred :
    
            song = songDf.iloc[int(songId)]['song_name']
            artist = songDf.iloc[int(songId)]['artist_name_basket']
            
            txt += f'{song} - {artist} / {round(prop*100, 1)}%\n\n'

        res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': txt
                    }
                }],
                'quickReplies': [{
                    'label': '음악추가',
                    'action': 'message',
                    'messageText': '음악추가',
                },
                {
                    'label': '돌아가기',
                    'action': 'message',
                    'messageText': '시작',

                }]
            }
        }

        return jsonify(res)

    elif return_str == '플레이리스트삭제' :
        req = request.get_json()
        makeQuickReply(
            "어떻게 할까요?",
            ["선택삭제", "모두삭제", "돌아가기"],
            ["block", 'message', 'message'],
            blockId = None,   # blockID 추가 필요            
        )
        
        # req = request.get_json()
        # userId = req['userRequest']['user']['id']
        # userId = str(userId).strip()
        # user = loadUser(userId)
        
        # myPlaylist = []

        # user['myPlaylist'] = myPlaylist 

        # saveUser(userId, user)

        # res = {
        #     'version': "2.0",
        #     'template': {
        #         'outputs': [{
        #             'simpleText': {
        #                 'text': f'플레이리스트가 삭제되었습니다.\n\nMy playlist : {myPlaylist}'
        #             }
        #         }],
        #         'quickReplies': [{
        #             'label': '음악추가',
        #             'action': 'message',
        #             'messageText': '음악추가',

        #         },
        #         {
        #             'label': '음악추천',
        #             'action': 'message',
        #             'messageText': '음악추천',

        #         }]
        #     }
        # }

        # return jsonify(res)

    else:
        res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': '올바른 형식으로 다시 입력해주세요.'
                    }
                }]
            }
        }

        return jsonify(res)


@app.route("/addMusic", methods=['POST'])
def addMusic():
    req = request.get_json()
    songId = req['action']['clientExtra']['songId']
    songId = str(songId).strip()

    userId = req['userRequest']['user']['id']
    userId = str(userId).strip()

    user = loadUser(userId)
    user['myPlaylist'].append(songId)

    myPlaylist = user['myPlaylist']

    saveUser(userId, user)
    
    res = {
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': f'노래가 추가되었습니다.\n\nMy playlist : {myPlaylist}'# '무엇을 하시겠습니까 ?'
                }
            }],
                'quickReplies': [{
                    'label': '음악추가',
                    'action': 'message',
                    'messageText': '음악추가',
                },{
                    'label': '음악추천',
                    'action': 'message',
                    'messageText': '음악추천',
                },{
                    'label': '플레이리스트삭제',
                    'action': 'message',
                    'messageText': '플레이리스트삭제',
                }]
        }
    }

    return jsonify(res)


# 메인 함수
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'dev':
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, threaded=True)
