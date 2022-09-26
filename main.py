from flask import Flask
from flask import request
from flask import Response
import requests
import time
import hashlib
from urllib.request import urlopen, Request

TOKEN = "tokenhere"
app = Flask(__name__)

# setting the URL you want to monitor cs210rb
urlMonitor = Request('https://suis.sabanciuniv.edu/prod/bwckschd.p_disp_detail_sched?term_in=202201&crn_in=10087',
                     headers={'User-Agent': 'Mozilla/5.0'})

# to perform a GET request and load the
# content of the website and store it in a var
responseMonitor = urlopen(urlMonitor).read()
# to create the initial hash
currentHash = hashlib.sha224(responseMonitor).hexdigest()
print("running")

def parse_message(message):
    print("message-->", message)
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id, txt


def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot'+TOKEN+'/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }

    r = requests.post(url, json=payload)
    return r


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()

        chat_id, txt = parse_message(msg)
        if txt == "StartProcess":
            tel_send_message(chat_id, "Staring the process")
            time.sleep(3)
            while True:
                time.sleep(3)
                responseMonitor = urlopen(urlMonitor).read()
                currentHash = hashlib.sha224(responseMonitor).hexdigest()
                print("took hash")
                time.sleep(45)
                responseMonitor = urlopen(urlMonitor).read()
                newHash = hashlib.sha224(responseMonitor).hexdigest()
                if newHash == currentHash:
                    print("no change in console")
                    continue
                else:
                    # notify
                    print("something changed in console")
                    tel_send_message(chat_id, "something changed in bot")
                    # again read the website
                    responseMonitor = urlopen(urlMonitor).read()

                    # create a hash
                    currentHash = hashlib.sha224(responseMonitor).hexdigest()
                    # wait for 30 seconds
                    time.sleep(30)
                    continue
        else:
            tel_send_message(chat_id, 'This is the response to any other message sent, send StartProcess')

        return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"


if __name__ == '__main__':
    app.run(debug=True)
