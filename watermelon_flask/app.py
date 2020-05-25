from flask import Flask, request, json, jsonify
from gensim.models import Word2Vec
import pandas as pd
from song2vec import Song2Vec
import sys
import pickle

app = Flask(__name__)


modelPath = '/home/ubuntu/watermelon/song2vec/'
dataPath  = '/home/ubuntu/watermelon/data/'


if len(sys.argv)>1 and sys.argv[1] == 'dev':
    modelPath = 'C:/melon/'
    dataPath  = 'C:/melon/'

model = Song2Vec(path=modelPath)


songDf = pd.read_json(dataPath + 'song_meta.json')


def loadUser(self, userId):
    try:
        with open(f'{userId}.bin', 'rb') as f:
            user = pickle.load(f) # 
            return user
    except:
        return False

def saveUser(self, userId, user):
    try:
        with open(f'{userId}.bin', 'wb') as f:
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
        item = {
            'label'  : labels[i],
            'action' : action,
            'messageText' : messages[i] if messages else labels[i]
        }
        if action == 'block':
            item['blockId'] = blockId
        if extra:
            item['extra'] = extra[i]
        res['template']['quickReplies'].append(item)

    return res

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

    elif return_str.find('-') != -1 :

        artist, song = return_str.split('-')

        # 입력받은 가수와 제목으로 df 구성
        findArtistDf = songDf[songDf.artist_name_basket.str.contains(artist.strip())].sort_values(by='song_name')
        
        if len(findArtistDf.song_name.str.replace(' ', '').str.contains(song.strip())) > 0 :
            findSongDf = findArtistDf[findArtistDf.song_name.str.replace(' ', '').str.contains(song.strip())]
        else :
            findSongDf = findArtistDf

            
        # 길이순 재 정렬
        idx = findSongDf['song_name'].str.len().sort_values().index
        findSongDf = findSongDf.reindex(idx)

        txt = '몇번째 음악을 추가하시겠습니까?\n\n'
        quickReplies = []

        for i in range(len(findSongDf)) :  

            song = findSongDf.iloc[i].song_name
            artist = findSongDf.iloc[i].artist_name_basket
            album = findSongDf.iloc[i].album_name
            songId = findSongDf.iloc[i].name

            txt += '{}번 {} - {} / {}\n\n'.format((i+1), artist, song, album)  # song_name 출력 
             
            quickReplies. append({
                    'label': str(i+1),
                    'action': 'block',
                    'messageText': f'{i+1}번 노래가 추가되었습니다.',
                    'blockId' : '5ecb168c031ba400011698b3',
                    'extra' : {'songId':str(songId)},
                    })

            if i == 9 :
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

    else : 
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
def addMusic() :
    req = request.get_json()
    songId = req['action']['clientExtra']['songId']
    songId = str(songId)

    userId = req['userRequest']['user']['id']
    userId = str(userId)

    # user = loadUser()
    # user['myPlaylist'].append(songId)
    # saveUser(userId, user)


    res = {
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': userId
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
