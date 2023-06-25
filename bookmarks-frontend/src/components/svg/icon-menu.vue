<template>
    <button class="">
        {{ books }}
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="30" fill="currentColor">
            <path 
                fill-rule="evenodd" 
                d="M5.6 0H19a5 5 0 0 1 5 5v22.3c0 1.3-1 2-2 2.4-.9.3-2 .2-3-.5L12.3 24l-6.7 5.2c-1 .7-2.2.8-3.1.5-1-.3-2-1.1-2-2.4V5a5 5 0 0 1 5-5Zm-3 5a3 3 0 0 1 3-3H19a3 3 0 0 1 3 3v22.3s0 .3-.5.5c-.5.1-1 0-1.3-.2l-6.9-5.3h-2l-7 5.3c-.3.2-.8.3-1.2.2-.5-.2-.6-.4-.6-.5V5Z"
                clip-rule="evenodd"
            />
        </svg>
    </button>
</template>

<script>
    export default {
        props: {
            books: {
                type: Number,
            }
        },
    }
</script>