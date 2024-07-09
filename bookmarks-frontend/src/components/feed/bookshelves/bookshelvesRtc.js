import { urls, navRoutes } from "../../../services/urls";
import { helpersCtrl } from "../../../services/helpers";
import { ref } from 'vue';
import { db } from "../../../services/db";

const { getCookieByParam } = helpersCtrl

// what we use to tell the client a change happenend.
const wsDataLoaded = new CustomEvent('ws-loaded-data', {
    detail: {
      value: 'true'  
    }
});

export const wsConnectionError = new CustomEvent('ws-connection-error', {
    detail: {
        message: 'An error happened, please try reordering again.'
    }
});

// Want to clean up after the element is removed from v-dom.
export const removeWsEventListener = () => {
    document.removeEventListener('ws-loaded-data', wsDataLoaded);
    document.removeEventListener('ws-connection-error', wsConnectionError);
}

export const ws = {
    // client: getCookieByParam(['token']),
    socket: null, // Initialize socket variable
    books: [],
    secure_token: null,
    connection_address: '',
    current_state: '', // Use current state to lock out ui or inform users that reorders are occuring. 
    // This is set by the on message function. We can get really granular here and our ws manager in 
    // fastapi can help us with some parralellization issues.

    // #TODO Add a get request using the login token to get a new returned token specifically for the websocket connection. 
    newSocket: async (connection_address) => {
        // Get request that gets the token
        try {
            // Get request that gets the token
            const res = await db.get(urls.rtc.getBookshelfWsToken(connection_address));
    
            ws.secure_token = res.token;
            ws.connection_address = connection_address;
            ws.socket = new WebSocket(urls.rtc.bookshelf(connection_address, ws.secure_token));
        } catch (error) {
            console.error('Error creating new socket:', error);

            // How do we want to handle this?
        }
    },
    
    createNewSocketConnection: async (connection_address) => {
        if (!ws.socket) {
            await ws.newSocket(connection_address); // Create a new socket if it doesn't exist or if it's closed
        
            ws.socket.onopen = (e) => { 
                console.log('Socket opened at', ws.socket, e)
            };

            ws.socket.onmessage = (e) => {
                const data = JSON.parse(e.data);
                // if(!ws.secure_token && data?.token){
                //     ws.secure_token = data.token;
                // }
                // cases.
                if(data?.state === 'locked'){
                    console.log('locked while reordering', data);
                    ws.current_state = 'locked'
                // unlocked means we are also returning reordered data 
                } else if (data?.state === 'unlocked') {
                    console.log('unlocked', data);
                    ws.current_state = 'unlocked';
                    // make sure we have bookshelves saved 
                    if (data.data.length) {
                        ws.books = data.data;
                        // Used to reload data.
                        document.dispatchEvent(wsDataLoaded);
                    }
                } else if(data.state === 'error'){
                    // TODO: Add a fetch bookshelf to reset cache and front end from database.
                    ws.state = e.data.state;
                    ws.data = async () => await getBookshelf(ws.connection_address)();
                }
                // How we are watching data being sent from a websocket..
            };

            ws.socket.onclose = (e) => {
                console.log('Socket closed', e);
                if(ws.socket){
                    ws.socket.close(1000);
                    ws.connection_address = '';
                    ws.socket = null;
                }
            }
        }
    },

    unsubscribeFromSocketConnection() {
        // We need to make sure websocket exists and the socket is not closed before we close.
        if (ws.socket && ws.socket.readyState !== WebSocket.CLOSED) {
            ws.socket.close(1000);
            ws.connection_address = '';
            ws.socket = null;
        }
    },

    sendData(data) {
        if (ws.socket && ws.socket.readyState === WebSocket.OPEN) {
            data.token = ws.secure_token;
            ws.socket.send(JSON.stringify(data));
            console.log(data);
        } else {
            console.error("WebSocket connection is not open, reconnecting.");
            ws.createNewSocketConnection(ws.connection_address);
            document.dispatchEvent(wsConnectionError);
        }
    },
}

// Used to let client know state without having to import entire ws object.
export const wsCurrentState = ref(ws.current_state);

export async function getBookshelf(bookshelf_id){
    await db.get(urls.rtc.bookShelfTest(bookshelf_id))
}

export function goToBookshelfSettingsPage(router, user_id, bookshelf_id){
    router.push(`/feed/${user_id}/bookshelves/${bookshelf_id}/edit`)
}

export function removeEventListenersFn(element) {
    element.removeEventListeners('dragstart');
    element.removeEventListeners('dragend');
}

export function convertListToMap(list, key) {
    let result = new Map();
    list.forEach((data) => {
        result.set(data[key], data);
    })
    return result;
}

export async function get_bookshelf(shelfName) {
    let result = {};
    let bookshelfPromise = await db.get(urls.rtc.bookShelfTest(shelfName)).then((res) => { result = res });
    Promise.resolve(bookshelfPromise).then(() => {
        return result
    });
}

export const viewBookshelvesForSection = (user_id, location) => {
    return navRoutes.toBookshelfSectionPage(user_id, location);
}