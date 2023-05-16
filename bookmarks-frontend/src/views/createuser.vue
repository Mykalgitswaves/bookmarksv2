<template>
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
        }
    },
    mounted(){
        const state = useStore();
        this.createFormState = computed(() => userFormMapping[state.page])
    }
}

</script>