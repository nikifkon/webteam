## Usage

start local server: `localhost:8081`

```
cd server
pip install -r requirements.txt
python app.py
```


## Api

### `/api/register` (http)

Here you can get pair id/token to join the game

POST Request

```
{
    "name": "CHOOSE YOUR NAME",
    "role": "melee"|"range"
}
```

Response

```
{
    "status": "ok",
    "data": {
        "id": "YOUR ID",
        "token": "YOUR token"
    }
}
```

## `/api/game` (websockets)

This is main api endpoint. Here you can interact with other players and subscribe for updates

### Join the game

Request:

```
{
    "command": "join",
    "data": {
        "id": "ID YOU GOT AFTER REGISTER",
        "token": "TOKEN YOU GOT AFTER REGISTER"
    }
}
```

Response:

if id/token was correct

```
{
    "command": "join",
    "status": "ok",
    "data": {
        "mapWidth": 1337,
        "mapHeight": 1488,
        "visibleMapWidth": 1001,  // always odd
        "visibleMapHeight": 1001,  // always odd

        // depends on choosen role
        "chargeCD": 5,
        "shootCD": 5,
        "shootRange": 5, // how far you damage can go (in cells)
        "shootRadius" 1, // how wide your damage can go (in radian)
        "shootSpeed": 10, // cell per sec
        "moveSpeed": 5, // cell per sec
        "hitboxWidth": 5,  // always odd
        "hittboxHeight: 5,  // always odd
        "HP": 10,
        "shootDamage": 3,
    }
}
```

if not

```
{
    "command": "join",
    "status": "fail",
}
```


### Changes

You will be automaticly subscribed on changes (such as moving and shoting) from another players

Every tick you got messages like this:

```
{
    "posX": 228,
    "posY": 42,
    "HP": 10,
    "shootCD": "HOW MUCH TIME I HAVE TO WAIT BEFORE NEXT SHOOT",
    "chargeCD": "HOW MUCH TIME I HAVE TO WAIT BEFORE NEXT CHARGE",
    "visibleEnemeis": [
        {
            "role": "melee"|"range",
            "posX": 227,
            "posY": 42,
            "HP": 5
        },
        {
            ...
        }
    ],
    "visibleDamage": [
        {
            "type": "melee"|"range",
            "posX": "227",
            "posY": 42,
        }
    ]
}
```

visible map - is part of whole map visible by player. Its matrix of letters centered by player.

each letter means something:

- "F" - free cell
- "W" - wall cell
- "U" - you cell
- "E" - enemy cell
- "D" - damage cell


### Moving

You can send moving command, but during one tick only random one would be registered

Request
```
{
    "command": "move",
    "data": {
        "vecX": 11,
        "vecY": 22,
        "charge": true // if wanna apply charge
    },
}
```

given vector will be automaticly normolized, so you specify only direction

No response


### Shoting

see shooting CD

Request
```
{
    "command": "shoot",
    "data": {
        "vecX": 11,
        "vecY": 22
    }
}
```
