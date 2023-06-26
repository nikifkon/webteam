import requests
import websocket
import json
import time
from collections import deque
import queue
import math
import os

# API_BASE_URL = "http://localhost:8081/api"
# WS_BASE_URL = "ws://localhost:8081/api/game"
API_BASE_URL = "http://158.160.48.156/api"
WS_BASE_URL = "ws://158.160.48.156/api/game"


# Регистрация
def register(name, role):
    url = f"{API_BASE_URL}/register"
    payload = {
        "name": name,
        "role": role
    }
    response = requests.post(url, json=payload)
    data = response.json()
    if response.status_code == 200:
        return data["id"], data["token"]
    else:
        return None


# Присоединение к игре
def join_game(id, token):
    url = f"{WS_BASE_URL}?id={id}&token={token}"
    ws = websocket.create_connection(url)
    join_command = {
        "command": "join",
        "data": {
            "id": id,
            "token": token
        }
    }
    ws.send(json.dumps(join_command))
    response = ws.recv()
    data = json.loads(response)
    if data["status"] == "ok":
        game_info = data["data"]
        return game_info, ws
    else:
        return None


# Определение типа ячейки на основе символа
def get_cell_type(cell):
    if cell == "F":
        return "free"
    elif cell == "W":
        return "wall"
    elif cell == "U":
        return "you"
    elif cell == "E":
        return "enemy"
    elif cell == "D":
        return "damage"
    else:
        return "unknown"


# Обработка сообщений об изменениях
def process_game_update(data):
    posX = data["posX"]
    posY = data["posY"]
    hp = data["HP"]
    shoot_cd = data["shootCD"]
    # charge_cd = data["chargeCD"]
    visible_enemies = data["visibleEnemeis"]
    visible_damage = data["visibleDamage"]
    visible_map = data.get("visibleMap", "")

    # Дополнительная обработка полученных данных
    # ...

    # Пример вывода информации
    print(f"Position: ({posX}, {posY})")
    print(f"HP: {hp}")
    print(f"Shoot Cooldown: {shoot_cd}")
    # print(f"Charge Cooldown: {charge_cd}")
    print("Visible Enemies:")
    for enemy in visible_enemies:
        enemy_role = enemy["role"]
        enemy_posX = enemy["posX"]
        enemy_posY = enemy["posY"]
        enemy_hp = enemy["HP"]
        print(f"- Role: {enemy_role}, Position: ({enemy_posX}, {enemy_posY}), HP: {enemy_hp}")
    print("Visible Damage:")
    for damage in visible_damage:
        damage_type = damage["type"]
        damage_posX = damage["posX"]
        damage_posY = damage["posY"]
        print(f"- Type: {damage_type}, Position: ({damage_posX}, {damage_posY})")
    print("Visible Map:")
    for row in visible_map:
        cells = [get_cell_type(cell) for cell in row]
        print(" ".join(cells))
    print("--------------------------------------")


# Отправка команды на движение
def move(ws, vecX, vecY, charge=False):
    move_command = {
        "command": "move",
        "data": {
            "vecX": vecX,
            "vecY": vecY,
            "charge": charge
        }
    }
    ws.send(json.dumps(move_command))


def shoot(ws, vecX, vecY):
    shoot_command = {
        "command": "shoot",
        "data": {
            "vecX": vecX,
            "vecY": vecY
        }
    }
    ws.send(json.dumps(shoot_command))

def bfs(start, finish,field):
    fin_row = int(finish[0])
    fin_col = int(finish[1])
    start_row = int(start[0])
    start_col = int(start[1])
    # field = open("../server/idoknow100x100.txt", 'r').readlines()
    n = max(fin_row, start_row) + 1
    m = max(fin_col, start_col) + 1
    visited = [[False] * m for _ in range(n)]
    paths = [[[]] * m for _ in range(n)]
    queue = deque([[start_row, start_col]])
    visited[start_row][start_col] = True
    paths[start_row][start_col] = [[start_row, start_col]]
    while queue:
        row, col = queue.popleft()
        # print(row, col)  # Можно изменить действие на требуемое

        # Проверяем соседние клетки
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row = row + dx
            new_col = col + dy

            # Проверяем, что новые координаты находятся в пределах прямоугольника
            if 0 <= new_row < n and 0 <= new_col < m and not visited[new_row][new_col] and field[new_row][new_col] !="W":
                queue.append((new_row, new_col))
                visited[new_row][new_col] = True
                paths[new_row][new_col] = paths[row][col].copy()
                paths[new_row][new_col].append([new_row, new_col])
    # return paths[new_row-1][new_col-1]      [fin_row - 1][fin_col - 1]
    return paths[fin_row][fin_col]


