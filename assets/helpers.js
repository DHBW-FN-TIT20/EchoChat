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
        btn.innerText = content;
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
}

export { helpers }
