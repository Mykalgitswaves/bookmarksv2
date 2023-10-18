import { reactive } from 'vue';
import { postData } from "../../../../../postsData";
import { helpersCtrl } from "../../../../services/helpers";

const { clone } = helpersCtrl;
const { posts } = postData

export const questions = clone(posts.comparison);

export const topics = Object.keys(questions);

// Used to as a way to send comparison data over wire to server.
export class Comparison {

    static count = 0;

    constructor() {
        this.id = ++Comparison.count
        this.comparator_ids = []
        this.book_small_imgs = []
        this.comparator_a_title = null
        this.comparator_b_title = null
        this.topic =  ''
        this.q = ''
        this.comparison = ''
        this.is_spoiler = false
        this.comparator_a_headline = ''
        this.comparator_b_headline =  ''
        this.is_ai_generated = false
    }
};
        // post_id='',
        // book=book_ids,
        // user_username=current_user.username,
        // headline=response['headline'],
        // comparators=response['comparators'],
        // comparator_ids=response['comparator_ids'],
        // responses=response['responses'],
        // book_specific_responses=response['book_specific_responses'],
        // book_title=response['title'],
        // book_small_img=response['small_img_url'])