"""
We need a way for multiple clients with write access editing the same bookshelf to keep fresh state and avoid race conditions with reordering, removing, or adding the same books. A possible solution is to create a rtc connection from a new websocket server pinging each client viewing with write access when a change has taken place. A change to a bookshelf consists of the following:  
    1) A put request to reorder the books inside of a shelf.
    2) A user adding a book to a collaborative shelf.
    3) A user removing a book that another user is reordering.
    4) A user Posting the same book as another user at the same time.
Each of these conditions could potentially fuck up our app / and at very least, a bookshelf due to users not having up to date state from our server and performing any of the above.

if we can use web sockets to communicate to multiple clients on the same page that a change has taken place and where it has taken place, we can refresh (call endpoints), temporarily disable UI components or potentially ignore requests made at the same time as another client. If we are going to do the last bit, we should consider which users get priority for two conditions happening simultaneously. Not sure it makes sense to get that nuanced either.

"""