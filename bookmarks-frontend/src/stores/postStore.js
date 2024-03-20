/**
 * Used to carry over information from the post on feed page to the actual post page! 
 */
export const postStore = {
    state: null,
    save: function(props) {
        postStore.state = props;
    }
}