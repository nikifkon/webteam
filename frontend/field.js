export class Field {
    constructor(pattern, cell_size) {
        this.cells = [];
        for (let line of pattern.split('\n')) {
            this.cells.push([]);
            for (let cell_type of line) {
                let cell = cell_type == 'F' ? new Free() : new Wall();
                this.cells[this.cells.length - 1].push(cell);
            }
        }
        this.width = pattern.split('\n')[0].length - 1;
        this.height = pattern.split('\n').length - 1;
        this.cell_size = cell_size;
    }

    // Render
    render(ctx) {
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                ctx.save();
                ctx.translate(x * this.cell_size, y * this.cell_size);
                this.cells[y][x].render(ctx);
                ctx.restore();
            }
        }
    }
}


export class Cell {
    constructor() {
    }
}

export class Free extends Cell {
    constructor() {
        super();
        Free.img = new Image();
        Free.img.src = "free_sprite2x2.png";
    }

    static img;

    render(ctx) {
        ctx.drawImage(Free.img, 0, 0);
    }
}

export class Wall extends Cell {
    constructor() {
        super();
        Wall.img = new Image();
        Wall.img.src = "free_sprite.png";
    }

    static img;
}