import asyncio
import math
import json
import random
import base64
import os

import aiohttp_cors
import aiohttp
from aiohttp import web
import websockets


HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8081))

TICK_RATE = 1/30

MELEE_ROLE = 0
RANGE_ROLE = 1


class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.hitbox_width = 5
        self.hitbox_height = 5
        self.move_speed = 5
        self.shoot_speed = 10
        if role == MELEE_ROLE:
            self.shoot_range = 10
            self.shoot_radius = 2
        else:
            self.shoot_range = 80
            self.shoot_radius = 0.4
    
    def can_shoot(self):
        pass

class RegService:
    def __init__(self):
        self.max_id = 0
        self.db = {}

    def _get_next_id(self):
        self.max_id += 1
        return self.max_id

    def regPlayer(self, player):
        new_id = str(self._get_next_id())
        new_token = base64.b64encode(random.randbytes(20)).decode()
        self.db[(new_id, new_token)] = player
        print(self.db)
        return dict(id=new_id, token=new_token)
    
    def loginPlayer(self, id: int, token: str) -> Player:
        return self.db[(id, token)]

def norm(l, vecX, vecY):
    lo = math.sqrt(vecX * vecX + vecY * vecY)
    c = l / lo
    return c * vecX, c * vecY


class Map:
    def __init__(self, filename):
        self.visible_width = 1001
        self.visible_height = 1001
        self.speed = 5  # cell per second
        self.shoot_speed = 10

        with open(filename) as f:
            self._map = f.readlines()
            self.width = len(self._map[0])
            self.height = len(self._map)
    
    def spawnPlayer(self, player: Player):
        pass

    def move(self, player: Player, vecX: int, vecY: int):
        vecX, vecY = norm(self.speed, vecX, vecY)
        pass

    def shoot(self, player: Player, vecX: int, vecY: int):
        vecX, vecY = norm(self.shoot_speed, vecX, vecY)
        pass
    
    def __str__(self):
        return "\n".join(self._map)


class Game:
    def __init__(self):
        self.playersQueues = {}
        self.map = Map("free100x30.txt")
    
    def joinPlayer(self, player) -> dict:
        self.playersQueues[player] = {
            "move": [],
            "shoot": []
        }
        self.map.spawnPlayer(player)
        data = {}
        data["mapWidth"] = self.map.width
        data["mapHeight"] = self.map.height
        data["visibleMapWidth"] = self.map.visible_width
        data["visibleMapHeight"] = self.map.visible_height
        data["shootRange"] = player.shoot_range
        data["shootRadius"] = player.shoot_radius
        data["moveSpeed"] = player.move_speed
        data["shootSpeed"] = player.shoot_speed
        data["hitboxWidth"] = player.hitbox_width
        data["hitboxHeight"] = player.hitbox_height
        data["map"] = str(self.map)
        return data
        
    
    def registerMove(self, player: Player, data: dict):
        self.playersQueues[player]["move"].append(data)

    def registerShoot(self, player: Player, data: dict):
        self.playersQueues[player]["shoot"].append(data)

    def getUpdateForPlayer(self, player: Player) -> dict:
        pass
    
    def updateGame(self):
        for player, queues in self.playersQueues:
            move_q = queues['move']
            shoot_q = queues['move']
            if move_q:
                self.map.move(player, **move_q[0])
            if shoot_q and player.can_shoot():
                self.map.shoot(player, **shoot_q[0])
            move_q.clear()
            shoot_q.clear()

WS2PLAYER = dict()
GAME = Game()
REG_SERVICE = RegService()

async def tick():
    while True:
        GAME.updateGame()
        for ws, player in WS2PLAYER:
            data = GAME.getUpdateForPlayer(player)           
            msg = {
                "status": "ok",
                "data": data
            }
            await ws.send(json.loads(data))
        await asyncio.sleep(TICK_RATE)

loop = asyncio.get_event_loop()

loop.create_task(tick())


async def handler(websocket, path):
    try:
        async for msg in websocket:
            await handle_message(msg, websocket)
    except websockets.ConnectionClosedError:
        pass
    finally:
        WS2PLAYER.pop(websocket, None)

async def handle_message(msg, websocket):
    data = json.loads(msg)
    print(data)
    command = data.get("command")
    if command == "join":
        player = REG_SERVICE.loginPlayer(**data["data"])
        if not player:
            await websocket.send_str(json.dumps({
                "command": "join",
                "status": "fail",
                "data": {"detail": "wrong id/token pair"}
            }))
            return
        WS2PLAYER[websocket] = player
        data = GAME.joinPlayer(player)
        await websocket.send_str(json.dumps({
            "command": "join",
            "status": "ok",
            "data": data
        }))
    elif command == "move":
        player = WS2PLAYER.get(websocket)
        if not player:
            await websocket.send_str(json.dumps({
                "command": "move",
                "status": "fail",
                "data": {
                    "detail": "unauthorized."
                }
            }))
        GAME.registerMove(player, **data["data"])
    elif command == "shoot":
        player = WS2PLAYER.get(websocket)
        if not player:
            await websocket.send_str(json.dumps({
                "command": "shoot",
                "status": "fail",
                "data": {
                    "detail": "unauthorized."
                }
            }))
        GAME.register(player, **data["data"])


async def testhandle(request):
    data = await request.json()
    ret = REG_SERVICE.regPlayer(Player(data["name"], RANGE_ROLE if data["role"] == "range" else MELEE_ROLE))
    return web.json_response(ret)


async def websocket_handler(request):
    print('Websocket connection starting')
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    print('Websocket connection ready')

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            await handle_message(msg.data, ws)

    print('Websocket connection closed')
    return ws


def main():
    app = aiohttp.web.Application()
    app.router.add_route('POST', '/api/register', testhandle)
    app.router.add_route('GET', '/api/game', websocket_handler)
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*"
            )
    })
    for route in list(app.router.routes()):
        cors.add(route)
    aiohttp.web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    main()
