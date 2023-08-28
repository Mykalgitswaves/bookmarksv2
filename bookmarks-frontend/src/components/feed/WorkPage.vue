<template>
    <section class="works-page-wrapper-margin">
    <TransitionGroup name="work-page">
            <p class="text-xl font-semibold lh-fix"><button type="button" v-if="loaded">works page</button><span v-if="!loaded">Good things come to those who wait...</span></p>
            <button type="button" @click="backToFeed">Back</button>
            <div :class="'works-wrapper shadow-lg mt-5 ' + activeWork">
                <div class="">
                    <img :src="image" :alt="title + 'image'" v-if="loaded">

                    <div class="placeholder" v-if="!loaded"></div> 

                    <p class="text-xl font-semibold mb-5">
                        <span v-if="loaded">{{ title }}</span>
                        <span>{{ fallbackTitle }}</span>
                    </p>

                    <p>
                       <span v-if="loaded">{{ description }}</span>
                       <span v-if="!loaded">{{ fallbackDescription }}</span>
                    </p>
                </div>

                <div class="mt-5 container flex justify-between">
                    <button 
                        type="button"
                        class="text-indigo-500 font-medium cursor-pointer"
                        @click="isActiveWork = !isActiveWork"
                    >
                        Add to bookshelf
                    </button>
                    <button type="button"
                        class="text-indigo-500 font-medium cursor-pointer"
                    >
                        Show Reviews
                    </button>
                </div>
            </div>

            <p class="text-xl font-semibold text-slate-700 my-5">Reviews of this work</p>

            <SimilarBooks/>
    </TransitionGroup>
    </section>
</template>

<script setup>
import SimilarBooks from '@/components/feed/SimilarBooks.vue';
import {ref, computed, onMounted } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router'

const router = useRouter();
const route = useRoute();
const book_id = route.params.work;
const data = ref(null); 
const isActiveWork = ref(false);

function backToFeed() {
    return router.push(`/feed/${route.params.user}/review/all`)
};

async function getWorkPage() {
    
    console.log(route.params);
    await fetch(`http://127.0.0.1:8000/api/books/${book_id}`)
    .then((data) => data.json())
    .then((res) => {
        data.value = res.data
    });
}

getWorkPage()

const description = computed(() => (data.value.description.toLowerCase()));
const title = computed(() => (data.value.title));
const image = computed(() => (data.value.img_url));
const loaded = computed(() => data.value === null ? false : true);
const activeWork = computed(() => isActiveWork.value ? 'bg-indigo-200': 'bg-slate-50')

const fallbackTitle = 'Patience is a virtue';

onMounted(() => {
    console.log(router.currentRoute.value.path)
})
</script>

<style scoped>

    
    .works-page-wrapper-margin {
        margin-left: 1.5rem;
        margin-right: 1.5rem;
    }
    .works-wrapper {
        min-height: 250px;
        border-radius: .3rem;
        padding: 1rem;
        max-width: 1000px;
        width: 60vw;
        min-width: 300px;
    }

    .placeholder {
        height: 146px;
        width: 98px;
        background-color: #1e1e1e;
        border-radius: .25rem;
    }

    /* .work-page-enter-active,
    .work-page-leave-active {
        transform: 0 45px;
        transition: opacity 0.5s ease-out;
    }

    .work-page-enter-from,
    .work-page-leave-to {
        opacity: 0;
    } */
</style>