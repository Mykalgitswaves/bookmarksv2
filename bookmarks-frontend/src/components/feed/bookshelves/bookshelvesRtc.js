import { urls } from "../../../services/urls";
import { helpersCtrl } from "../../../services/helpers";

const { getCookieByParam } = helpersCtrl

export const eventFunctionMapping = {
    'opened': {
        function: (data) => (console.log(data.detail))
    },
    'closed': {
        function: (data) => (console.log(data.detail))
    }
}

// const BOOKSHELF_EVENT_TYPES = [
//     'opened',
//     'closed'
// ]

// const event = {
//     "type": "post",
// }
// const urlParams = new URLSearchParams(window.location.search);
// const bookshelf_id = urlParams.get('bookshelf');

// This might not work;
export const ws = {
    client: getCookieByParam(['token']),
    socket: null, // Initialize socket variable
    
    newSocket: () => {
        ws.socket = new WebSocket(urls.rtc.bookshelf('new')); // Assign the socket to ws.socket
        return ws.socket;
    },
    
    createNewSocketConnection: () => {
            ws.newSocket(); // Create a new socket if it doesn't exist or if it's closed
        
            ws.socket.onopen = (e) => { 
                console.log('socket opened at', ws.socket, e)
            };

            ws.socket.onmessage = (e) => {
                const data = JSON.parse(e.data);
                console.log(data, 'onmessage');
            };

            console.log(ws.socket)
    },
    
    unsubscribeFromSocketConnection() {
        // We need to make sure websocket exists and the socket is not closed before we close.
        if (ws.socket && ws.socket.readyState !== WebSocket.CLOSED) {
            ws.socket.close();
        }
    }
}
