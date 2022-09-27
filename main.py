
# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import math
import logging
import random
from flask import Flask, request

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__)
moves = ['F', 'T', 'L', 'R']

zombie_list = dict()
elapsed_time = 0
target_user = None

direction = {
    "E": (1, 0),
    "W": (-1, 0),
    "S": (1, 0),
    "N": (-1, 0)
}

@app.route("/", methods=['GET'])
def index():
    dims = input_json["arena"]["dims"]
    return "Let the battle begin!"

@app.route("/", methods=['POST'])
def move():
    global zombie_list
    global elapsed_time
    global target_user

    elapsed_time += 1
    
    request.get_data()
    logger.info(request.json)
    
    # TODO add your implementation here to replace the random response
    input_json = request.json


    # m*n 배열은 최소 (m-1) + (n-1)번만 움직이면 어디로나 갈 수 있음.
    if elapsed_time < dims[0] + dims[1] - 2:
        # 가만히 있는 좀비를 찾을것임.
        for user, user_value in input_json["arena"]["state"].items():
            # 위치 정보 초기화
            if user not in zombie_list:
                zombie_list[user] = {
                    "pos_x": user_value["x"],
                    "pos_y": user_value["x"],
                    "pos_direction": user_value["direction"],
                    "stop_elapsed_time": 0
                }
            
            else:
                zombie_list[user].update({
                    "cur_x": user_value["x"],
                    "cur_y": user["y"],
                    "cur_direction": user_value["direction"]
                })

                if zombie_list[user]["pos_x"] == zombie_list["cur_x"] \
                    and zombie_list[user]["pos_y"] == zombie_list["cur_y"] \
                    and zombie_list[user]["pos_direction"] == zombie_list["cur_direction"]:
                    zombie_list[user]["stop_elapsed_time"] += 1

        return moves[random.randrange(len(moves))]
    # 19초 동안은 타겟을 정하기 위한 것
    else:
        # 19초가 지나 타겟이 정해졌으면 해당 타겟으로 이동 (단, 해당 타겟의 표적이 안되도록)
        if not target_user:
            target_user = sorted(zombie_list, key=lambda x:zombie_list[x]["stop_elapsed_time"], reverse=True)[0]

            target_x = input_json["arena"]["state"]["x"]
            target_y = input_json["arena"]["state"]["y"]
            target_direction = input_json["arena"]["state"]["direction"]

            target_pos = (target_x - direction[target_direction], target_y - direction[target_direction])
        
            # 벽에 붙어 있는 애들은 제외시키기
            if target_x in [0, dims[0]] or target_y in [0, dims[1]]:
                target_user = None

                return "T"
        
        # 내 위치 정보 가져오기
        href = input_json["_links"]["self"]["href"]
        my = input_json["arena"]["state"][href]

        my_direction = my["direction"]
        my_x = my["x"]
        my_y = my["y"]

        # 1. x 좌표 맞추고 (만약 벽에 붙어있다면 같이 벽에 붙기)
        if target_x - my_x > 0:
            # 오른쪽 이동을 위해 방향을 E로 맞추기
            if my_direction != "E": return "R"
            # 방향 맞췄으면 전진
            else: return "F"
        elif target_x - my_x < 0:
            if my_direction != "W": return "R"
            else: return "F"
        elif target_x == my_x:
            # 2. y 좌표 맞추고 (만약 벽에 붙어있다면 같이 벽에 붙기)
            if target_y - my_y > 0:
                # 오른쪽 이동을 위해 방향을 E로 맞추기
                if my_direction != "N": return "R"
                # 방향 맞췄으면 전진
                else: return "F"
            elif target_y - my_y < 0:
                if my_direction != "S": return "R"
                else: return "F"

            elif target_y == my_y:
                # 3. 방향 맞추고
                if target_direction != my_direction: return "R"
                # 4. 쏘세요~
                else: "T"
                

if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
