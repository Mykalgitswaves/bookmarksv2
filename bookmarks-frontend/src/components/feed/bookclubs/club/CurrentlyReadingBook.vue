<template>
    <div class="ml-auto mr-auto">
        <p class="text-stone-600 italic mb-2" v-if="book">
            <span v-if="!isUserFinishedReading">Currently reading</span>
            <span v-else>Finished reading</span>
        </p>

        <div v-if="book" class="currently-reading-book">
            <img :src="book.small_img_url" alt="" class="currently-reading-img">

            <div class="book-metadata">
                <h3 class="fancy text-xl text-stone-800">{{ book.title }}</h3>

                <p v-if="book?.author_names?.length" class="text-sm text-stone-600">
                    {{ helpersCtrl.commanatoredString(book.author_names) }}
                </p>
            </div>

            <!-- If either the club or the user is finished reading then load this. -->
            <span class="finished-reading-blurb" v-if="currentStatusForClub.clubFinishedWithCurrentBook || currentStatusForClub.userFinishedWithCurrentBook">
                {{ currentStatusForClub.clubFinishedWithCurrentBook ? 'The club has finished reading' : 'You\'ve finished reading' }}

                <IconCrown />
            </span>
        </div>
        
        <div v-else class="currently-reading-book none">
            <h3 class="text-stone-600 fancy text-center">
                This club isn't currently reading anything, 
            </h3>

            <button role="navigation" 
                type="button" 
                class="btn btn-ghost btn-wide btn-tiny mt-5"
                @click="$emit('currently-reading-settings')"
            >
                set one now!
            </button>
        </div>
    </div>
</template>
<script setup>
import { computed, defineAsyncComponent } from 'vue';
import {useRoute} from 'vue-router';
import { helpersCtrl } from '../../../../services/helpers';
import { useCurrentUserStore } from '@/stores/currentUser';

const IconCrown = defineAsyncComponent(() => import('@/components/svg/icon-crown.vue'));

defineProps({
    book: {
        type: Object,
    },
    isUserFinishedReading: {
        type: Boolean,
        required: false,
    }
});

const store = useCurrentUserStore();
const { user } = store;

const route = useRoute();
const { bookclub } = route.params;
// Computed function for when this changes.
const currentStatusForClub = computed(() => {
    const statusForClub = user.clubs[bookclub];

    if (!statusForClub) {
        console.warn('weird state mismanaged here');
        return false;
    }

    return statusForClub;
});

</script>
<style scoped>
.currently-reading-book {
    display: flex;
    flex-wrap: wrap;
    column-gap: 20px;
    border: 1px solid var(--stone-200);
    border-radius: 4px;
    padding: 8px;
    position: relative;

    & .currently-reading-img {
        height: 80px;
        border-radius: 8px;
    }

    &.none {
        display: block;
    }
}

.finished-reading-blurb {
    position: absolute;
    bottom: 5px;
    right: 10px;
    display: flex;
    align-items: end;
    gap: 4px;
    font-size: var(--font-sm);
    color: var(--stone-400);
    font-family: var(--fancy-script);
}
</style>   