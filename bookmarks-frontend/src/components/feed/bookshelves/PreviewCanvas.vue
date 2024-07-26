<template>
    <p class="text-stone-500 text-sm">Viewing reviews for pages:
        <span class="text-indigo-500">
            {{ currentPageRangeStart + '-' + pageRangeEnd }}
        </span>
    </p>
    <div class="range">
        <canvas ref="canvasRef"></canvas>
        <input type="range" :max="props.totalPages" v-model="currentPageRangeStart"/>
    </div>
</template>
<script setup>
import { ref, onMounted, computed, watchEffect }from 'vue';

const props = defineProps({
    /**
     * @type {Object} 
     * @param {Object[int: int]} pageDict – 
     * Containing pages with non zero amounts of update. 
     *  Key === page number: value === update
     * --------------------------------------
     * 
     */
    progressBarData: {
        type: Object,
        required: true,
    },
    /**
     * @param {Array[Object]} updates – 
     * List containing objects - each object contains
     * – created_date
     * – headline
     * – id
     * – page
     */
    previewData: {
        type: Object,
        required: true,
    },
    totalPages: {
        type: Number,
        required: true,
    },
});

const canvasRef = ref(null);

const currentPageRangeStart = ref(0);

const pageRangeEnd = computed(() => 
    (props.progressBarData.defaultPageRange + parseInt(currentPageRangeStart.value))
);

const emit = defineEmits(['modelValue:changed'])

watchEffect(() => {
    currentPageRangeStart.value;
    emit('modelValue:changed', parseInt(currentPageRangeStart.value));
});

onMounted(() => {
    const canvas = canvasRef.value;
    const context = canvas.getContext('2d');
    const { weights } = props.progressBarData;
    
    const width = canvas.width = canvas.offsetWidth;
    const height = canvas.height = canvas.offsetHeight;

    const gradient = context.createLinearGradient(0, 0, width, 0);
    weights.forEach((weight, index, array) => {
        const position = index / (array.length - 1);
        const r = Math.max((weight * 255), 255);
        const color = `rgba(${r}, 20, 56, ${weight})`; // Using black as base color
        gradient.addColorStop(position, color);
    });

    context.fillStyle = gradient;
    context.fillRect(0, 0, width, height);
});

</script>
<style scoped>
.range {
    position: relative;
    width: 100%;
    height: 20px;
}

canvas {
    position: relative;
    margin-top: 15px;
    height: 20px;
    width: 100%;
    border-radius: 4px;
    border: 1px solid var(--stone-400);
    /* background-color: red; */
}

input[type="range"] {
    position: absolute;
    bottom: 0;
    left: 0;
    appearance: none;    
    width: 100%;
    background-color: transparent;
    overflow: clip;
}

/* WebKit browsers (Chrome, Safari) */
input[type="range"]::-webkit-slider-thumb {
    appearance: none;
    width: 20px;
    height: 20px;
    background-color: var(--indigo-500);
    cursor: pointer;
    opacity: .2;
    border-radius: 4px;
}

/* Firefox */
input[type="range"]::-moz-range-thumb {
    width: 20px;
    height: 40px;
    background-color: green;
    cursor: pointer;
}

/* IE and Edge */
input[type="range"]::-ms-thumb {
    width: 20px;
    height: 40px;
    background-color: green;
    cursor: pointer;
}
</style>