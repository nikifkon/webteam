import asyncio
import math
import json
import random
import base64
import os

import aiohttp_cors
import aiohttp
from aiohttp import web

from .vector import Vector


FREE = 'F'
YOU = "U"
ENEMY = "E"
DAMAGE = "D"
NONE = 'N'

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8081))

TICK_RATE = 1/30
# TICK_RATE = 1

MELEE_ROLE = 0
RANGE_ROLE = 1


class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.hitbox_width = 5
        self.hitbox_height = 5
        self.move_speed = 100
        self.shoot_speed = 200
        self.hp = 10
        if role == MELEE_ROLE:
            self.shoot_range = 10
            self.shoot_radius = 2
        else:
            self.shoot_range = 80
            self.shoot_radius = 0.4
    
    def can_shoot(self):
        return True

class DamageArea:
    def __init__(self, owner: Player):
        self.owner = owner


class MeleeDamageArea(DamageArea):
    def __init__(self, owner: Player, direction: Vector):
        super().__init__(owner)
        self.direction = direction


class RangeDamageArea(DamageArea):
    def __init__(self, owner: Player, direction: Vector):
        super().__init__(owner)
        self.direction = direction


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


class Map:
    def __init__(self, filename):
        self.visible_width = 1000
        self.visible_height = 1000
        self.player2pos: dict[Player, Vector] = {}  # always discrete
        self.damageAreas2pos: dict[tuple[DamageArea, Vector]] = {}

        with open(filename) as f:
            self._map = list(map(lambda line: list(line.strip()), f.readlines()))
            self.width = len(self._map[0])
            self.height = len(self._map)
    
    def spawnPlayer(self, player: Player):
        x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
        self.player2pos[player] = Vector(x, y)


    def move(self, player: Player, vec: Vector, dt: float):
        vec = dt * player.move_speed * vec.normalize()
        print(vec)
        self.player2pos[player] += vec

    def shoot(self, area: DamageArea):
        self.damageAreas2pos[area] = self.player2pos[area.owner]

    def moveDamageAreas(self, dt: float):
        for area in self.damageAreas2pos:
            vec = dt * area.owner.shoot_speed * area.direction.normalize()
            self.damageAreas2pos[area] += vec

    def _is_visible(self, player, pos):
        player_pos = self.player2pos[player]
        top_left_visible = player_pos - 1/2 * Vector(self.visible_width - 1, self.visible_height - 1)
        botton_right_visible = top_left_visible + Vector(self.visible_width, self.visible_height)
        all_pos = lambda vec: all(c > 0 for c in vec.values)
        return all_pos(pos - top_left_visible) and all_pos(botton_right_visible - pos)

    def get_visible_enemies_for_player(self, player: Player) -> list[tuple[Player, Vector]]:
        return filter(lambda tpl: self._is_visible(*tpl), self.player2pos.items())

    def get_visible_damage_for_player(self, player: Player) -> list[DamageArea]:
        return filter(lambda tpl: self._is_visible(player, tpl[1]), self.damageAreas2pos.items())

    def __str__(self):
        return "\n".join("".join(row) for row in self._map)


class Game:
    def __init__(self):
        self.playersQueues = {}
        self.damageAreaQueue = []
        self.map = Map("server/free100x30.txt")
    
    def joinPlayer(self, player: Player) -> dict:
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
        data["HP"] = player.hp
        return data
        
    
    def registerMove(self, player: Player, data: dict):
        self.playersQueues[player]["move"].append(Vector(*data.values()))

    def registerShoot(self, player: Player, data: dict):
        self.playersQueues[player]["shoot"].append(Vector(*data.values()))

    def getUpdateForPlayer(self, player: Player) -> dict:
        vec = self.map.player2pos[player]
        visiblebEnemies = [{
                "role": enemie.role,
                "posX": pos.values[0],
                "posY": pos.values[1],
                "HP": enemie.hp
            }
            for enemie, pos in self.map.get_visible_enemies_for_player(player)
            if enemie != player
        ]

        visibleDamage = [{
                "type": "melee" if damage.owner.role == MELEE_ROLE else "range",
                "posX": pos.values[0],
                "posY": pos.values[1],
            } for damage, pos in self.map.get_visible_damage_for_player(player)
        ]

        return {
            "posX": vec.values[0],
            "posY": vec.values[1],
            "HP": player.hp,
            "visibleEnemeis": visiblebEnemies,
            "visibleDamage": visibleDamage,
            "shootCD": 0,  # TODO
        }
    
    def updateGame(self, dt):
        for player, queues in self.playersQueues.items():
            move_q = queues['move']
            shoot_q = queues['shoot']
            if move_q:
                self.map.move(player, move_q[0], dt)
            if shoot_q and player.can_shoot():
                if player.role == MELEE_ROLE:
                    area = MeleeDamageArea(player, shoot_q[0])
                else:
                    area = RangeDamageArea(player, shoot_q[0])
                self.map.shoot(area)
            move_q.clear()
            shoot_q.clear()
        self.map.moveDamageAreas(dt)

WS2PLAYER = dict()
GAME = Game()
REG_SERVICE = RegService()

async def tick():
    while True:
        GAME.updateGame(TICK_RATE)
        for ws, player in WS2PLAYER.items():
            data = GAME.getUpdateForPlayer(player)           
            msg = {
                "command": "update",
                "status": "ok",
                "data": data
            }
            await ws.send_str(json.dumps(msg))
        await asyncio.sleep(TICK_RATE)


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
        GAME.registerMove(player, data["data"])
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
        GAME.registerShoot(player, data["data"])


async def testhandle(request):
    if request.content_type == 'application/json':
        data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        data = await request.post()
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
    
    # unsubscribe
    WS2PLAYER.pop(ws)
    print('Websocket connection closed')
    return ws


async def main(loop):
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

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()

    await tick()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
