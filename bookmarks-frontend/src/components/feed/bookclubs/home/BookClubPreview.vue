<template>
    <div class="bookclub-preview" 
        :class="{
            'behind': bookclub.pace < 0,
            'on-target': bookclub.pace === 0,
            'ahead': bookclub.pace > 0,
            'finished': bookclub.currently_reading_book?.is_user_finished_reading
        }"
        @click="router.push(navRoutes.toBookClubFeed(user, bookclub.book_club_id))"
    >
        <img
            class="currently-reading-img" 
            :src="bookclub.currently_reading_book?.small_img_url || 'https://placehold.co/400x600?text=Nothing'" 
            alt="" 
        />

        <div class="metadata" v-if="bookclub">
            <div>
                <h3 class="title">
                    {{ bookclub.book_club_name}}
                </h3>
                <p v-if="bookclub.currently_reading_book" class="currently-reading">
                    Currently Reading: <i class="text-indigo-500 block">{{ bookclub.currently_reading_book.title }}</i>
                    <br/>
                    <span v-if="bookclub.currently_reading_book" 
                        class="mt-2 block"
                        :class="{
                            'text-md fancy text-center text-stone-700': bookclub.currently_reading_book.is_user_finished_reading,
                            'text-xs text-stone-500 italic': !bookclub.currently_reading_book.is_user_finished_reading
                        }"
                    >{{ paceOfCurrentUserForClub }}</span>
                </p>

                <p v-else class="currently-reading">Not currently reading anything</p>
            </div>

            <button 
                class="link" 
                @click="router.push(
                    navRoutes.toBookClubFeed(user, bookclub.book_club_id))"
            >
            Go to club
            </button>
        </div>
    </div>
</template>
<script setup>
import { computed } from 'vue';
import { navRoutes } from '../../../../services/urls';
import { useRouter } from 'vue-router'

const router = useRouter();
const props = defineProps({
    bookclub: {
        type: Object,
        required: true,
    },
    user: {
        type: String,
        required: false,
    }
});

const paceOfCurrentUserForClub = computed(() => {
    if (props.bookclub.currently_reading_book.is_user_finished_reading) {
        return '🎉 You finished this book! 🎉'
    }

    let pace = props.bookclub.pace
    if (pace < 0) {
        return `You are ${Math.abs(pace)} chapters behind the club pace`
    } else if (pace === 0) {
        return 'You are on track for the club pace'
    } else {
        return `You are ${pace} chapters ahead of the club pace`
    }
});

</script>
<style scoped>
.bookclub-preview {
    width: 100%;
    border-radius: var(--radius-sm);
    padding-left: 14px;
    padding-bottom: 8px;
    padding-top: 8px;
    display: grid;
    align-content: space-between;
    column-gap: 20px;
    row-gap: 20px;
    background-color: var(--stone-50);
    /* max-width: 1fr; */

    & .title {
        font-size: var(--font-2xl);
        font-family: var(--fancy-script);
        color: var(--stone-700);
    }


    & .currently-reading {
        color: var(--stone-500);
        font-size: var(--font-sm);
    }

    & .currently-reading-img {
        height: 100px;
        border-radius: var(--radius-sm);
    }

    & .link {
        padding-top: 30px;
        color: var(--blue-400);
        font-size: var(--font-sm);
        text-decoration: underline;
    }

    &.ahead {
        border: 1px dotted var(--green-300)
    }

    &.behind {
        border: 1px dotted var(--red-300)
    }

    &.finished {
        border: 1px solid var(--indigo-500);
        background-color: var(--indigo-50);
    }
}

.placeholder {
    background-color: var(--stone-200);
    width: 70px;
    height: 100px;
}

@media screen and (max-width: 768px) {
    .bookclub-preview {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-around;
        align-items: center;
    }
}

</style>