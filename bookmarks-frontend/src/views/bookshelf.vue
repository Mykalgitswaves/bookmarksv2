<template>
    <div class="h-screen w-screen grid place-content-center relative">    
        <h1>Your Bookshelf</h1>
        <component :is="homeComponentMap" />
    </div>
</template>

<script>
    export default {
        data() {
            return {

            }
        }
    }
</script>