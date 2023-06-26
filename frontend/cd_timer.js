const cdContainer = document.createElement('div');
cdContainer.className = 'cdContainer';

document.querySelector('body').appendChild(cdContainer);

export class CDTimer {
    constructor(name, maxValue) {
        this.name = name;
        this.maxValue = maxValue;
        this.physWidth = 250;
        this.front = null;
    }

    render() {
        const wrapper = document.createElement('div');
        wrapper.className = 'cdTimerWrapper';
        
        const wrapper2 = document.createElement('div');
        wrapper2.style.width = this.physWidth + 'px';
        wrapper2.className = 'cdTimerWrapper2';
        const back = document.createElement('div');
        back.className = 'back';
        const front = document.createElement('div');
        front.className = 'front';
        back.style.width = this.physWidth + 'px';
        front.style.width = 0 + 'px';

        const front_text = document.createElement('div');
        front_text.appendChild(document.createTextNode(this.name));
        front_text.style.width = this.physWidth + 'px';
        front_text.className = 'front_text';

        wrapper2.appendChild(back);
        wrapper2.appendChild(front);
        wrapper2.appendChild(front_text)
        wrapper.appendChild(wrapper2);

        cdContainer.appendChild(wrapper);

        this.front = front;
    }

    rerender(cd) {
        console.log(cd / this.maxValue * this.physWidth + 'px');
        this.front.style.width = cd / this.maxValue * this.physWidth + 'px';
    }
}