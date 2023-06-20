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

## `/api/game/<room>` (websockets)

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
        "shootRange": 5, // how far you damage can go
        "shootRadius" 1 // how wide your damage can go (in radian)
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
    "visibleMap": "MAP IN FORMAT DESCRIBED BELLOW",
    "shootCD": "HOW MUCH TIME I HAVE TO WAIT BEFORE NEXT SHOOT"
}
```

visible map - is part of whole map visible by player. Its matrix of letters centered by player.

each letter means something:

"F" - free cell
"U" - you cell
"E" - enemy cell
"D" - demage cell

For example:

if whole map is 7x7

```
FFFFFFF
EFFFFFF
FFFFFFF
FFFFFFF
FFFFUFF
FFFFFFF
FFFFFFF
```

your pos: x=4,y=4

enemy pos: x=0,y=1

and visibility: width=5,height=5

you will get following map

```
FFFFF
FFFFF
FFUFF
FFFFF
FFFFF
```

so you can not see the enemy

### Moving

You can send moving command, but during one tick only random one would be registered

Request
```
{
    "command": "move",
    "data": {
        "vecX": 11,
        "vecY": 22
    }
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

