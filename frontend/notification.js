const notificationContainer = document.createElement('div');
notificationContainer.style.position = 'absolute';
notificationContainer.style.width = '100px';
notificationContainer.style.backgroundColor = 'white';
notificationContainer.style.bottom = '0px';
document.querySelector('body').appendChild(notificationContainer);

export class Notification {
    constructor(text) {
        this.text = text;
    }

    render() {
        const wrapper = document.createElement('div');
        const text = document.createTextNode(this.text);
        wrapper.appendChild(text);
        notificationContainer.appendChild(wrapper);
        setTimeout(() => {
            wrapper.remove()
        }, 10000)
    }
}