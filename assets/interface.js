/*
 * EchoChat interface implementation
 *  handles server interaction 
 */

class echoInterface {
    constructor(client, uri = 'ws://127.0.0.1:8000/ws'){
        this.websocket = this.connectWebSocket(uri)
        this.client = client
    }

    connectWebSocket(uri) {
        let websocket = new WebSocket(uri);

        websocket.onopen = () => {
            console.log("websocket connected")
        }
        websocket.onmessage = (event) => {
            this.handleMessage(event.data);
        }
        websocket.onclose = () => {
            // attempt reconnect
        }
        websocket.onerror = (error) => {
            this.errorHandler(error);
        }

        return websocket
    }

    handleMessage(raw) {
        let message = JSON.parse(raw);
        switch(message.status) {
            case 'success':
                this.client.successHandler(this.client, message);
                break;
            default:
                this.client.errorHandler(this.client, message);
                break;
        }
    }

    sendRequest(request, data) {
        const payload = {
            function: request,
            parameters: data,
        }
        this.websocket.send(JSON.stringify(payload));
    }

    subscribe(topic) {
        this.sendRequest('SUBSCRIBE_TOPIC', {name: topic});
    }
    unsubscribe(topic) {
        this.sendRequest('UNSUBSCRIBE_TOPIC', {name: topic});
    }
    publish(topic, message) {
        this.sendRequest('PUBLISH_TOPIC', {name: topic, message: message});
    }
    listTopics() {
        this.sendRequest('LIST_TOPICS', {})
    }
    topicStatus(topic) {
        this.sendRequest('GET_TOPIC_STATUS', {name: topic})
    }

}

export { echoInterface }

