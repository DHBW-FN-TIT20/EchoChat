/*
 * EchoChat client implementation
 *   handles client functionality
 */

import { echoInterface } from './interface.js'
import { helpers } from './helpers.js'

class client {
    constructor() {
        // startup code
        this.int = new echoInterface(this)
        this.initListeners();
        this.topics = [];
        this.statuses = {};
    }

    initListeners() {
        // assign event listerners
        document.getElementById('topicButton').addEventListener('click', () => {
            // toggle spinner on
            document.getElementById('spinner').classList.remove('hidden');
            document.getElementById('topics').classList.add('hidden');
            this.int.listTopics();
        });
        document.getElementById('send').addEventListener('click', () => {
            const topic = document.getElementById('currentTopic').innerText;
            const message = document.getElementById('input').value;
            console.log(topic);
            this.int.publish(topic, message);
        });
    }

    successHandler(self, message) {
        switch (message.function) {
            case 'SUBSCRIBE_TOPIC':
                // client tried subscribing to topic
                break;
            case 'UNSUBSCRIBE_TOPIC':
                // client tried unsubscribing from topic
                break;
            case 'PUBLISH_TOPIC':
                // client tried to publish a message to a topic
                break;
            case 'LIST_TOPICS':
                // client requested a list of topic

                let listElement = document.getElementById('topics');
                listElement.innerHTML = "";

                console.log(self)
                self.topics = message.data.topic_list

                for (let i = 0; i < self.topics.length; i++) {
                    let btn = helpers.createTopicButton(self.topics[i], `topic${i}`)
                    listElement.appendChild(btn);
                }
                listElement.appendChild(helpers.createAddTopicButton());

                for (let i = 0; i < self.topics.length; i++) {
                    // this
                    self.topicStatus(self.topics[i]);
                } 

                break;
            case 'GET_TOPIC_STATUS':
                // client requested information about a topic

                let status = message.data;
                let pos = self.topics.indexOf(status.topic);
                let html = `<span class="">${status.subscribers}</span`;
                document.getElementById(`topic${pos}`).innerHTML += html;

                self.statuses[pos.toString()] = status;

                // toggle spinner off
                document.getElementById('spinner').classList.add('hidden');
                listElement.classList.remove('hidden');
                
                break;
            case 'UPDATE_TOPIC':
                // a subscribed topic was updated
                break;
            default:
                console.error("unknown message received");
        }
    }

    errorHandler(self, message) {
        console.error(self, message);
    }
}

export { client }

