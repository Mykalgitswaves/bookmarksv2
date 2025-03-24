<template>
  <button
    type="button"
    class="flex my-2 text-indigo-600 items-center back-hover"
    :class="defaultInlineMargin"
    @click="() => backFn() || router.back()"
  >
    <IconBack/>
    <slot name="button-text"></slot>

    <span v-if="!slots['button-text']" class="ml-2">Back</span>
  </button>
</template>
<script setup>

import { useSlots } from 'vue';
import { useRouter } from 'vue-router';
import IconBack from '../../svg/icon-back.vue';

const router = useRouter();

const props = defineProps({
  backFn: {
    type: Function,
    required: false,
  },
  marginLeft: {
    type: String,
    required: false,
  }
})

const slots = useSlots();

const defaultInlineMargin = props.marginLeft ? props.marginLeft : 'md:ml-10';
</script>
<style scoped>
.back-hover {
  transition: 250ms ease;
  display: flex;
  padding: 4px 12px;
  border-radius: 4px;
  white-space: nowrap;
  /* border: 1px solid var(--surface-primary); */
  min-width: 100px;
  column-gap: 8px;
  justify-content: center;
}

.back-hover:hover {
  background-color: #e0e7ff;
}

.back-btn:active {
  border-color: #768bf7
}
</style>