"""
We need a way for multiple clients with write access editing the same bookshelf to keep fresh state and avoid race conditions with reordering, removing, or adding the same books to a bookshelf. A possible solution is to create a rtc connection from a websocket server pinging each client viewing with write access when a change has taken place. A change to a bookshelf consists of the following:
    1) A put request to reorder the books inside of a shelf.
    2) A user adding a book to a collaborative shelf.
    3) A user removing a book that another user is reordering.
    4) A user Posting the same book as another user at the same time.
Each of these conditions could potentially fuck up our app / and at very least, a bookshelf due to users not having up to date state from our server and performing any of the above.

if we can use web sockets to communicate to multiple clients on the same page that a change has taken place and where it has taken place, we can refresh (call endpoints), temporarily disable UI components or potentially ignore multiple requests made at the same time. If we are going to do the last bit, we should consider which requests / users get priority for multiple conditions happening simultaneously. Not sure it makes sense to get that nuanced either.


Since we need something that works for multiple clients on the same bookshelf we can start to think about ways to identify when we'd need to start a web  socket connection. 

when a user lands on the editing page of a bookshelf that can kick start a function for particular pool connection:

import asyncio
import websockets

https://pypi.org/project/websockets/

https://fastapi.tiangolo.com/advanced/websockets/

bookshelf_pool = {} , we'd need a pool of diff users saved onto same dictionary for organizing all the different socket connections going on at once i think? we needa way to subscribe and unsubscribe from bookshelf events when the user leaves.

async def create_shelf_connection(websocket, path, client, bookshelf)
    event = await websocket.recv()
    event = "{bookshelf_id}-{event}".format(bookshelf_id=bookshelf.id, event=event)
    await websocket.send(event)


  On the client side wherever we have a the edit component we'd need something sending us to open a socket connection like so 

  user lands on component for editing a specific bookshelf.

    <script setup>
        import { onMounted } from 'vue';
        import { 
            createNewSocketConnection, unsubscribeFromSocketConnection 
        } from './bookshelfRtc.js';

        const props = defineProps({
            bookshelf: {
                type: Object
            },
        });

        // Use this so that users on different devices logged in at the same time can also know when to refresh / get fresh state.
        const client_id = Client.id

        const { user } = route.params;
        const { bookshelf } = route.params;
    // We'd need to have web sockets for creating a new socket connection?
        onMounted(() => {
            // Establish a connection
            createNewSocketConnection(props.bookshelf, client, user);
        });
        // Unmmount when userleaves component for bookshelf.
        unMounted(() => {
            unsubscribeFromSocketConnection(props.bookshelf);
        });
    </script>
   // bookshelvesRTC.js
    <script>
        // create some type of mapping to handle all the diff cases for sending and recieving events
        export const eventFunctionMapping = {
            'open': {
                function: (data) => (console.log(data.detail))
            },
            'closed': {
                function: (data) => ()
            }
        }

        const BOOKSHELF_EVENT_TYPES = [
            'open',
            'closed
        ]

        // We might need to pass this in user id as well
        export function createNewSocketConnection(bookshelf, client_id){
            const socket = new WebSocket(urls.rtc.bookshelf(bookshelf.id));
            socket.addEventListener('open', function (bookshelf, client_id) { 
                socket.send('connection opened at `${bookshelf}-${client_id}');
            });
        
            // This might not work;
            BOOKSHELF_EVENT_TYPES.forEach((EVENT) => {
                socket.addEventListener(EVENT, () => {
                    eventFunctionMapping[EVENT].function
                });
            });
        }
        
        const contactServer = () => {
            socket.send("Initialize");
        }

        export function unsubscribeFromSocketConnection() {
        
        }
    </script>
    // we'd need somesort of url specifically for establishing websocket connections
    <script>
        urls: {
            rtc: {
                // probably need a new baseUrl alternative that includes websockets.
                bookshelf: (bookshelf_id) `ws://${baseUrl}/api/${bookshelf_id}`
            }
        }
    </script>
"""