def start_bot():
    id, token = register("Bot", "range")
    if id and token:
        game_info, ws = join_game(id, token)
        if game_info:
            map_width = game_info["mapWidth"]
            map_height = game_info["mapHeight"]
            visible_map_width = game_info["visibleMapWidth"]
            visible_map_height = game_info["visibleMapHeight"]
            shoot_range = game_info["shootRange"]
            shoot_radius = game_info["shootRadius"]

            # Выполнение действий в игре
            shoot(ws, 11, 22)
            shoot(ws,22,11)
            response = ws.recv()
            data = json.loads(response)["data"]
            prev_posX = data["posX"]
            prev_posY = data["posY"]
            cur_posX = data["posX"]
            cur_posY = data["posY"]
            field = open("server/idoknow100x100.txt", 'r').readlines()
            while True:
                try:
                    response = ws.recv()
                    data = json.loads(response)
                    if data["command"] != "update":
                        continue
                    data = data["data"]
                    enemies = data["visibleEnemeis"]
                    player = enemies[0]
                    if player and player["HP"] > 0:
                        shoot(ws, player["posX"] - cur_posX, player["posY"] - cur_posY)
                    path = bfs([data["posX"], data["posY"]], [player["posX"], player["posY"]], field)
                    i=1
                    prev_posX = cur_posX
                    prev_posY = cur_posY
                    cur_posX = data["posX"]
                    cur_posY = data["posY"]
                    # print(path)
                    # print(data["posX"], data["posY"])
                    # print(prev_posX, prev_posY, cur_posX, cur_posY)
                    # print(abs(prev_posX - cur_posX) < 0.1 and abs(prev_posY - cur_posY) < 0.1)
                    if path and len(path) > 1:
                        first_step = path[0]
                        second_step = path[1]
                        dx = 0
                        dy = 0
                        if first_step[0] != second_step[0]:
                            # if abs(prev_posX - cur_posX) < 0.1 and abs(prev_posY - cur_posY) < 0.1 and path:
                            #     prev_step_posY = second_step[1]
                            #     cur_step_posY = path[2][1]
                            #     i = 3
                            #     while prev_step_posY == cur_step_posY and i < len(path):
                            #         prev_step_posY = cur_step_posY
                            #         cur_step_posY = path[i][1]
                            #         i += 1
                            #     # print(prev_step_posY, cur_step_posY)
                            #     dy = cur_step_posY - prev_step_posY
                            #     move(ws, 0, dy)
                            #     # response = ws.recv()
                            #     # data = json.l oads(response)
                            #     # data = data["data"]
                            #     # if abs(data["posY"] - cur_posY) < 0.1:
                            #     #     dx = second_step[0] - cur_posX
                            #     #     move(ws,-dx,-dy)
                            # else:
                            dx = second_step[0] - cur_posX
                            move(ws, dx, 0)
                        else:
                            # if abs(prev_posX - cur_posX) < 0.1 and abs(prev_posY - cur_posY) < 0.1:
                            #     prev_step_posX = second_step[0]
                            #     cur_step_posX = path[2][0]
                            #     i = 3
                            #     while prev_step_posX == cur_step_posX and i < len(path):
                            #         prev_step_posX = cur_step_posX
                            #         cur_step_posX = path[i][0]
                            #         i += 1
                            #     dx = cur_step_posX - prev_step_posX
                            #     move(ws, dx, 0)
                            # else:
                            dy = second_step[1] - cur_posY
                            move(ws, 0, dy)
                        # print(cur_posX, cur_posY)
                        # print(step)
                        # print(math.ceil(dx), math.ceil(dy))
                        time.sleep(0.01)
                except KeyboardInterrupt:
                    ws.close()
                    break

        else:
            print("Не удалось присоединиться к игре")
    else:
        print("Не удалось зарегистрироваться в игре")
    # field = open("../server/idoknow100x100.txt", 'r').readlines()
    # print(field[52][77])

    # field = ['WWWW',
    #          'WFWW',
    #          'WFFW',
    #          'WWWW']
    # print(bfs([1,1],[2,2],field))