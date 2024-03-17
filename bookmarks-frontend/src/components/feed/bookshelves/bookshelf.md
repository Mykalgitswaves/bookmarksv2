Legacy code for initial reorder function that haad us trying to maintain state on front end for snappier feel. Rather just let server bookshelf object be the source of truth.

function reorder_books(bookData) {
    isReordering.value = true;

    const { target_id, previous_book_id, next_book_id } = bookData;

    console.log('past destructuring of bookdata', bookData)

    // Find the current, previous, and next books
    const curr = books.value.find(b => b.id === target_id);
    const prev = previous_book_id ? books.value.find(b => b.id === previous_book_id) : null;
    const next = next_book_id ? books.value.find(b => b.id === next_book_id) : null;

    // Early exit if we can't find the current book or both previous and next books
    if (!curr || (!prev && !next)) {
        isReordering.value = false;
        return;
    }

    // Remove current book from the list
    const indexOfCurr = books.value.indexOf(curr);
    books.value.splice(indexOfCurr, 1);

    // Find the index where the current book should be inserted
    // Inserting to the beginning of the list is the default!
    let insertIndex = 0; 
    
    // Common case, sorting to middle of list. (IE not the beginning or end) 
    if (prev && next) {
        // If both previous and next books exist, insert between them
        const indexOfPrev = books.value.indexOf(prev);
        const indexOfNext = books.value.indexOf(next);
        insertIndex = indexOfPrev;
        console.assert(indexOfNext === indexOfPrev + 1);
        // If next book is right after previous book, insert after previous book
        insertIndex = indexOfPrev;
    // Inserting to the end of the list. 
    } else if (prev && !next) {
        // For the last book in the list reorder.
        // If only previous book exists, insert after previous book
        insertIndex = books.value.length;
    }

    // Insert the current book at the determined index
    books.value.splice(insertIndex, 0, curr);
    console.log('made it to the end of reorder_books', books.value);
    // Update the order of each book
    books.value.forEach((b, index) => b.order = index + 1);
    // reordering
    console.log('right before sending ws data to server.')
    // Send data to server
    ws.sendData(bookData);

    isReordering.value = false;
    unsetKey++;
}