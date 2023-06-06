<template>
    <div class="px-4 pt-5">
        <ul class="grid grid-cols-1 gap-5">
            <li 
                v-for="author in authors" :key="author.id"
                @click="data.push(author.full_name); isToggled[author.id] = true; sendDataToParent();"
                :class="'flex flex-row gap-5 py-4 px-4 place-content-start bg-gray-100 rounded-md my-1 hover:bg-gray-200 max-w-[700px]'
                + (isToggled[author.id] === true ? 'border-solid border-indigo-200 border-2 bg-indigo-50' : '')"
            >
                <div class="flex flex-col justify-center">
                    <p class="text-xl font-semibold text-gray-800">{{ author.full_name }}</p>
                </div>
            </li>
        </ul>
    </div>
</template>

<script>
    export default {
        props: {
            authors: {
                type: Array,
                required: true
            }
        },
        data() {
            return {
                isToggled: {},
                data: []
            }
        },
        methods: {
            sendDataToParent(){
                this.$emit('author-data-updated', {authors: this.data})
            }
        }
    }
</script>