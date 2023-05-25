<template>
    <div class="flex flex-row">
    <div 
        v-for="(page, index) in pages" :key="index"
    >
        <button 
            class="w-[3rem] ml-5 px-2 py-2 bg-indigo-600 
            rounded-md text-gray-200 mb-10 
            hover:bg-indigo-800 duration-200"
            @click="getCurrentPage(page)"
        >
            {{ page }}
        </button>
    </div>
</div>
</template>

<script>
    export default {
        props: {
            pages: {
                type: Array,
                required: true,
            }
        },
        methods: {
            getCurrentPage(page) {
                this.$emit('selected-page', page)
                window.dispatchEvent(new CustomEvent('cashmoney', 
                { detail: page }
                ))
            }
        },
        mounted() {
            window.addEventListener('cashmoney', (e) => {
                console.log('cashmoney', e.detail)
            })
        }
    }

</script>