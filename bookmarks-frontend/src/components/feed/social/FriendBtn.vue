<template>
    <button
        :type="type"
        :alt="alt"
        :class="classes"
        @click="handleClickAndEmitNewBtnState(payloadData)"
    >
        <span v-if="text">{{ text }}</span>
        <slot name="icon">
        </slot>
    </button>
</template>
<script setup>
import { currentClickPayload } from "./friendRequestButton";

const props = defineProps({
    setElementAttr: {
        type: Function,
        required: false,
    },
    type: {
        type: String,
        required: true,
    },
    alt: {
        type: String,
        required: true,
    },
    classes: {
        type: String,
        required: false,
        default: ''
    },
    text: {
        type: String,
        required: false,
        default: ''
    },
    click: {
        type: Function,
        required: false,
        default: () => null
    },
    payloadData: {
        type: Object,
        required: false
    }
});

const emit = defineEmits(['rel-to-user-changed']);

async function handleClickAndEmitNewBtnState(payloadData) {
    const data = await props.click(...currentClickPayload(payloadData.user, payloadData.user_id));
    emit('rel-to-user-changed', data)
}
</script>