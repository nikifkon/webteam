export class MoveCommand {
    constructor(vector, player) {
        this.vector = vector;
        this.player = player;
    }

    execute() {
        this.player.pos = this.player.pos.add(this.vector);
    }
    
    to_msg() {
        return {
            "command": "move",
            "data": {
                "vecX": this.vector.x,
                "vecY": this.vector.y
            }
        }
    }
}

export class ShootCommand {
    constructor(vector, player) {
        this.vector = vector;
        this.player = player;
    }

    to_msg() {
        return {
            "command": "shoot",
            "data": {
                "vecX": this.vector.x,
                "vecY": this.vector.y
            }
        }
    }
}