<template>
    <section class="post-section-wrapper" v-if="loaded">
        <div class="explore-header">
            <div class="mb-2">
                <h2 class="fancy text-3xl text-stone-600 mb-2">Explore bookshelves</h2>
                <p class="text-stone-500 text-base">Find new bookshelves! The following is a collection of bookshelves authored by your friends, that you can join!</p>
            </div>

            <div>    
                <RouterLink 
                    :to="navRoutes.toBookshelvesMainPage(userId)" 
                    class="btn btn-tiny btn-nav text-sm ml-auto"
                >
                    back to your shelves
                </RouterLink>
            </div>
        </div>

        <div class="explore-bookshelves" v-if="bookshelves.length">
            <!-- An explore bookshelf is different from a regular one -->
            <div
                v-for="(bookshelf, index) in bookshelves" 
                :key="index"
            >
                <div class="flex space-between">
                    <p class="mb-2 fancy text-stone-400 text-sm">Created by 
                        <RouterLink :to="navRoutes.toUserPage(bookshelf.created_by_username)" class="italic text-indigo-500">
                            {{ bookshelf.created_by_username }}
                        </RouterLink>
                    </p>

                    <p class="ml-2 text-sm text-stone-500">{{ bookshelf.follower_count }} followers, {{ bookshelf.member_count}} members</p>
                </div>

                <!-- The actual button you can navigate to. -->
                <div 
                    class="explore-bookshelf cursor-pointer" 
                    :class="{'followed': followedShelves[bookshelf.id]}"
                    role="button" 
                    @click="router.push(navRoutes.toBookshelfPage(userId, bookshelf.id))"
                >   
                    <div class="img-container">
                        <img v-for="(img, index) in bookshelf.book_img_urls.slice(0,4)" :key="index" :src="img"/>
                    </div>

                    <div>
                        <h4 class="text-stone-600 fancy text-lg">{{ bookshelf.title }}</h4>
                        <p class="text-sm text-stone-500">{{ bookshelf.description }}</p>
                    </div>

                    <span class="italic text-sm text-indigo-500 ml-auto">{{ bookshelf.books_count || 0 }} books</span>
                </div>

                <div class="mt-2 flex gap-2">
                    <button type="button" 
                        class="btn btn-tiny text-sm btn-specter" 
                        :class="{'followed': followedShelves[bookshelf.id]}"
                        @click="followBookshelf(bookshelf)"
                    >
                       <span v-if="!followedShelves[bookshelf.id]">Follow bookshelf</span>
                       <span v-else>followed 🎉</span>
                    </button>
                </div>
            </div>
        </div>

        <div v-else class="mt-10 text-center ">
            <h4 class="fancy text-xl text-stone-500">No shelves!🤖</h4>
            <button 
                type="button" 
                class="mt-2 w-40 mx-auto btn btn-submit text-sm"
                @click="router.push(navRoutes.toBookshelvesCreate(userId))"    
            >
                Create your own now!
            </button>
        </div>
    </section>
</template>
<script setup>
import { navRoutes, urls } from '../../../services/urls';
import { db } from '../../../services/db';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
    bookshelves: {
        type: Array,
        required: false,
    },
    userId: {
        type: String,
        required: true,
    }
}); 

const router = useRouter();
const followedShelves = ref({});
const loaded = ref(false);

// manually create the dictionary based on bookshelves to see what we got!
props.bookshelves.forEach((shelf) => {
    followedShelves.value[shelf.id] = false;
});

loaded.value = true;

/**
 * @async_functions
 */

async function followBookshelf(bookshelf) {
    followedShelves.value[bookshelf.id] = true;
    db.put(
        urls.rtc.followPublicBookshelf(bookshelf.id), 
        null, 
        false, 
        (res) => {
            bookshelf.follower_count += 1;
        }, 
        (err) => {
            followedShelves.value[bookshelf.id] = false;
        }
    );
}
</script>
<style scoped>
.explore-bookshelf {
    border: 1px solid var(--indigo-100);
    border-radius: 8px;
    padding: 10px 14px;
    display: flex;
    column-gap: 10px;
    align-items: center;
    transition: all 250ms ease-in-out;
    background-color: var(--surface-primary);
}

.explore-bookshelf:hover {
    background-color: var(--surface-primary);
    box-shadow: var(--shadow-lg);
}

.explore-bookshelf.followed {
    border-color: var(--indigo-300);
    background-color: var(--indigo-100);
}

@starting-style {
    .explore-bookshelf {
        opacity: 0;
    }
}

.img-container {
    display: grid;
    grid-template-areas:
        "a b"
        "c d"
    ;
    width: 40px;
}

.img-container img {
    width: 20px;
    height: 30px;
}

.explore-header {
    display: grid;
    justify-content: start;
    row-gap: 10px;
    padding: 20px;
    padding-left: 40px;
    background-color: var(--stone-100);
    border-radius: 8px;
    margin-bottom: 20px;
}

.explore-bookshelves {
    max-width: 768px;
    margin-right: auto;
    margin-left: 2vw;
}

.btn.followed {
    border: 1px solid var(--indigo-300);
    background-color: var(--indigo-50);
}
</style>