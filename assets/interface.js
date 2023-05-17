const outputDiv = document.getElementById('output');
const inputField = document.getElementById('input');
const sendButton = document.getElementById('sendBtn');
const sendSubscribe = document.getElementById('sendSub');
let websocket;

// Connect to the WebSocket server
function connectWebSocket() {
    websocket = new WebSocket('ws://127.0.0.1:8000/ws');

    websocket.onopen = () => {
        outputDiv.innerHTML += '<p>WebSocket connection established.</p>';
    };

    websocket.onmessage = (event) => {
        outputDiv.innerHTML += '<p>Received: ' + event.data + '</p>';
    };

    websocket.onclose = () => {
        outputDiv.innerHTML += '<p>WebSocket connection closed.</p>';
    };

    websocket.onerror = (error) => {
        outputDiv.innerHTML += '<p>Error: ' + error + '</p>';
    };
}

function subscribe(topic) {
    const payload = {
        function: "SUBSCRIBE_TOPIC",
        parameters: {
            name: topic
        }
    }
    websocket.send(JSON.stringify(payload));
    outputDiv.innerHTML += "<p>Sent: " + JSON.stringify(payload) + "</p>";
}

// Send a message through the WebSocket
function sendMessage() {
    const message = inputField.value;
    websocket.send(message);
    outputDiv.innerHTML += '<p>Sent: ' + message + '</p>';
    inputField.value = '';
}

// Connect WebSocket button click event
connectWebSocket();

// Send message button click event
sendButton.addEventListener('click', sendMessage);
sendSubscribe.addEventListener("click", e => {
    subscribe(inputField.value);
});

