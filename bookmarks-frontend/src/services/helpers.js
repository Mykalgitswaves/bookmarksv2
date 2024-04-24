import { toRaw } from 'vue'
import JSConfetti from 'js-confetti'
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
    // Takes a list of strings and concatenates them with commas depending on the index.
    commanatoredString: (list) => {
        let error = () => { throw new Error("commanatoredString needs a list with values! No empty ones brah");}
        
        if (!list || !list.length) {
            return null;
        }
        
        let result = '';
        
        list.forEach((i, name) => {
            result += `${name + commanator(i, list)}`
        });

        return result
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
        data.quote = update.quote;

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

// Returns a function, that, when invoked, will only be triggered at most once
// during a given window of time. Normally, the throttled function will run
// as much as it can, without ever going more than once per `wait` duration;
// but if you'd like to disable the execution on the leading edge, pass
// `{leading: false}`. To disable execution on the trailing edge, ditto.
export function explicitThrottle(func, wait, options) {
    var context, args, result;
    var timeout = null;
    var previous = 0;
    if (!options) options = {};
    var later = function() {
      previous = options.leading === false ? 0 : Date.now();
      timeout = null;
      result = func.apply(context, args);
      if (!timeout) context = args = null;
    };
    return function() {
      var now = Date.now();
      if (!previous && options.leading === false) previous = now;
      var remaining = wait - (now - previous);
      context = this;
      args = arguments;
      if (remaining <= 0 || remaining > wait) {
        if (timeout) {
          clearTimeout(timeout);
          timeout = null;
        }
        previous = now;
        result = func.apply(context, args);
        if (!timeout) context = args = null;
      } else if (!timeout && options.trailing !== false) {
        timeout = setTimeout(later, remaining);
      }
      return result;
    };
  };

export function throttle (callback, limit) {
    var waiting = false;                      // Initially, we're not waiting
    return function () {                      // We return a throttled function
        if (!waiting) {                       // If we're not waiting
            callback.apply(this, arguments);  // Execute users function
            waiting = true;                   // Prevent future invocations
            setTimeout(function () {          // After a period of time
                waiting = false;              // And allow future invocations
            }, limit);
        }
    }
}

/** 
* @param {reactiveObject} - a vue reactive object.
* @param {key} - a string, should be 'value'.
* @param {value} - any, the actual value you want to set
*/
export const setReactiveProperty = (reactiveObject, key, value) => {
    let error = () => { throw new Error("A object, key and value is required"); }

    return (!reactiveObject || !key || !value) ? 
        error() :
        reactiveObject[key] = value
}

function isNumber(number){
    return Number.isFinite(parseFloat(number))
}

export function isEven(number) {
    if(isNumber(number)){
        return number % 2 == 0;
    } else {
        console.error('please provide a valid number', number, 'is not valid');
    }
}

export function isOdd(number) {
    if(isNumber(number)){
        return Math.abs(number % 2) == 1
    } else {
        console.error('please provide a valid number', number, 'is not valid');
    }
}

export function last(list){
    return list[list.length - 1]
}

export async function createConfetti(options){
    const jsConfetti = new JSConfetti()
    await jsConfetti.addConfetti(options||{})
    jsConfetti.clearCanvas()
}

export const truncateText = (originalString, truncatedLength) => {
    if (originalString.length > truncatedLength) {
        return originalString.slice(0, truncatedLength) + '...';
    }
    return originalString;
}