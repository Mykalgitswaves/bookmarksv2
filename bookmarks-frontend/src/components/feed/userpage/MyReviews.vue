<template>
    <KeepAlive>
        <TransitionGroup name="content" tag="div" class="mt-10">
            <div v-if="aboutData?.length">
                <div
                    v-for="post in aboutData" :key="post.id" 
                    class="center-cards"
                >
                    <component
                        :is="feedComponentMapping[post?.type]?.component()"
                        v-bind="feedComponentMapping[post?.type]?.props(post)"
                    />
                </div>
            </div>
        </TransitionGroup>
    </KeepAlive>

    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
    import { db } from '../../../services/db';
    import { urls } from '../../../services/urls';
    import { ref, onMounted, watchEffect } from 'vue';
    import { useRoute } from 'vue-router';
    import { feedComponentMapping } from '../feedPostsService';
    
    const aboutData = ref([]);
    const route = useRoute();
    
    const user_id = () => {
        if(route.params.user_profile){
            return route.params.user_profile
        }  else {
            return route.params.user
        }
    }
    onMounted(() => {
        if(!aboutData.value.length){
            db.get(urls.reviews.getReviews(user_id())).then((res) => {
                aboutData.value = res.data;
            })
        }
    })

    watchEffect(() => {
        console.log(aboutData.value)
    })
</script>