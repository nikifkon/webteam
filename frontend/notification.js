const notificationContainer = document.createElement('div');
notificationContainer.className = 'notificationContainer';

document.querySelector('body').appendChild(notificationContainer);

export class Notification {
    constructor(text, color) {
        this.text = text;
        this.color = color || 'azure';
    }

    render() {
        const wrapper = document.createElement('div');
        wrapper.className = 'notificationWrapper';
        wrapper.style.background = this.color;
        const text = document.createTextNode(this.text);
        wrapper.appendChild(text);
        notificationContainer.appendChild(wrapper);
        setTimeout(() => {
            wrapper.remove()
        }, 10000)
    }
}