<template>
    <nav class="min-h-[100vh] w-12 
        bg-indigo-100 shadow-sm flex
        flex-col align-middle py-4 px-2"
    >
        <Comment/>
    </nav>
</template>

<script>
import Comment from '../svg/icon-chat.vue'
// #Todo: for later: Add this once page routing is more cash money.
// <RouterLink to="/review"><p class="hover:text-indigo-300' + (isActive ? 'text-indigo-800 text-sm' : 'text-gray-800')">Add Review</p></RouterLink>
    export default {
        components: {
            Comment    
        },
        data() {
            return {

            }
        },
        methods: {
        
        },
        created() {
            window.addEventListener('scroll', this.scrollEvent)
        },
        unmounted() {
            window.removeEventListener('scroll', this.scrollEvent)
        }
    }
</script>
