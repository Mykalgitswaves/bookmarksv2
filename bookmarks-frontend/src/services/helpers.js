import { toRaw } from 'vue'

// Helper functions used throughout our app!
export const helpersCtrl = {
    // Handles commas
    commanator: (index, arrayLength) => {
        let curr = index + 1
        if ((curr >= arrayLength)) {
            return '';
        } else {
            return ', '
        }
    },
    getCookieByParam: (cookieName) => {
        const cookiesArray = document.cookie.split('; ');
        //iterate through cookieArray
        for (let i = 0; i < cookiesArray.length; i++) {
            const cookie = cookiesArray[i];
            const [key, value] = cookie.split('=');

            const trimmedKey = key.trim();

            if(trimmedKey === cookieName[0]) {
                return decodeURIComponent(value);
            }
        }

        // Return null if param is not found;
        return null;
    },
    /**
    * Function for assembling data into a dictionary that our db can use to create reviews
    * @param {{questionList: Array}} details - contains question dictionaries that hold q.id, q.q, q.response, q.isSpoiler 
    * @param {{bookId: Number}} details - contains id for book review
    * @param {{headline: String}} details - Headline for book review 
    */
    formatReviewData: (questionList, book, headline) => {
        questionList = typeof questionList === Proxy ? toRaw(questionList) : questionList
        const data = {};
        data.book_id = book.id;
        data.title = book.title;
        data.small_img_url = book.small_img_url;
        data.headline = headline;
        data.questions = Array.from(questionList.map((q) => q.q))
        data.ids = Array.from(questionList.map((q) => q.id))
        data.responses = Array.from(questionList.map((q) => q.response))
        data.spoilers = Array.from(questionList.map((q) => q.is_spoiler))
        
        return data;
    },
    formatUpdateData: (update) => {
        const data = {};
        
        data.book_id = update.book_id;
        data.title = update.book_title;
        data.small_img_url = update.small_img_url;
        data.page = update.page;
        data.headline = update.headline;
        data.response = update.response;
        data.is_spoiler = update.is_spoiler;

        return data;
    },
    /**
    * Function for cloning objects
    * @param {{obj}} obj - creates clone of object 
    * @returns {{obj}} cloned obj
    */
    clone(obj) {
        const clone = JSON.parse(JSON.stringify(obj));
        console.log(clone)
        return clone
    },
    /**
    * Function for saving books to refs
    * @param {{book_id}} string_number - either a string or a number. 
    * @returns {{void}} void
    */
    bookHandler(book_id, ref) {
        ref.value = book_id
    },
  
    // Returns a function, that, as long as it continues to be invoked, will not
    // be triggered. The function will be called after it stops being called for
    // N milliseconds. If `immediate` is passed, trigger the function on the
    // leading edge, instead of the trailing.
    debounce(func, wait, immediate) {
        var timeout;
        return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
        };
    },
}

export function emit(element, eventName, eventData) {
    const event = new CustomEvent(eventName, { detail: eventData });
    element.dispatchEvent(event);
}
