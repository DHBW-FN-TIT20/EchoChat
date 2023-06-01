/*
 * EchoChat client implementation
 *   handles client functionality
 */

import { helpers } from './helpers.js'

class client {
    constructor(uri = 'ws://127.0.0.1:8000/ws') {
        // startup code
        this.websocket = this.connectWebSocket(uri)
        this.initListeners();
        this.topics = [];
        this.statuses = {};
        this.sentMessage = false;
    }

    initListeners() {
        // assign event listerners
        document.getElementById('topicButton').addEventListener('click', () => {
            // toggle spinner on
            document.getElementById('spinner').classList.remove('hidden');
            document.getElementById('topics').classList.add('hidden');
            this.listTopics();
        });
        document.getElementById('send').addEventListener('click', this.initSend);
        document.getElementById('input').addEventListener('keydown', e => {
            if (e.key === "Enter") {
                let self = this;
                this.initSend(self);
            }
        });
    }
    initSend(self) {
        let message = document.getElementById('input').value;
        if (message.trim() !== "") {
            const topic = document.getElementById('currentTopic').innerText;
            document.getElementById('input').value = ""
            self.publish(topic, message.trim());
            self.sentMessage = message.trim();
        } else {
            document.getElementById('input').value = "";
        }
    }

    successHandler(message) {
        switch (message.function) {
            case 'SUBSCRIBE_TOPIC':
                // client tried subscribing to topic
                document.getElementById('closeTopicsModal').click();
                document.getElementById('currentTopic').innerText = message.data.topic;
                document.getElementById('chat').innerHTML = ''; // clear chat window
                break;
            case 'UNSUBSCRIBE_TOPIC':
                // client tried unsubscribing from topic
                break;
            case 'PUBLISH_TOPIC':
                // client tried to publish a message to a topic
                this.sentMessage = false; // reset
                break;
            case 'LIST_TOPICS':
                // client requested a list of topic
                this.handleTopicList(message);
                break;
            case 'GET_TOPIC_STATUS':
                // client requested information about a topic

                let status = message.data;
                let pos = this.topics.indexOf(status.topic);
                let html = `<span class="">${status.subscribers}</span`;
                document.getElementById(`topic${pos}`).querySelector('div').innerHTML += html;

                this.statuses[pos.toString()] = status;

                // toggle spinner off
                document.getElementById('spinner').classList.add('hidden');
                document.getElementById('topics').classList.remove('hidden');

                break;
            case 'UPDATE_TOPIC':
                // a subscribed topic was updated
                this.handleTopicUpdate(message)
                break;
            default:
                console.error("unknown message received");
        }
    }

    errorHandler(message) {
        console.error(message);
    }

    handleTopicList(message) {
        let listElement = document.getElementById('topics');
        listElement.innerHTML = "";

        this.topics = message.data.topic_list

        for (let i = 0; i < this.topics.length; i++) {
            let btn = helpers.createTopicButton(this.topics[i], `topic${i}`, this.executeSubscribe)
            btn.addEventListener('click', () => {
                // unsubscribe from existing topic
                let currentTopic = document.getElementById('currentTopic').innerText;
                console.log(`unsubscribing from '${currentTopic}'`)
                this.unsubscribe(currentTopic);

                // subscribe to new topic
                console.log(`subscribing to '${this.topics[i]}'`)
                this.subscribe(this.topics[i]);

                // toggle spinner on
                document.getElementById('spinner').classList.add('hidden');
                document.getElementById('topics').classList.remove('hidden');
            });
            listElement.appendChild(btn);
        }

        let add = helpers.createAddTopicButton();
        add.addEventListener('click', e => {
            if (e.target === add && !e.target.classList.contains('converted')) {
                let html = '<div class="d-flex justify-content-between">' +
                    '<input type="text" id="topicInput" class="form-control form-control-sm me-2">' +
                    '<button class="btn btn-sm btn-outline-secondary" id="topicInputButton">Choose</button></div>'
                e.target.innerHTML = html;
                let topicInput = document.getElementById("topicInput");
                topicInput.addEventListener('keydown', e => {
                    if (e.key === "Enter") {
                        let client = this;
                        subTopic(client);
                    }
                });
                document.getElementById('topicInputButton').addEventListener('click', () => {
                    let client = this;
                    subTopic(client)
                });

                function subTopic(client) {
                    // unsubscribe from existing topic
                    let currentTopic = document.getElementById('currentTopic').innerText;
                    console.log(`unsubscribing from '${currentTopic}'`);
                    client.unsubscribe(currentTopic);

                    // subscribe to new topic
                    console.log(`subscribing to '${topicInput.value}'`);
                    client.subscribe(topicInput.value);

                    // toggle spinner on
                    document.getElementById('spinner').classList.add('hidden');
                    document.getElementById('topics').classList.remove('hidden');
                }

                e.target.classList.add('converted');
                topicInput.focus();
            }
        });
        listElement.appendChild(add);

        if (this.topics.length < 1) {
            // toggle spinner off
            document.getElementById('spinner').classList.add('hidden');
            listElement.classList.remove('hidden');
        } else {
            for (let i = 0; i < this.topics.length; i++) {
                // this
                this.topicStatus(this.topics[i]);
            }
        }
    }

    handleTopicUpdate(message) {
        let currentTopic = document.getElementById('currentTopic').innerText;
        if (message.data.name === currentTopic) {
            let chat = document.getElementById('chat');

            if (this.sentMessage !== false && message.data.message === this.sentMessage) {
                chat.appendChild(helpers.createChatMessage(message.data.message, 'right'));
                this.sentMessage = false;
            } else {
                chat.appendChild(helpers.createChatMessage(message.data.message));
            }
            chat.scrollTop = chat.scrollHeight;
        } else {
            console.warn(`chat message received from a different topic: ${message.data.name}, ${message.data.timestamp}, ${message.data.message}`)
        }
    }



    /*============ Interface ==============*/

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
        switch (message.status) {
            case 'success':
                this.successHandler(message);
                break;
            default:
                this.errorHandler(message);
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
        this.sendRequest('SUBSCRIBE_TOPIC', { name: topic });
    }
    unsubscribe(topic) {
        this.sendRequest('UNSUBSCRIBE_TOPIC', { name: topic });
    }
    publish(topic, message) {
        this.sendRequest('PUBLISH_TOPIC', { name: topic, message: message });
    }
    listTopics() {
        this.sendRequest('LIST_TOPICS', {})
    }
    topicStatus(topic) {
        this.sendRequest('GET_TOPIC_STATUS', { name: topic })
    }
}

export { client }

