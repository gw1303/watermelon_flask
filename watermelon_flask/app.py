from flask import Flask, request, json, jsonify
from gensim.models import Word2Vec
import pandas as pd
from song2vec import Song2Vec
from ALS import PreCalculated
import sys, random
import pickle
from konlpy.tag import Okt 
import re
import gc


app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False

s2vPath = '/home/ubuntu/watermelon/song2vec/'
alsPath = '/home/ubuntu/watermelon/als/'
dataPath = '/home/ubuntu/watermelon/data/'

if len(sys.argv) > 1 and sys.argv[1] == 'dev':
    s2vPath = 'C:/melon/'
    dataPath = 'C:/melon/'
    alsPath = 'C:/melon/'

s2v = Song2Vec(path=s2vPath)
als = PreCalculated(path=alsPath)
tw = Okt()
tw.pos('시작합니다')

songDf = pd.read_json(dataPath + 'song_meta.json')
genreDf = pd.DataFrame(pd.read_json(dataPath + 'genre_gn_all.json', encoding='utf-8', typ='series'), columns=['genre'])
with open(f'{dataPath}tagUnique.bin', 'rb') as f:
    tagUnique = pickle.load(f)  #


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
            item['blockId'] = blockId[i]
        if extra:
            if extra[i] : item['extra'] = extra[i]
        res['template']['quickReplies'].append(item)

    return res


def findSongById(sid, df=songDf):
    song = df.iloc[int(sid)].song_name
    artist = df.iloc[int(sid)].artist_name_basket
    return f'{song} - {artist}'


def findGenreTag(message) :

    global tw

    tagSeries = pd.Series(tagUnique)
    message = message.replace(' ', '')


    targetTypes = ['Noun', 'Adjective','Verb']
    target = []

    for text, types in tw.pos(message) :
        if types in targetTypes :
            target.append(text)

    # 불용어 제거
    stopwords = ['음악', '노래', '때', '좋은','추천','기전','들을', '듣고싶어', '할', '해줘', '갈','듣기']
    for stop in stopwords :
        if stop in target :
            target.remove(stop)

    # tag, genre dict
    tagDict = {}
    genreDict = {}
    for i in target :
        if tagSeries[tagSeries.str.contains(i)].tolist() : 
            tagList = tagSeries[tagSeries.str.contains(i)].tolist()
            tagList.sort(key=len)
            tagDict[i] = tagList[:3]
        if genreDf[genreDf.genre.str.contains(i)].index.tolist() :
            genreDict[i] = genreDf[genreDf.genre.str.contains(i)].index.tolist()

    res = {'genre':genreDict, 'tag':tagDict}
    
    if res['genre'] or res['tag'] :
        return res
    else :
        return None


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


