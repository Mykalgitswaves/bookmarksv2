import { urls } from "../../../services/urls";
import { helpersCtrl } from "../../../services/helpers";
import { ref } from 'vue';
import { db } from "../../../services/db";

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
    data: ref([]),
    newSocket: () => {
        ws.socket = new WebSocket(urls.rtc.bookshelf('new')); // Assign the socket to ws.socket
        return ws.socket;
    },
    
    createNewSocketConnection: () => {
        if(!ws.socket){
            ws.newSocket(); // Create a new socket if it doesn't exist or if it's closed
        
            ws.socket.onopen = (e) => { 
                console.log('socket opened at', ws.socket, e)
            };

            ws.socket.onmessage = (e) => {
                const res = JSON.parse(e.data)
                const data = JSON.parse(res.data)
                if(res.type === "add"){
                    ws.data.value.push(data);
                } else if (res.type === "remove") {
                    ws.data.value = ws.data.value.filter((d) => d !== ws.data.value[res.data])
                }
                // How we are watching data being sent from a websocket. v fast.
                console.log(ws.data.value)
            };
        }
    },
    
    unsubscribeFromSocketConnection() {
        // We need to make sure websocket exists and the socket is not closed before we close.
        if (ws.socket && ws.socket.readyState !== WebSocket.CLOSED) {
            ws.socket.close();
        }
    },
}


export async function getBookshelf(bookshelf_id){
    await db.get(urls.rtc.bookShelfTest(bookshelf_id))
}

export function goToBookshelfSettingsPage(router, user_id, bookshelf_id){
    router.push(`/feed/${user_id}/bookshelves/${bookshelf_id}/edit`)
}