export const PubSub = {
    subscribers: new Map(),

    subscribe(event, subscriber) {
        console.log('subscription callback', event)
        if (!this.subscribers.has(event)) {
            this.subscribers.set(event, []);
        }
        this.subscribers.get(event).push(subscriber);
    },

    unsubscribe(event, subscriber) {
        if(this.subscribers.has(event)) {
            const updatedSubscribers = this.subscribers.get(event).filter(sub => sub !== subscriber);
            if (updatedSubscribers.length > 0) {
                this.subscribers.set(event, updatedSubscribers);
            } else {
                this.subscribers.delete(event);
            }
        }
    },

    publish(event, payload) {
        console.log(event, payload, 'publish event')
        if (this.subscribers.has(event)) {
            this.subscribers.get(event).forEach(subscriber => {
                subscriber(payload)
            });
        }
    }
}