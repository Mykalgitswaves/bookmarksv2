import { urls } from "../../../services/urls";
import { helpersCtrl, throttle } from "../../../services/helpers";
import { ref, reactive } from 'vue';
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
    connection_address: '',

    newSocket: (connection_address) => {
        ws.connection_address = connection_address;
        ws.socket = new WebSocket(urls.rtc.bookshelf(connection_address)); // Assign the socket to ws.socket
        return ws.socket;
    },
    
    createNewSocketConnection: (connection_address) => {
        if (!ws.socket) {
            ws.newSocket(connection_address); // Create a new socket if it doesn't exist or if it's closed
        
            ws.socket.onopen = (e) => { 
                console.log('Socket opened at', ws.socket, e)
            };

            ws.socket.onmessage = (e) => {
                const data = JSON.parse(e.data);
                ws.data.value.push(data);
                // How we are watching data being sent from a websocket..
                console.log(ws.data.value);
            };
        }
    },

    unsubscribeFromSocketConnection() {
        // We need to make sure websocket exists and the socket is not closed before we close.
        if (ws.socket && ws.socket.readyState !== WebSocket.CLOSED) {
            ws.socket.close(1000);
            ws.connection_address = '';
        }
    },

    sendData(data) {
        if (ws.socket && ws.socket.readyState === WebSocket.OPEN) {
            ws.socket.send(JSON.stringify(data));
            console.log(data);
        } else {
            console.error("WebSocket connection is not open.");
        }
    },
}


export async function getBookshelf(bookshelf_id){
    await db.get(urls.rtc.bookShelfTest(bookshelf_id))
}

export function goToBookshelfSettingsPage(router, user_id, bookshelf_id){
    router.push(`/feed/${user_id}/bookshelves/${bookshelf_id}/edit`)
}

export function addEventListenersFn(element){
    let dragged;
    element.addEventListener('dragstart', (e) => {
        dragged = e.target.innerHTML;
        console.log(dragged, 'drag start')
        e.target.style.opacity = '0.4';
        e.target.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', element.innerHTML);
    });

    element.addEventListener('dragend', (e) => {
        e.stopPropagation();

        e.target.style.opacity = '1.0';
        e.target.classList.remove('dragging');
        console.log(dragged, e)
        
        return false;
    });

    element.addEventListener('drop', (e) => {
        e.preventDefault();
        // move dragged element to the selected drop target
        if (dragged !== undefined && dragged !== e.target) {
            // Swap innerHTML of dragged and dropped elements
            const tempHTML = e.target.closest('#bookId');
            e.target.outerHTML = dragged;
            dragged = tempHTML.outerHTML;
        }
    })

    element.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.target.classList.add('dragged-over');
    });

    element.addEventListener('dragleave', (e) => {
        e.target.classList.remove('dragged-over');
    });
}

export function removeEventListenersFn(element) {
    element.removeEventListeners('dragstart');
    element.removeEventListeners('dragend');
}

export const items = [
    {
        id: 'G001',
        order: 0,
        bookTitle: 'Brave New World',
        author: "Aldous Huxley",
        imgUrl: "http://books.google.com/books/content?id=TIJ5EAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
    },
    {
        id: 'G002',
        order: 1,
        bookTitle: 'Infinite Jest',
        author: "David Foster Wallace",
        imgUrl: 'http://upload.wikimedia.org/wikipedia/en/4/4f/Infinite_jest_cover.jpg',
    },
    {
        id: 'G003',
        order: 2,
        bookTitle: 'The sirens of Titan',
        author: "Kurt Vonnegut",
        imgUrl: 'http://pictures.abebooks.com/isbn/9780385333498-us.jpg',
    },
    {
        id: 'G004',
        order: 3,
        bookTitle: 'The Odyssey',
        author: "Homer",
        imgUrl: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Giuseppe_Bottani_-_Athena_revealing_Ithaca_to_Ulysses.jpg/440px-Giuseppe_Bottani_-_Athena_revealing_Ithaca_to_Ulysses.jpg',
    },
    {
        id: 'G001',
        order: 0,
        bookTitle: 'Brave New World',
        author: "Aldous Huxley",
        imgUrl: "http://books.google.com/books/content?id=TIJ5EAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
    },
    {
        id: 'G002',
        order: 1,
        bookTitle: 'Infinite Jest',
        author: "David Foster Wallace",
        imgUrl: 'http://upload.wikimedia.org/wikipedia/en/4/4f/Infinite_jest_cover.jpg',
    },
    {
        id: 'G003',
        order: 2,
        bookTitle: 'The sirens of Titan',
        author: "Kurt Vonnegut",
        imgUrl: 'http://pictures.abebooks.com/isbn/9780385333498-us.jpg',
    },
    {
        id: 'G004',
        order: 3,
        bookTitle: 'The Odyssey',
        author: "Homer",
        imgUrl: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Giuseppe_Bottani_-_Athena_revealing_Ithaca_to_Ulysses.jpg/440px-Giuseppe_Bottani_-_Athena_revealing_Ithaca_to_Ulysses.jpg',
    },
    {
        id: 'G001',
        order: 0,
        bookTitle: 'Brave New World',
        author: "Aldous Huxley",
        imgUrl: "http://books.google.com/books/content?id=TIJ5EAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
    },
    {
        id: 'G002',
        order: 1,
        bookTitle: 'Infinite Jest',
        author: "David Foster Wallace",
        imgUrl: 'http://upload.wikimedia.org/wikipedia/en/4/4f/Infinite_jest_cover.jpg',
    },
    {
        id: 'G003',
        order: 2,
        bookTitle: 'The sirens of Titan',
        author: "Kurt Vonnegut",
        imgUrl: 'http://pictures.abebooks.com/isbn/9780385333498-us.jpg',
    },
    {
        id: 'G004',
        order: 3,
        bookTitle: 'The Odyssey',
        author: "Homer",
        imgUrl: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Giuseppe_Bottani_-_Athena_revealing_Ithaca_to_Ulysses.jpg/440px-Giuseppe_Bottani_-_Athena_revealing_Ithaca_to_Ulysses.jpg',
    }
];


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