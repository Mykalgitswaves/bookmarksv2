<template>
    <div>
        <p class="text-slate-600 text-2xl font-semibold mb-5">Readers who also loved 
            <span class="text-indigo-600">Book Name</span>
        </p>

        <div class="grid-row-readers">
            <div 
                class="reader" 
                v-for="(user, index) in paginatedUsers"
                :key="index"
            >   
                    <div class="mb-5">
                        <p class="text-slate-700 font-medium">{{ user.username }}</p>
                        <p class="text-slate-500 reviews">{{ user.review_ids.length }} reviews</p>
                    </div>
                    
                    <button 
                        class="bg-indigo-900 px-2 py-2 rounded-sm text-white"
                        type="button"
                        alt="follow user"
                        @click="followUser(index)"
                        >
                        <span v-if="followedAuthors[index]">Unfollow</span><span v-else>Follow</span>
                    </button>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, computed } from 'vue';
import { db } from '../../../services/db'; 
import { users } from '../../../fixtureData/dummyUsers.js';

let followedAuthors = {}
const paginationIndex = ref(0);
// 5 per page
const itemsPerPage = (users.length / 1.5);

const paginatedUsers = computed(() => {
    return users.slice(paginationIndex.value, paginationIndex.value + itemsPerPage)
})

// To be replaced with an actual post function that will trigger a reload of the component instance.
function followUser(index) {
    followedAuthors = followedAuthors[index]
    console.log(followedAuthors)
}

</script>
<style scoped>

.grid-row-readers {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
}

.reader {
    padding: 1rem;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    transition: background 200ms ease-in-out;
    align-items: start;
    background: var(--background-container-gradient);
}

.reader:hover {
    background: var(--hover-container-gradient);
    transition: all 200ms ease-in-out;
}


.reader button {
    width: 100%;
}

</style>