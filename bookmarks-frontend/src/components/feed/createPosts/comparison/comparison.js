import { reactive } from 'vue';
import { postData } from "../../../../../postsData";
import { helpersCtrl } from "../../../../services/helpers";

const { clone } = helpersCtrl;
const { posts } = postData

export const questions = clone(posts.comparison);

export const topics = Object.keys(questions);

// Used to as a way to send comparison data over wire to server.
export const comparison = reactive({
    id: 0,
    comparator_a: null,
    comparator_b: null,
    topic: '',
    comparison: '',
    is_spoiler: false,
    comparator_a_headline: '',
    comparator_b_headline: '',
    is_ai_generated: false,
});

export const store = new Map();
