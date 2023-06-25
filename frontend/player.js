import Vector from "./vector.js";

export class Player {
    constructor(init_pos, hp) {
        this.pos = init_pos || new Vector(10, 10);
        this.hp = hp;
        Player.img = document.getElementById("melee_sprite")
    }

    static img;

    // Render
    render(cxt) {
        cxt.save();
        cxt.translate(this.pos.x, this.pos.y);
        cxt.translate(-cxt['hitboxWidth'] / 2, -cxt['hitboxHeight'] / 2);
        cxt.drawImage(Player.img, 0, 0, cxt['hitboxWidth'], cxt['hitboxHeight']);

        const hpBarWidth = cxt['hitboxWidth'];
        const hpBarHeight = 7;

        cxt.translate(0, -hpBarHeight - 5);
        cxt.beginPath();
        cxt.rect(0, 0, hpBarWidth, hpBarHeight);
        cxt.fillStyle = "gray";
        cxt.fill();

        cxt.beginPath();
        cxt.rect(0, 0, hpBarWidth * this.hp / cxt.maxHP, hpBarHeight);
        cxt.fillStyle = "red";
        cxt.fill();

        cxt.restore();
    }
}