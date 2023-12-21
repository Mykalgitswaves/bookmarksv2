<template>
    <div class="friend-request">
        <img src="" alt="">
        <div class="friend-request-heading">
            <h3 class="text-slate-800">{{ user.username }}</h3>
            <p class="text-slate-600 text-small">{{ num }} mutual friends </p>
        </div>

        <div class="friend-request-btns">
            <button
                v-for="button in buttons['anonymous']"
                :type="button.type"
                :alt="button.alt"
                :class="button.class"
                @click="button.click"
            >
                <component :is="button.icon" />
            </button>
        </div>
    </div>
</template>
<script setup>
import { friendRequestButtons } from './friendRequestButton';
const buttons = friendRequestButtons;

const props = defineProps({
    num: {
        type: Number,
    },
    user: {
        type: Object,
    }
})

</script>
<style scoped lang="scss">
    .friend-request {
        display: grid;
        grid-template-columns: min-content auto .35fr;
        height: min-content;
        padding: 12px;
        border-radius: 8px; 
        border: 1px solid #f5f5f4;

        img {
            border-radius: 50%;
            background: #d7d7d7;
            width: 50px;
            margin-right: 24px;
        }
    }
    .friend-request-btns {
        display: grid;
        grid-template-columns: repeat(2, 40px);
        margin-right: 12px;
        column-gap: 1em;
        justify-content: flex-end;
    }

    .friend-request-heading {
        overflow-wrap: anywhere;
    }

    .friend-request-accept-btn {
        background-color: #a5b4fc;
        border-radius: 8px;
        color: #fff;
        justify-self: center;
        padding: 12px;
        transition: all 250ms ease;

        &:hover {
            background-color: #818cf8;
        }
    }

.friend-request-reject-btn {
        background-color: #dc2626;
        border-radius: 8px;
        color: #fff;
        justify-self: center;
        padding: 12px;
        transition: all 250ms ease;

        &:hover {
            background-color: #b91c1c;
        }
    }
</style>