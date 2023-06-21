import asyncio
import math
import json

import websockets


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
        pass

    def regPlayer(self, player):
        pass
    
    def loginPlayer(self, id: int, token: str) -> Player:
        return Player("test", MELEE_ROLE)

def norm(l, vecX, vecY):
    lo = math.sqrt(vecX * vecX + vecY * vecY)
    c = l / lo
    return c * vecX, c * vecY


class Map:
    def __init__(self, filename):
        self.visible_width: 1001
        self.visible_height: 1001
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
        pass


class Game:
    def __init__(self):
        self.playersQueues = {}
        self.map = Map()
    
    def joinPlayer(self, player) -> dict:
        self.playersQueues[player] = {
            "move": [],
            "shoot": []
        }
        self.map.spawnPLayer(player)
        data = {}
        data["mapWidth"] = self.map.width
        data["mapHeight"] = self.map.height
        data["visibleMapWidth"] = self.map.visible_width
        data["visibleMapHeight"] = self.map.visible_height
        data["shootRange"] = self.player.shoot_range
        data["shootRadius"] = self.player.shoot_radius
        data["moveSpeed"] = self.player.move_speed
        data["shootSpeed"] = self.player.shoot_speed
        data["hitboxWidth"] = self.player.hitbox_width
        data["hitboxHeight"] = self.player.hitbox_height
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
            data = json.loads(msg)
            command = data.get("command")
            if command == "join":
                player = REG_SERVICE.loginPlayer(*data["data"])
                if not player:
                    await websocket.send(json.dumps({
                        "command": "join",
                        "status": "fail",
                        "data": {"detail": "wrong id/token pair"}
                    }))
                    return
                WS2PLAYER[websocket] = player
                data = GAME.joinPlayer(player)
                await websocket.send(json.dumps({
                    "command": "join",
                    "status": "ok",
                    "data": data
                }))
            elif command == "move":
                player = WS2PLAYER.get(websocket)
                if not player:
                    await websocket.send(json.dumps({
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
                    await websocket.send(json.dumps({
                        "command": "shoot",
                        "status": "fail",
                        "data": {
                            "detail": "unauthorized."
                        }
                    }))
                GAME.register(player, **data["data"])
    except websockets.ConnectionClosedError:
        pass
    finally:
        WS2PLAYER.pop(websocket, None)
        


if __name__ == "__main__":
    start_server = websockets.serve(handler, "", 8001)
    loop.run_until_complete(start_server)
    loop.run_forever()