<template>
    <span class="tooltip" :class="attrs?.color">
        <Transition name="content" tag="span">
            <span v-show="isShowingTip" 
                class="tooltip-message" 
                :class="attrs.alignment"
            >
                <slot name="message" ref=""></slot>
            </span>
        </Transition>
            
        <IconQuestionTip 
            @mouseover="isShowingTip = true" 
            @mouseleave="isShowingTip = false"
        />
    </span>
</template>
<script setup>
import { useAttrs, ref } from 'vue';
import IconQuestionTip from '../svg/icon-question-tip.vue';
const attrs = useAttrs();
const isShowingTip = ref(false);
</script>
<style scoped>
.tooltip {
    display: inline-block;
    position: relative;
    height: auto;
    width: 20px;
    color: var(--stone-700);
}

.tooltip.purple {
    color: var(--indigo-400);
}

.tooltip-message {
    position: absolute;
    width: 280px;
    font-size: var(--font-xs);
}

.tooltip-message.left {
    left: 30px;
    top: -5px;
}
</style>