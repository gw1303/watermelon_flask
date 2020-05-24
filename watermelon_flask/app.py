from flask import Flask, request, json, jsonify
from gensim.models import Word2Vec
import pandas as pd

app = Flask(__name__)

a = 0

model = Word2Vec.load('/home/ubuntu/watermelon/song2vec/song2vec.model')

songDf = pd.read_json('/home/ubuntu/watermelon/data/song_meta.json')

@app.route("/")
def hello():
    
    global a
    global songDf

    a += 1


    return str(a) + songDf.iloc['song_name'][a]

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