# 메인 함수
@app.route("/message", methods=['POST'])
def message():
    req = request.get_json()
    return_str = req['userRequest']['utterance']
    return_str = str(return_str).strip()

    # 필요한 변수들 
    global songDf

    if return_str == '시작':
        req = request.get_json()

        userId = req['userRequest']['user']['id']
        userId = str(userId).strip()
        user = loadUser(userId)
        
        myPlaylist = user['myPlaylist']


        res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': f'무엇을 하시겠습니까 ?\n\nMy playlist : {myPlaylist}'
                    }
                }],
                'quickReplies': [{
                    'label': '음악추가',
                    'action': 'message',
                    'messageText': '음악추가',

                },{
                    'label': '음악추천',
                    'action': 'message',
                    'messageText': '음악제안',

                    },{
                    'label': '플레이리스트삭제',
                    'action': 'message',
                    'messageText': '플레이리스트삭제',
                }]
            }
        }

        return jsonify(res)

    elif return_str == '음악추가':
        res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': '=====================\n\n              가수 - 제목\n\n=====================\n\n        형식으로 입력해주세요\n\n  < 일부만 입력해도 검색 가능 >'
                    }            
                }],
                'quickReplies': [
                {
                    'label': '돌아가기',
                    'action': 'message',
                    'messageText': '시작',
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

        txt = '몇번째 음악을 추가하시겠습니까?'
        quickReplies = []
        if len(findSongDf) >= 1 :
            for i in range(len(findSongDf)):

                song = findSongDf.iloc[i].song_name
                artist = findSongDf.iloc[i].artist_name_basket
                album = findSongDf.iloc[i].album_name
                songId = findSongDf.iloc[i].name

                txt += '\n\n{}번 {} - {} / {}'.format((i + 1), song, artist,  album)  # song_name 출력

                quickReplies.append({
                    'label': str(i + 1),
                    'action': 'block',
                    'messageText': f'{i + 1}번 노래 추가해줘',
                    'blockId': '5ecb168c031ba400011698b3',
                    'extra': {'songId': str(songId)},
                })

                if i == 9:
                    break

            quickReplies.append({
                    'label': '돌아가기',
                    'action': 'message',
                    'messageText': '시작',
                })    

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
                        'text': '원하시는 음악을 찾을 수 없습니다.\n\n다시 입력해주세요.'
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


    elif return_str.find('추천') != -1 :

        req = request.get_json()
        userId = req['userRequest']['user']['id']
        userId = str(userId).strip()
        user = loadUser(userId)
        
        found = findGenreTag(return_str)
        

        genre = []
        tags = []

        if found :
            for i in found['genre'].values() :
                genre += i
            for i in found['tag'].values() :
                tags += i

        if tags or genre :

            pred = s2v.getRecommendation(songs=user['myPlaylist'], tags=tags, genres=genre)
            
            if not user['myPlaylist']:
                pred = sorted(random.sample(pred, 20), key=lambda x:x[1])

            txt = '당신에게 추천드리는 음악입니다.'

            for songId, prop in  pred[:10] :
        
                song = songDf.iloc[int(songId)]['song_name']
                artist = songDf.iloc[int(songId)]['artist_name_basket']
                
                txt += f'\n\n{song} - {artist}'

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

            gc.collect()

            return jsonify(res)

        else : 
            res = {
                'version': "2.0",
                'template': {
                    'outputs': [{
                        'simpleText': {
                            'text': '원하시는 느낌의 음악을 찾을 수 없습니다.'
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

    elif return_str == '음악제안':
        req = request.get_json()
        userId = req['userRequest']['user']['id']
        userId = str(userId).strip()
        user = loadUser(userId)

        if user['myPlaylist'] :

            s2vResult = s2v.getRecommendation(songs=user['myPlaylist'])
            alsResult = als.getRecommendation(songs=user['myPlaylist'])

            s2vResultItem = [str(sid) for sid, score in s2vResult]
            alsResultItem = [str(sid) for sid, score in alsResult]

            s2vResult = list(zip(s2vResultItem, als.rankScore))
            alsResult = list(zip(alsResultItem, als.rankScore))

            totalRank = als.combMNZ([s2vResult, alsResult])
            
            txt = '당신에게 추천드리는 음악입니다.'

            for songId, prop in totalRank[:10] :
        
                song = songDf.iloc[int(songId)]['song_name']
                artist = songDf.iloc[int(songId)]['artist_name_basket']
                
                txt += f'\n\n{song} - {artist}'

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

        else : 
            res = {
                'version': "2.0",
                'template': {
                    'outputs': [{
                        'simpleText': {
                            'text': '플레이리스트에 음악을 추가해주세요.'
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
        res = makeQuickReply(
            "어떻게 할까요?",
            ["선택삭제", "모두삭제", "돌아가기"],
            ["block", 'block', 'message'],
            ["선택삭제", "모두삭제", "시작"],
            blockId = ['5eccf7cfd30dd70001af5fb6', '5eccf7dc6fe05800015edd5e', None],   # blockID 추가 필요            
        )
        
        return jsonify(res)

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
    
    myPlaylist = user['myPlaylist']
    
    if songId in myPlaylist :

        res = {
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': '해당 곡이 이미 존재합니다.'                   }
                }],
                    'quickReplies': [{
                        'label': '음악추가',
                        'action': 'message',
                        'messageText': '음악추가',
                    },{
                        'label': '돌아가기',
                        'action': 'message',
                        'messageText': '시작',
                    }]
            }
        }

        return jsonify(res)

    else : 
        user['myPlaylist'].append(songId)
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
                        'messageText': '음악제안',
                    },{
                        'label': '플레이리스트삭제',
                        'action': 'message',
                        'messageText': '플레이리스트삭제',
                    }]
            }
        }

        return jsonify(res)

@app.route("/deleteAllMusic", methods=['POST'])
def deleteAllMusic():  # 5eccf7dc6fe05800015edd5e
    req = request.get_json()
    utterance = req['userRequest']['utterance']
    utterance = str(utterance).strip()
    userId = req['userRequest']['user']['id']
    userId = str(userId).strip()
    user = loadUser(userId) 

    user['myPlaylist'] = []        
    res = makeQuickReply(
        '삭제되었습니다.',
        ['돌아가기'],
        'message',
        ['시작']
    )
    saveUser(userId, user)
    return jsonify(res)

@app.route("/deleteSelectedMusic", methods=['POST'])
def deleteSelectedMusic():
    thisBlockId = '5eccf7cfd30dd70001af5fb6'
    req = request.get_json()
    userId = req['userRequest']['user']['id']
    userId = str(userId).strip()
    user = loadUser(userId)

    choice = req['action']['clientExtra']

    if choice:
        user['myPlaylist'].remove(choice['songId'])    
        saveUser(userId, user)

    playlist = []
    songids = []

    for i, sid in enumerate(user['myPlaylist']):
        playlist.append(f'{i+1}번 {findSongById(sid)}')
        songids.append({'songId':sid})
    
    if playlist:
        res = makeQuickReply(
            '몇번째 음악을 삭제하시겠습니까?\n\n'+ '\n\n'.join(playlist),
            [str(j+1) for j in range(len(playlist))] + ["돌아가기"],
            action = ['block' for _ in range(len(playlist))] + ["message"],
            messages=[f'{j+1}번' for j in range(len(playlist))] + ["시작"],
            blockId=[thisBlockId for j in range(len(playlist))],
            extra=songids + [None]
        )
        
    else:
        res = makeQuickReply(
        '남은 음악이 없어요.',
        ['돌아가기'],
        'message',
        ['시작']
    )

    return jsonify(res)


# 메인 함수
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'dev':
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, threaded=True)
