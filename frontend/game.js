import Vector from './vector.js';

export class Game {
    constructor(field, players) {
        this.field = field;
        this.players = players;
        this.center = new Vector(500, 300);
    }

    render(ctx) {
        const leftCorner = this.getLeftCorner(ctx, this.center);
        ctx.save();
        ctx.translate(leftCorner.x, leftCorner.y);
        this.field.render(ctx);  // slow! TODO: rerender only chunks
        for (let player of this.players) {
            player.render(ctx);
        }
        ctx.restore();
    }

    getLeftCorner(ctx, center) {
        return (new Vector(ctx.canvas.width, ctx.canvas.height)).mul(0.5).add(center.neg());
    }
}