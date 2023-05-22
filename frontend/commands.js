export class MoveCommand {
    constructor(vector, player) {
        this.vector = vector;
        this.player = player;
    }

    execute() {
        this.player.pos = this.player.pos.add(this.vector);
    }
}