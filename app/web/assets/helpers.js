/*
* Client helper functions
*   helps prevent clutter in the actual client
*/

const helpers = {
    createTopicButton: function(content, id) {
        let btn = document.createElement('button');
        btn.classList.add('list-group-item');
        btn.classList.add('list-group-item-action');
        btn.setAttribute('id', id);

        let div = document.createElement('div');
        div.classList.add("d-flex", "justify-content-between");
        div.innerText = content;
        
        btn.appendChild(div);
        return btn
    },
    createAddTopicButton: function() {
        let text = '<i class="bi bi-plus"></i>&nbsp;New';
        let btn = document.createElement('button');
        btn.classList.add('list-group-item');
        btn.classList.add('list-group-item-action');
        btn.innerHTML = text;
        return btn
    },
    createChatMessage: function(content, side='left') {
        let parent = document.createElement('div');
        parent.classList.add("d-flex")
        side == 'left' ? parent.classList.add("justify-content-start") : parent.classList.add("justify-content-end");

        let child = document.createElement('div');
        child.classList.add("border", "rounded", "p-2", "mb-2", "px-3", "mw-90");
        child.innerText = content;

        parent.appendChild(child);
        return parent
    }
}

export { helpers }
