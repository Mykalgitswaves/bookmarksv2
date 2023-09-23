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
    formatReviewData: (questionList, book_id, headline) => {
        questionList = typeof questionList === Proxy ? toRaw(questionList) : questionList
        const data = {}
        data.book_id = book_id;
        data.headline = headline;
        data.questions = Array.from(questionList.map((q) => q.q))
        data.ids = Array.from(questionList.map((q) => q.id))
        data.responses = Array.from(questionList.map((q) => q.response))
        data.spoilers = Array.from(questionList.map((q) => q.is_spoiler))
        return data;
    }
}