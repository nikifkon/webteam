export default class Vector {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }

    add(other) {
        return new Vector(this.x + other.x, this.y + other.y)
    }

    neg() {
        return this.mul(-1);
    }

    mul(alpha) {
        return new Vector(alpha * this.x, alpha * this.y);
    }
}