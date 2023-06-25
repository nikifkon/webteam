import Vector from "./vector.js";

export class Player {
    constructor(init_pos, width, height, cell_size) {
        this.pos = init_pos || new Vector(10, 10);
        this.width = width;
        this.height = height;
        Player.img = document.getElementById("melee_sprite")
    }

    static img;

    // Render
    render(ctx) {
        console.log(this);
        ctx.save();
        ctx.translate(this.pos.x, this.pos.y);
        ctx.translate(-this.width/2, -this.height/2);
        ctx.drawImage(Player.img, 0, 0);
        ctx.restore();
    }
}