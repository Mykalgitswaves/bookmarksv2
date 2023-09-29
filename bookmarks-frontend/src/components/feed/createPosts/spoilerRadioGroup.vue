<template>
    <KeepAlive>
        <label :for="modelObject.id">
            <span class="mr-5">Spoilers</span>
            <input :id="modelObject.id" type="checkbox" v-model="modelObject.is_spoiler" value="true" @change="emit('is-spoiler-event', modelObject.is_spoiler)">
        </label>
    </KeepAlive>
</template>
<script setup>
import { defineEmits, computed } from 'vue'
const props = defineProps({
    modelObject: Object
})

const modelObject = computed(() => (props.modelObject))
// default it to false.
if(modelObject.value) {
    modelObject.value.is_spoiler = false;
} 

const emit = defineEmits();


</script>