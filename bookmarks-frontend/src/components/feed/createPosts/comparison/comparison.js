import { postData } from "../../../../../postsData";
import { helpersCtrl } from "../../../../services/helpers";

const { clone } = helpersCtrl;
const { posts } = postData

export const questions = clone(posts.comparison);

export const topics = Object.keys(questions);