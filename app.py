from flask import Flask, request,jsonify,Response
import requests
import json
import logging
from logging import config
import sys

app = Flask(__name__)
conf_path = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
with open(conf_path, 'r') as f:
    cfg = json.load(f)

config.dictConfig(cfg['LOGGER'])
app_logger = logging.getLogger('default')

URL = 'https://api.telegram.org/bot{}/'.format(cfg['TELEGRAM']['token'])
SECRET_KEY = cfg['TELEGRAM']['secret_key']
PORT = cfg['TELEGRAM']['port']
IP = cfg['TELEGRAM']['ip']


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

        
def err_formater(errors:list):
    res = ''
    for item in errors:
        res += f"ID: {item['id']} : {item['error']}\n"
    return res


def send_message(chat_id, text='', attachemnts=None):
    pass


@app.route('/', methods=['POST', 'GET'])
def index():
    r = request.get_json()
    print(r)
    if 'message' in r.keys():
        if 'text' in r.get('message').keys():
            if '/get_id' in r['message']['text']:
                r = requests.post(URL + 'sendMessage', json={"chat_id":r['message']['chat']['id'], "text": r['message']['chat']['id']})#, proxies=proxy)
    return 'ok', 200


@app.route('/api/1.0/web/news/', methods=['POST','GET'])
def web():
    try:
        app_logger.info('\n'+str(request.headers))
        res = dict(request.form)
        app_logger.info(res)

        if 'key' not in res.keys() or 'text' not in res.keys() or 'id' not in res.keys():
            app_logger.error('\nkey in args: {}\ntext in args: {}'.format('key' in res.keys(),'text' in res.keys()))
            return Response('Needed arguments not found', 403)

        key = res.get('key') if isinstance(res.get('key'), str) else res.get('key')[0]
        text = res.get('text') if isinstance(res.get('text'), str) else res.get('text')[0]
        chanel_ids = res.get('id').split(',') if isinstance(res.get('id'),str) else res.get('id')


        if text is None:
            app_logger.warning('Body is empty')
            return Response('Body is empty', 403)

        app_logger.info(' - '.join([str(res.get('key') == SECRET_KEY), SECRET_KEY, key]))
        if key is None or key != SECRET_KEY:
            app_logger.info('Key is not valid')
            return Response('Key is not valid', 403)
        else:
            wrong_isd = []
            for id in chanel_ids:
                r = requests.post(URL + 'sendMessage', json={"chat_id": id, "text": text})#, proxies=proxy)
                app_logger.info('Telergam post request:{} : {}'.format(id, r.status_code))
                if r.status_code != 200:
                    app_logger.error('Telegram request error: {}, {}'.format(r.status_code, f'ID: {id} : {r.text}'))
                    wrong_isd.append({'id': id, 'error': r.text})
            if len(wrong_isd):
                return Response('Telegram request error:{}'.format(err_formater(wrong_isd)), 500)
            else:
                return Response('OK', 200)
    except Exception as e:
        app_logger.error(e)
        return Response(str(e), 500),

if __name__ == '__main__':
    app.run(host=IP, port=PORT)
