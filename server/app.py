import asyncio
import math
import json
import random
import base64
import os

import aiohttp_cors
import aiohttp
from aiohttp import web
import os
from .vector import Vector


FREE = 'F'
YOU = "U"
ENEMY = "E"
DAMAGE = "D"
NONE = 'N'

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8081))

TICK_RATE = 1/30

MELEE_ROLE = 0
RANGE_ROLE = 1


class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.hitbox_width = 20
        self.hitbox_height = 20
        self.move_speed = 100
        self.shoot_speed = 200
        self.hp = 10
        if role == MELEE_ROLE:
            self.charge_cd = 1
            self.charge_mul = 50
            self.shoot_cd = 1.5
            self.shoot_range = 10
            self.shoot_radius = 2
            self.shoot_damage = 4
        else:
            self.charge_cd = 1
            self.charge_mul = 50
            self.shoot_cd = 1
            self.shoot_range = 300
            self.shoot_radius = 0.4
            self.shoot_damage = 3

    def is_col(self, pl_pos: Vector, pos: Vector) -> bool:
        diff = pl_pos - pos
        return all(abs(c) < thr for c, thr in zip(diff.values, [self.hitbox_width, self.hitbox_height]))

class DamageArea:
    def __init__(self, owner: Player, ttl: float, created_at: float):
        self.owner = owner
        self.ttl = ttl
        self.created_at = created_at


class MeleeDamageArea(DamageArea):
    def __init__(self, owner: Player, direction: Vector, created_at: float):
        ttl = owner.shoot_range / owner.shoot_speed
        super().__init__(owner, ttl, created_at)
        self.direction = direction


