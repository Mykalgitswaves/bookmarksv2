<template>
    <div class="">
        <input class="" type="text">
        <button class="send-comment-btn" type="button" @click="">
            <IconSend />
        </button>

        <div v-if="!props.comments.length">
            <p></p>
        </div>
    </div>
</template>
<script setup>
import IconSend from '../../svg/icon-send.vue';
const props = defineProps({
    comments: {
        type: Array,
        required: false,
    }
})
</script>
<style scoped>
.send-comment-btn {
    padding: 8px;
    border-radius: 50%;
    border: 1px solid #4b5563;
    color: #4b5563;
    display: grid;
}

</style>