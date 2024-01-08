import createReviewPost from './createPosts/createReviewPost.vue';
import createUpdatePost from './createPosts/createUpdatePost.vue';
import createComparisonPost from './createPosts/createComparisonPost.vue';
import { urls } from '../../services/urls';
import { router } from '../../router/index';
// we want there to be an additonal create step in our component. So that if you decide to create something, you go to a create Post Page which then directs you to these other pages. Instead of having posting happen on the work feed. THat way we can also pull when we redirect you showing you your most recent post. 
export function navigate(basePath, option){
    if(option){
        return router.push(`${basePath}/${option}`);
    }
    
    return router.push(basePath);
}

export const componentMapping = {
    "review": createReviewPost,
    "update": createUpdatePost,
    "comparison": createComparisonPost,
}

export const urlsMapping = {
    "review": urls.reviews.review,
    "update": urls.reviews.update,
    "comparison": urls.reviews.comparison,
  }