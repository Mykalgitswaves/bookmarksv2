<template>
    <div>
        <input type="number" v-model="form.num_books">
        <input type="number" v-model="form.num_time_period">
        <label for="pace">
            pace
            <select name="pace" id="pace" v-model="form.time_period">
                <option v-for="(option, index) in selectOptions" 
                    :key="index" 
                    :value="option"
                >
                    {{ option }}
                </option>
            </select>
        </label>
    </div>
</template>
<script setup>
import { watch, ref } from 'vue';
import { BookClub } from '../models/models';

const selectOptions = Object.values(BookClub.paceIntervals)

const form = ref({
    num_books: 1,
    num_time_period: 1,
    time_period: '',
    name: '',
});

const emit = defineEmits(['update-form-data'])

watch(form, (newValue) => {
    if (newValue) {
        emit('update-form-data', newValue)
    }
})
</script>