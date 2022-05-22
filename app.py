from queue import Queue
from threading import Thread
from datetime import timedelta
from flask import Flask, request, render_template, send_from_directory, session
from mcts import MCTS
from breakthrough import BreakThrough, move_string_to_number, move_number_to_string, IllegalMoveError
import time
import json
import uuid
import os


def play_game(queue_in, queue_out):
    tree = MCTS()
    board_numeric = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, -1, -1, -1, -1, -1, -1, -1, -1, 0,
                     0, -1, -1, -1, -1, -1, -1, -1, -1, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
                     0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     ]

    board = BreakThrough(board=board_numeric, turn=1,
                         winner=None, terminal=False)

    isFirst = True
    while True:
        t = 300 if isFirst else 100
        isFirst = False

        for _ in range(t):
            tree.do_rollout(board)

        # Release this process if user haven't move over 30 seconds
        timeout = time.time() + 30
        while(queue_in.empty()):
            if time.time() > timeout:
                json_data = json.dumps({
                    "status": "timeout",
                    "data": ""
                })
                queue_out.put(json_data)
                return
        try:
            move_string = queue_in.get()
            move_number = move_string_to_number(move_string)
            board = board.make_move(move_number)
            if board.terminal:
                break
        except IllegalMoveError:
            json_data = json.dumps({
                "status": "error",
                "data": "illegal move"
            })
            queue_out.put(json_data)
            return

        node = tree.choose(board)
        move_number = node.parent_movement
        board = node
        json_data = json.dumps({
            "status": "move",
            "data": move_number_to_string(move_number)
        })
        queue_out.put(json_data)
        if board.terminal:
            break

    json_data = json.dumps({
        "status": "end",
        "data": board.winner
    })
    queue_out.put(json_data)
    return


app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
processes = {}
boards = {}
queues_in = {}
queues_out = {}


def cleanup(uid):
    if uid not in processes:
        return None

    del queues_in[uid]
    del queues_out[uid]
    del processes[uid]
    return True


@app.route('/', methods=['GET'])
def home():
    # if session.get('uid') is None:
    #     session['uid'] = uuid.uuid4()
    # else:
    #     cleanup(session['uid'])
    session['uid'] = uuid.uuid4()
    return render_template('game.html')


@app.route('/api/play', methods=['POST'])
def play():
    uid = session.get('uid')
    move = request.form['move']

    if not uid:
        json_data = json.dumps({
            "status": "error",
            "data": "No session"
        })
        return json_data

    if uid not in processes.keys():
        # Start the game
        queues_in[uid] = Queue()
        queues_out[uid] = Queue()
        queues_in[uid].put(move)
        processes[uid] = Thread(target=play_game, args=(
            queues_in[uid], queues_out[uid]))
        processes[uid].start()
    else:
        # Keep playing the game
        queues_in[uid].put(move)

    # Wait for the response
    while(queues_out[uid].empty()):
        pass
    json_data = queues_out[uid].get()
    data = json.loads(json_data)

    # status: move, timeout, error, end
    if data['status'] != 'move':
        del queues_in[uid]
        del queues_out[uid]
        processes[uid].join()
        del processes[uid]

    return json_data


# @app.route('/api/board', methods=['GET'])
# def get_board():
#     uid = session.get('uid')
#     if uid not in boards.keys():
#         boards[uid] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                        0, -1, -1, -1, -1, -1, -1, -1, -1, 0,
#                        0, -1, -1, -1, -1, -1, -1, -1, -1, 0,
#                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                        0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
#                        0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
#                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                        ]

#     return json.dumps({
#         "data": boards[uid]
#     }
#     )


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


app.run(host='0.0.0.0', port=5001)
