import json
from collections import defaultdict
import os

import mitmproxy.http
from mitmproxy import tcp
from pathlib import Path

from parser import Parser

received = {}
sent = {}
conversation_parsed = defaultdict(lambda: [])


def save_to_file(filepath, write_mode, data):
    Path(os.path.split(filepath)[0]).mkdir(parents=True, exist_ok=True)
    with open(filepath, write_mode) as f:
        f.write(data)

# Start of TCP intercept
def tcp_start(flow: mitmproxy.tcp.TCPFlow):
    """
        A TCP connection has started.
    """

def tcp_message(flow: mitmproxy.tcp.TCPFlow):
    """
        A TCP connection has received a message. The most recent message
        will be flow.messages[-1]. The message is user-modifiable.
    """
    con_id = flow.id
    message = flow.messages[-1]
    # Select the correct Parser (each connection has its own):
    if message.from_client:
        if not con_id in sent:
            sent[con_id] = Parser()
        current = sent[con_id]
    else:
        if not con_id in received:
            received[con_id] = Parser()
        current = received[con_id]

    ret = current.decode(message.content) # Decode message with correct parser

    if ret == [] and current.state == current.states[1]: # message not ready yet
        pass

    else: # Message is complete
        vals, byte_types, byte_values = zip(*ret)
        for i, v in enumerate(vals):
            save_to_file(f'out/conversation{con_id}.txt', 'a+', '\t'.join(
                ['sent ->' if message.from_client else 'received <-', json.dumps(vals)]) + '\n') # Save messages to file


def tcp_error(flow: mitmproxy.tcp.TCPFlow):
    """
        A TCP error has occurred.
    """


def tcp_end(flow: mitmproxy.tcp.TCPFlow):
    """
        A TCP connection has ended.
    """
    con_id = flow.id
    if con_id in received:
        del received[con_id]
    if con_id in sent:
        del sent[con_id]


# Start of HTTP intercept
def response(flow: mitmproxy.http.HTTPFlow):

    if "outsideservices/command/topAccountsLeaderboard" in flow.request.pretty_url: #Save leaderboards
        if flow.response.status_code == 200:
            boardId = flow.request.query["leaderboardId"]
            data = json.loads(flow.response.text)
            with open(f'out/leaderboard{boardId}.json', 'w') as f:
                json.dump(data, f)



def request(flow: mitmproxy.http.HTTPFlow):
    if flow.request.method == "GET":
        pass

    if flow.request.method == "POST":
        pass
