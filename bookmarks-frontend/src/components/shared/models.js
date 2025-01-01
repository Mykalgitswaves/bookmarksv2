const BOOKSHELF_TYPE = 'bookshelf';
const MESSAGE_TYPE = 'bookclub';
const DESTROYED = 'destroyed';

// Always clone this when using methods off the model.
export const Toast = {
    defaultType: BOOKSHELF_TYPE,
    TYPES: {
        MESSAGE_TYPE, 
        BOOKSHELF_TYPE, 
        DESTROYED
    },
}

export const BOOKSHELVES_VISIBLITY_OPTIONS = [
    { label: 'Public', value: 'public' }, 
    { label: 'Private', value: 'private' },
    { label: 'Friends', value: 'friends' },
];