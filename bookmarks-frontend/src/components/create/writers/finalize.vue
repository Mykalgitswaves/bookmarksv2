<template>
    <div class="container grid place-content-center">
        <RouterLink to="/home">
            <button 
                class="mt-5 px-36 py-4 bg-indigo-600 rounded-sm text-indigo-100"
                type="button"
            >Continue
            </button>
        </RouterLink>
    </div>
</template>

<script>
    import { useStore } from '../../../stores/page.js';

export default {
    methods: {
        navigate() {
            this.state.getNextPage()
        },
       
    },
    mounted() {
        this.state = useStore()     
    }
}
</script>
