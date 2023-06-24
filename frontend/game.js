import Vector from './vector.js';

export class Game {
    constructor(field, players, context) {
        this.field = field;
        this.players = players;
        this.context = context;
        this.damage_areas = []
        this.center = new Vector(this.field.getPixelWidth() / 2, this.field.getPixelHeight() / 2);
    }

    render(ctx) {
        const leftCorner = this.getLeftCorner(ctx);
        console.debug(this.center, leftCorner);
        
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
        this.field.render(ctx, leftCorner);  // slow! TODO: rerender only chunks
        console.debug(this.players);
        
        ctx.save();
        ctx.translate(leftCorner.x, leftCorner.y);
        for (let player of this.players) {
            player.render(ctx);
        }

        for (let area of this.damage_areas) {
            area.render(ctx);
        }
        ctx.restore();
    }

    getLeftCorner(ctx) {
        return (new Vector(this.context.canvas.width, this.context.canvas.height)).mul(0.5).add(this.center.neg());
    }
}