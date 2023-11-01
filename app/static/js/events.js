const currentHostname = window.location.hostname;
const currentPort = window.location.port;
let websocketUrl = `ws://${currentHostname}`;

if (currentPort && currentPort.length) {
    websocketUrl = `${websocketUrl}:${currentPort}`;
}

websocketUrl = `${websocketUrl}/ws`;

console.log('websocketUrl', websocketUrl);

function getGenerateListImageUpdates(
    taskId,
    listId
) {
    console.log('[getGenerateImageUpdates]', taskId);
    const url = `${websocketUrl}/${taskId}`;
    const socket = new ReconnectingWebSocket(url);
    socket.debug = true

    socket.onopen = ()=>{
        // $('#websocket-status').removeClass('reconnecting').addClass('open')
        console.log('websocket open')
    }

    socket.onclose = ()=>{
        // $('#websocket-status').removeClass('open').addClass('reconnecting')
        console.log('websocket closed')
    }

    socket.onmessage = async (msg) => {
        let data = {};
        try {
            data = msg.data && JSON.parse(msg.data);
            console.log('data', data);
        } catch (err) {
            console.error('websocket msg is not JSON');
            console.log('websocket message', msg);
        }

        if (data.task_results && data.task_results.error && data.task_results.error.length) {
            console.error(`Sorry, there was an error generating images: ${data.task_results.error}`);
            $('#generate-scene-image-error').show().find('.message').text(data.task_results.error);
            $sceneImagesLoader.hide();
        } else if (data.completed) {
            console.log("SCENE IMAGE GENERATION FINISHED");
            $(`#list-generate-image-${listId}`).removeClass('spinner-border');
            refreshLists();
        }
    }
}
