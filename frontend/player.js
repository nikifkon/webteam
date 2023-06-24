import Vector from "./vector.js";

export class Player {
    constructor(init_pos) {
        this.pos = init_pos || new Vector(10, 10);
        Player.img = document.getElementById("melee_sprite")
    }

    static img;

    // Render
    render(ctx) {
        ctx.save();
        ctx.translate(this.pos.x, this.pos.y);
        ctx.drawImage(Player.img, 0, 0);
        ctx.restore();
    }
}