class RangeDamageArea(DamageArea):
    def __init__(self, owner: Player, direction: Vector, created_at: float):
        ttl = owner.shoot_range / owner.shoot_speed
        super().__init__(owner, ttl, created_at)
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


    def move(self, player: Player, vec: Vector, dt: float, apply_charge: bool):
        vec = dt * player.move_speed * vec.normalize()
        if apply_charge:
            vec *= player.charge_mul
        self.player2pos[player] += vec

    def shoot(self, area: DamageArea):
        self.damageAreas2pos[area] = self.player2pos[area.owner]

    def moveDamageAreas(self, dt: float, time: float):
        for area in list(self.damageAreas2pos.keys()):
            vec = dt * area.owner.shoot_speed * area.direction.normalize()
            self.damageAreas2pos[area] += vec
            if pl := self.find_col_player(area):
                pl.hp = max(0, pl.hp - area.owner.shoot_damage)
                self.damageAreas2pos.pop(area)
            if area.created_at + area.ttl < time:
                self.damageAreas2pos.pop(area)

    def find_col_player(self, area: DamageArea):
        for player, pos in self.player2pos.items():
            if player != area.owner and player.is_col(pos, self.damageAreas2pos[area]):
                return player

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
        self.player2lastshoot: dict[Player, float] = {}
        self.player2lastcharge: dict[Player, float] = {}
        self.map = Map("server/free100x30.txt")
    
    def joinPlayer(self, player: Player) -> dict:
        self.playersQueues[player] = {
            "move": [],
            "shoot": [],
            "charge": []
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

        self.player2lastshoot[player] = -player.shoot_cd
        self.player2lastcharge[player] = -player.charge_cd
        return data
        
    
    def registerMove(self, player: Player, data: dict):
        self.playersQueues[player]["move"].append((Vector(data["vecX"], data["vecY"]), data['charge']))

    def registerShoot(self, player: Player, data: dict):
        self.playersQueues[player]["shoot"].append(Vector(*data.values()))

    def registerCharge(self, player: Player, data: dict):
        self.playersQueues[player]["charge"].append(Vector(*data.values()))

    def getUpdateForPlayer(self, player: Player) -> dict:
        vec = self.map.player2pos[player]
        visiblebEnemies = [{
                "role": "melee" if enemie.role == MELEE_ROLE else "range",
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
            "shootCD": self.player2lastshoot[player],  # TODO
        }
    
    def can_shoot(self, player: Player, time: float):
        return time - self.player2lastshoot[player] > player.shoot_cd
    
    def can_charge(self, player: Player, time: float):
        return time - self.player2lastshoot[player] > player.charge_cd
    
    
    def updateGame(self, dt, time):
        for player, queues in self.playersQueues.items():
            move_q = queues['move']
            shoot_q = queues['shoot']
            charge_q = queues['charge']


            if move_q:
                apply_charge = any(move[1] for move in move_q) and self.can_charge(player, time)
                self.map.move(player, move_q[0][0], dt, apply_charge)
            if shoot_q and self.can_shoot(player, time):
                if player.role == MELEE_ROLE:
                    area = MeleeDamageArea(player, shoot_q[0], time)
                else:
                    area = RangeDamageArea(player, shoot_q[0], time)
                self.map.shoot(area)
                self.player2lastshoot[player] = time
            move_q.clear()
            shoot_q.clear()
            charge_q.clear()
        self.map.moveDamageAreas(dt, time)



async def tick(app):
    overall = 0
    while True:
        app['GAME'].updateGame(TICK_RATE, overall)
        for ws, player in app['WS2PLAYER'].items():
            data = app['GAME'].getUpdateForPlayer(player)           
            msg = {
                "command": "update",
                "status": "ok",
                "data": data
            }
            await ws.send_str(json.dumps(msg))
        await asyncio.sleep(TICK_RATE)
        overall += TICK_RATE


async def handle_message(msg, websocket, app):
    try:
        data = json.loads(msg)
        print(data)
        command = data.get("command")
        if command == "join":
            player = app['REG_SERVICE'].loginPlayer(**data["data"])
            if not player:
                await websocket.send_str(json.dumps({
                    "command": "join",
                    "status": "fail",
                    "data": {"detail": "wrong id/token pair"}
                }))
                return
            app['WS2PLAYER'][websocket] = player
            data = app['GAME'].joinPlayer(player)
            await websocket.send_str(json.dumps({
                "command": "join",
                "status": "ok",
                "data": data
            }))
        elif command == "move":
            player = app['WS2PLAYER'].get(websocket)
            if not player:
                await websocket.send_str(json.dumps({
                    "command": "move",
                    "status": "fail",
                    "data": {
                        "detail": "unauthorized."
                    }
                }))
            app['GAME'].registerMove(player, data["data"])
        elif command == "shoot":
            player = app['WS2PLAYER'].get(websocket)
            if not player:
                await websocket.send_str(json.dumps({
                    "command": "shoot",
                    "status": "fail",
                    "data": {
                        "detail": "unauthorized."
                    }
                }))
            app['GAME'].registerShoot(player, data["data"])
    except Exception as exc:
        print(exc)
    finally:
        pass


async def testhandle(request):
    if request.content_type == 'application/json':
        data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        data = await request.post()
    ret = request.app['REG_SERVICE'].regPlayer(Player(data["name"], RANGE_ROLE if data["role"] == "range" else MELEE_ROLE))
    return web.json_response(ret)


async def websocket_handler(request):
    print('Websocket connection starting')
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    print('Websocket connection ready')

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            await handle_message(msg.data, ws, request.app)
    
    # unsubscribe
    request.app['WS2PLAYER'].pop(ws)
    print('Websocket connection closed')
    return ws


async def background_tasks(app):
    app['WS2PLAYER'] = dict()
    app['GAME'] = Game()
    app['REG_SERVICE'] = RegService()
    app['ws_mail'] = asyncio.create_task(tick(app))
    
def get_app():
    app = aiohttp.web.Application()
    app.router.add_route('POST', '/api/register', testhandle)
    app.router.add_route('GET', '/api/game', websocket_handler)
    app.on_startup.append(background_tasks)

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*"
            )
    })
    for route in list(app.router.routes()):
        cors.add(route)
    return app

async def run(loop):
    app = get_app()

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    while True:
        await asyncio.sleep(5)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
