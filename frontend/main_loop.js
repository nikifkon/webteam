import { Game } from './game.js';
import { Field, Free, Wall, None, Bullet } from './field.js';
import { Player } from './player.js';
import Vector from './vector.js';
import { MoveCommand, ShootCommand } from './commands.js';
import { Notification } from './notification.js'
import { CDTimer } from './cd_timer.js';


const WS_ENDPOINT = 'ws://158.160.48.156/api/game'
// const WS_ENDPOINT = 'ws://localhost:8081/api/game'

const playerCommand = [];
const me = new Player();

let GAME;

let GO_RIGHT = false;
let GO_LEFT = false;
let GO_UP = false;
let GO_DOWN = false;

document.addEventListener("keydown", keyDownHandler, false);
function keyDownHandler(e) {
    if (e.key === "Right" || e.key === "ArrowRight" || e.key.toLowerCase() === "d" || e.key.toLowerCase() === "в") {
        GO_RIGHT = true;
    } else if (e.key === "Left" || e.key === "ArrowLeft" || e.key.toLowerCase() === "a" || e.key.toLowerCase() === "ф") {
        GO_LEFT = true;
    }
    if (e.key === "Up" || e.key === "ArrowUp" || e.key.toLowerCase() === "w" || e.key.toLowerCase() === "ц") {
        GO_UP = true;
    } else if (e.key === "Down" || e.key === "ArrowDown" || e.key.toLowerCase() === "s" || e.key.toLowerCase() === "ы") {
        GO_DOWN = true;
    }
}

document.addEventListener("keyup", keyUpHandler, false);
function keyUpHandler(e) {
    if (e.key === "Right" || e.key === "ArrowRight" || e.key.toLowerCase() === "d" || e.key.toLowerCase() === "в") {
        GO_RIGHT = false;
    } else if (e.key === "Left" || e.key === "ArrowLeft" || e.key.toLowerCase() === "a" || e.key.toLowerCase() === "ф") {
        GO_LEFT = false;
    }
    if (e.key === "Up" || e.key === "ArrowUp" || e.key.toLowerCase() === "w" || e.key.toLowerCase() === "ц") {
        GO_UP = false;
    } else if (e.key === "Down" || e.key === "ArrowDown" || e.key.toLowerCase() === "s" || e.key.toLowerCase() === "ы") {
        GO_DOWN = false;
    }
}

let SHOOT_VEC = null;

document.addEventListener("click", leftClickHandler, false);
function leftClickHandler(e) {
    const cursor = new Vector(e.clientX, e.clientY);
    const tl = GAME.getLeftCorner();
    SHOOT_VEC = me.pos.neg().add(tl.neg()).add(cursor);
}

let CHARGE = false

document.addEventListener('contextmenu', (event) => {
    event.preventDefault();
    CHARGE = true;
})


let needResize = true;
window.addEventListener('resize', () => {
    needResize = true;
}, false);

function resizeCanvas() {
    const canvas = document.getElementById("main");
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    needResize = false;
}


function draw_game(draw_context, game) {
    if (needResize) {
        resizeCanvas();
    }
    game.render(draw_context);
}


const CELL_SIZE_IN_PIXELS = 20;


async function redirect_back() {
    window.location.href = 'start_menu.html';
}

async function check_creds() {
    if (localStorage.getItem('creds') === null) {
        await redirect_back();
    }
}


async function entrypoint() {
    await check_creds();
    const init_message = {
        "command": "join",
        "data": JSON.parse(localStorage.getItem('creds'))
    }
    console.debug(init_message);

    const canvas = document.getElementById("main");
    const cxt = canvas.getContext("2d");

    const socket = new WebSocket(WS_ENDPOINT);

    setInterval(sendCommands, 0.3)
    function sendCommands() {
        let direction = new Vector(0, 0);
        if (GO_RIGHT) {
            direction = direction.add(new Vector(5, 0));
        }
        if (GO_LEFT) {
            direction = direction.add(new Vector(-5, 0));
        }
        if (GO_UP) {
            direction = direction.add(new Vector(0, -5));
        }
        if (GO_DOWN) {
            direction = direction.add(new Vector(0, 5));
        }

        if (Math.abs(direction.y) >= 1e-5 || Math.abs(direction.x) >= 1e-5) {
            const command = new MoveCommand(direction, me, CHARGE);
            socket.send(JSON.stringify(command.to_msg()));
        }
        playerCommand.length = 0;
        CHARGE = false;

        if (SHOOT_VEC !== null) {
            const command = new ShootCommand(SHOOT_VEC, me);
            socket.send(JSON.stringify(command.to_msg()));
            SHOOT_VEC = null;
        }
    }


    socket.addEventListener('close', ev => {
        console.debug(`connection closed cauz ${ev.reason}`);
        window.location.href = '/frontend/start_menu.html'
    })

    socket.addEventListener('error', ev => {
        console.debug(`error!`);
    })

    socket.addEventListener('open', ev => {
        socket.send(JSON.stringify(init_message))
    });

    const shoot_timer = new CDTimer('next shoot (LKM)');
    const charge_timer = new CDTimer('next charge (PKM)');


    socket.addEventListener('message', ev => {
        let data = JSON.parse(ev.data);
        console.debug(data);
        if (data["command"] === "join") {
            console.log(data);
            // TODO: handle wrong creds
            const map = new Field(data["data"]['map'], CELL_SIZE_IN_PIXELS);
            GAME = new Game(map, [me], cxt);
            cxt['maxHP'] = data["data"]["HP"];
            cxt['hitboxWidth'] = data["data"]["hitboxWidth"] * CELL_SIZE_IN_PIXELS;
            cxt['hitboxHeight'] = data["data"]["hitboxHeight"] * CELL_SIZE_IN_PIXELS;
            shoot_timer.maxValue = data["data"]["shootCD"];
            charge_timer.maxValue = data["data"]["chargeCD"];

            shoot_timer.render();
            charge_timer.render();

            console.log(GAME);
        } else if (data["command"] === "update") {
            const new_center = (new Vector(data["data"]["posX"], data["data"]["posY"])).mul(CELL_SIZE_IN_PIXELS);
            GAME.center = new_center;
            me.pos = new_center;
            me.hp = data["data"]["HP"]
            
            if (data.data.new_map !== undefined) {
                const field = new Field(data.data.new_map, CELL_SIZE_IN_PIXELS);
                GAME.field = field;
            }

            shoot_timer.rerender(data["data"]["shootCD"]);
            charge_timer.rerender(data["data"]["chargeCD"]);

            // TODO ????
            const enemies = [];
            data["data"]["visibleEnemeis"].forEach(enemy => {
                enemies.push(new Player((new Vector(enemy.posX, enemy.posY).mul(CELL_SIZE_IN_PIXELS)), enemy.HP))
            })

            GAME.players = [
                me,
                ...enemies
            ]

            const areas = [];
            data.data.visibleDamage.forEach(area => {
                if (area.type === "range") {
                    areas.push(new Bullet((new Vector(area.posX, area.posY)).mul(CELL_SIZE_IN_PIXELS)));
                }
            });

            GAME.damage_areas = [
                ...areas
            ]

            draw_game(cxt, GAME);
        } else if (data.command == "new_player") {
            (new Notification(`new player: ${data.data.name}`)).render();
        } else if (data.command == "player_loose") {
            (new Notification(`player loose: ${data.data.name}`)).render();
        } else if (data.command == "player_win") {
            (new Notification(`player win: ${data.data.name}`)).render();
        }
    })
}

entrypoint();
