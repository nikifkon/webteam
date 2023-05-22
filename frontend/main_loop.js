import { Game } from './game.js';
import { Field, Free, Wall } from './field.js';
import { Player } from './player.js';
import Vector from './vector.js';
import { MoveCommand } from './commands.js';


const playerCommand = [];
const player = new Player();

document.addEventListener("keydown", keyDownHandler, false);
function keyDownHandler(e) {
    if (e.key === "Right" || e.key === "ArrowRight" || e.key === "d") {
        console.log('right');
        playerCommand.push(new MoveCommand(new Vector(5, 0), player));
    } else if (e.key === "Left" || e.key === "ArrowLeft" || e.key === "a") {
        playerCommand.push(new MoveCommand(new Vector(-5, 0), player));
    }
    if (e.key === "Up" || e.key === "ArrowUp" || e.key === "w") {
        playerCommand.push(new MoveCommand(new Vector(0, -5), player));
    } else if (e.key === "Down" || e.key === "ArrowDown" || e.key === "s") {
        playerCommand.push(new MoveCommand(new Vector(0, 5), player));
    }
}

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

let previousTime = 0.0;
function tick(draw_context, game, time) {
    if (needResize) {
        resizeCanvas();
    }
    const dt = time - previousTime;
    previousTime = time;
    for (let command of playerCommand) {
        command.execute();
    }
    playerCommand.length = 0;
    console.log('tick');
    game.render(draw_context);
    requestAnimationFrame(time => tick(draw_context, game, time));
}


const CELL_SIZE_IN_PIXELS = 20


function entrypoint() {
    fetch('free100x30.txt')
        .then(response => response.text())
        .then(pattern => {
            const canvas = document.getElementById("main");
            const ctx = canvas.getContext("2d")
            const map = new Field(pattern, CELL_SIZE_IN_PIXELS);
            const game = new Game(map, [player]);
            Free.img.onload = () => {  // TODO
                Wall.img.onload = () => {
                    // Player.img.onload = () => {
                        console.log(1);
                        requestAnimationFrame(time => {
                            console.log(2);
                            previousTime = time;
                            requestAnimationFrame(time => tick(ctx, game, time));
                        });
                    // }
                }
            }
        })

}

entrypoint();