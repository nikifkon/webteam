export class Field {
    constructor(pattern, cell_size) {
        this.cells = [];
        for (let line of pattern.split('\n')) {
            this.cells.push([]);
            for (let cell_type of line) {
                let cell = new None();
                if (cell_type === "F") {
                    cell = new Free();
                } else if (cell_type === "W") {
                    cell = new Wall();
                } else if (cell_type === "D") {
                    cell = new Fire();
                }
                this.cells[this.cells.length - 1].push(cell);
            }
        }
        this.width = pattern.split('\n')[0].length - 1;
        this.height = pattern.split('\n').length - 1;
        this.cell_size = cell_size;
        this._field_image_data = null;
    }

    getPixelWidth() {
        return this.width * this.cell_size;
    }

    getPixelHeight() {
        return this.height * this.cell_size;
    }

    getField(ctx) {
        if (this._field_image_data === null) {
            const canvas = ctx.canvas;
            const init_width = canvas.width;
            const init_height = canvas.height;
            canvas.width = this.getPixelWidth() + 100;
            canvas.height = this.getPixelHeight() + 100;
            ctx.beginPath();

            for (let y = 0; y < this.height; y++) {
                for (let x = 0; x < this.width; x++) {
                    ctx.save();
                    ctx.translate(x * this.cell_size, y * this.cell_size);
                    this.cells[y][x].render(ctx);
                    ctx.restore();
                }
            }
            
            this._field_image_data = ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
            canvas.width = init_width;
            canvas.height = init_height;
        }
        return this._field_image_data;
    }

    // Render
    render(ctx, leftCorner) {
        ctx.putImageData(this.getField(ctx), leftCorner.x, leftCorner.y)
    }
}


export class Cell {
    constructor() {
    }
}

export class Free extends Cell {
    constructor() {
        super();
        Free.img = document.getElementById("free_sprite")
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
        Wall.img.src = "wall_sprite.png";
    }

    static img;

    render(ctx) {
        ctx.drawImage(Wall.img, 0, 0);
    }
}

export class None extends Cell {
    constructor() {
        super();
        None.img = document.getElementById("none_sprite")
    }

    static img;

    render(ctx) {
        ctx.drawImage(None.img, 0, 0);
    }
}

export class Bullet extends Cell {
    constructor(pos) {
        super();
        this.pos = pos;
        Bullet.img = document.getElementById("bullet_sprite")
    }

    static img;

    render(ctx) {
        ctx.save();
        ctx.translate(this.pos.x, this.pos.y);
        ctx.drawImage(Bullet.img, 0, 0);
        ctx.restore();
    }
}

export class Fire extends Cell {
    constructor() {
        super();
        Fire.img = document.getElementById("fire_sprite");
    }

    render(ctx) {
        ctx.drawImage(Fire.img, 0, 0);
    }
}