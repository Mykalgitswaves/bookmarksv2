<template>
    <div class="fixed bottom-0 md:bottom-auto w-screen 
        flex flex-row justify-center align-items-end pb-8 pt-4
        px-14 bg-slate-900 md:justify-start
        space-x-8 opacity-[98%] scroll:opacity-[94%]"
        @scroll="scrollEvent()" ref="navbar"
    >
            <RouterLink to="/review">
                <p class="inline-block hover:text-indigo-200">
                    <Comment class="inline text-indigo-100"/>

                    <span class="text-indigo-100">
                    Add Review
                    </span>
                </p>
            </RouterLink>
            <RouterLink to="/book-club"><p class="text-indigo-100 hover:text-indigo-200 hover:underline">Book Club</p></RouterLink>
            <RouterLink to="/shelf"><p class="text-indigo-100 hover:text-indigo-200 hover:underline">View Shelf</p></RouterLink>   
    </div>
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
            scrollEvent() {
               let navbar = this.$refs.navbar;
               setInterval(decreaseOpacity, 50);
                function decreaseOpacity() {
                   let opacity = .98
                   navbar.style.opacity = opacity
                   navbar.style.opacity -= .05
                }
                        
                   }
        },
        created() {
            window.addEventListener('scroll', this.scrollEvent)
        },
        unmounted() {
            window.removeEventListener('scroll', this.scrollEvent)
        }
    }
</script>
