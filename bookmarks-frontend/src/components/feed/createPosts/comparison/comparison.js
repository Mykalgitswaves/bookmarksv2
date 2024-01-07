import { postData } from "../../../../../postsData";
import { helpersCtrl } from "../../../../services/helpers";

const { clone } = helpersCtrl;
const { posts } = postData

export const questions = clone(posts.comparison);

export const topics = questions.map((q) => q.topic);

// Used to as a way to send comparison data over wire to server.
export class Comparison {
    static count = 0;

    constructor() {
        this.id = ++Comparison.count
        this.book_ids = [];
        this.book_small_imgs = []
        this.comparator_ids = []
        this.comparator_a_title = null
        this.comparator_b_title = null
        this.topic =  ''
        this.q = ''
        this.comparison = ''
        this.is_spoiler = false
        this.comparator_a_headline = ''
        this.comparator_b_headline =  ''
        this.is_ai_generated = false
        this.is_add_irony = false
    };
};

/**
* @param { store } array from pinia, send this your questions
* @param { headlineArray } list from createComparisonQuestion Component, contains headlines
* @returns { postData } dictionary returns dictionary of formatted Post data
*/
export const formatQuestionStoreForPost = (store, headlineArray) => {
    const postData = {}

    postData.book_ids = store[0].book_ids;
    postData.book_titles = [store[0].comparator_a_title, store[0].comparator_b_title]
    postData.comparator_ids = store.map((q) => q.comparator_id)
    postData.book_small_imgs = store[0].small_img_url
    postData.comparator_topics = store.map((q) => q.topic)
    postData.responses = store.map((q) => q.comparison)
    postData.book_specific_headlines = headlineArray;

    return postData
}