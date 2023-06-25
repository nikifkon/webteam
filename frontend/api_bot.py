import requests
import websocket
import json
import time

API_BASE_URL = "http://localhost:8081/api"
WS_BASE_URL = "ws://localhost:8081/api/game"


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


# Пример использования
id, token = register("CHOOSE YOUR NAME", "range")
join_game(id,token)
if id and token:
    game_info, ws = join_game(id, token)
    if game_info:
        map_width = game_info["mapWidth"]
        map_height = game_info["mapHeight"]
        visible_map_width = game_info["visibleMapWidth"]
        visible_map_height = game_info["visibleMapHeight"]
        shoot_range = game_info["shootRange"]
        shoot_radius = game_info["shootRadius"]
        visible_map = game_info.get("visibleMap", "")
        # Выполнение действий в игре
        move(ws, 11, 22)
        shoot(ws, 11, 22)
        while True:
            try:
                response = ws.recv()
                data = json.loads(response)
                process_game_update(data["data"])
            except KeyboardInterrupt:
                ws.close()
                break
    else:
        print("Не удалось присоединиться к игре")
else:
    print("Не удалось зарегистрироваться в игре")
