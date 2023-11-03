<template>
    <div class="my-3 comment">
        <p class="">{{ props.comment.text }}</p>
        <div>
            <button 
                class=""
                type="button"
            >
                <IconComment/>
            </button>

            <button 
                class=""
                type="button"
            >
                <span class="flex ml-5"><IconLike/>{{ props.comment.likes }}</span>
            </button>
        </div>
    </div>
</template>
<script setup>
import IconLike from '../../svg/icon-like.vue';
import IconComment from '../../svg/icon-comment.vue';
const props = defineProps({
    comment: {
        type: Object,
        required: true,
    }
});
</script>
<style scoped>
.comment {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 2.25rem;
    border-radius: 8px;
    border: solid 1px rgb(238 242 255);
}
</style>