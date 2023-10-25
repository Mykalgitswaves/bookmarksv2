<template>
    <div>
                YOo world

    </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router';
import { urls } from '../../services/urls'; 

const postData = ref(null);
const route = useRoute();
const { user, comparison } = route.params;

async () => {
    await fetch(urls.reviews.getAllComparisonComments(user, comparison)).then((res) => {
        postData.value = res.data;
    })
}
</script>