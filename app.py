import os
from sanic import Sanic
from sanic.response import json
from sanic.request import Request
from sanic_cors import CORS
from mcts import *

# to enable debug, run app with `DEBUG=1 python app.py`
DEBUG = int(os.getenv("DEBUG")) or False

app = Sanic(__name__)
CORS(app)


@app.route("/play", methods=["POST"])
def play(request: Request):
    '''
    payload:
    {
        "turn": 3,
        "state": [
        [ "x", "o", ""],
        [ "" , "x", ""],
        [ "" , "" , ""]
        ]
    }
    '''

    body = request.json

    # #TODO:bit representation for state, input shaping
    # player1_state = ""
    # player2_state = ""
    # for row in range(3):
    #     for col in range(3):
    #         if body["state"][row][col] == 'x':
    #             player1_state+="1"
    #             player2_state+="0"
    #         elif body["state"][row][col] == 'o':
    #             player2_state+="1"
    #             player1_state+="0"
    #         else:
    #             player1_state += "0"
    #             player2_state += "0"
    # states = [int(player1_state, 2), int(player2_state, 2)]


    state = [[0, 0, 0],
             [0, 0, 0],
             [0, 0, 0]]
    for row in range(3):
        for column in range(3):
            element = body["state"][row][column]
            if element != "":
                if element == 'x':
                    state[row][column] = 1 #1 for cross
                else:
                    state[row][column] = 2 #2 for circle


    num_simulations = 2000
    mcts = MCTS(State(state, whose_turn=int(body["turn"])%2+1))
    for i in range(num_simulations):
        mcts.treepolicy() #select and expand
        result = mcts.rollout()
        mcts.backpropagate(result)
    
    r, c = mcts.return_action()
        
    return json({"row": str(r), "col": str(c)})

if __name__ == "__main__":
    # Docker image should always listen in port 7000
    app.run(host="0.0.0.0", port=7777, debug=DEBUG, access_log=DEBUG)

