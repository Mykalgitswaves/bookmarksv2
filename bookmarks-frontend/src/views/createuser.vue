<template>
    <div class="container w-screen
        flex flex-row py-3 mx-auto
        justify-start"
    >
        <p class="text-indigo-700 underline underline-offset-2 px-2"
            @click="getPrevPage">
            Prev
        </p>
        {{ page }}
        <p class="text-indigo-700 underline underline-offset-2 px-2"
            @click="getNextPage">
            Next
        </p>
    </div>
    <div class="h-screen w-screen grid place-content-center relative">
        <component :is="createFormState" />
    </div>
</template>

<script>
// Import create user form components
import CreateUserFormBooks from '@/components/create/createuserformbooks.vue';
import CreateUserFormGenre from '@/components/create/createusergenre.vue'
import CreateUserFormFinal from '@/components/create/createuserfinal.vue'

import { computed } from 'vue';
import { useStore } from '../stores/counter.js';

// Map to components keep the view the same
const userFormMapping = {
        1: CreateUserFormBooks,
        2: CreateUserFormGenre,
        3: CreateUserFormFinal
}

export default {
    data() {
        return {
            createFormState: null,
            state: null
        }
    },
    methods: {
        getNextPage() {
            const state = useStore();
            state.getNextPage();
        },
        getPrevPage() {
            const state = useStore();
            state.getPrevPage();
        }
    },
    computed: {
        page() {
            const state = useStore();;
            return state.page
        }
    },
    mounted(){
        const state = useStore();
        this.state = state;
        this.createFormState = computed(() => userFormMapping[state.page]);
    }
}

</script>