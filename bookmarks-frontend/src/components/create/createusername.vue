<template>
    <form 
        class="grid grid-cols-1 w-100 h-80 gap-2 place-content-center max-w-[600px]" 
    >
        <label class="text-3xl font-medium text-gray-700" for="fullname">What name do you go by?</label>
        <p class="mb-5 font-medium text-gray-500">This is what others will know you as</p>
        <input
            class="py-2 px-4 rounded-md border-2 border-indigo-200"
            v-model="fullname" 
            name="fullname"
            type="text"
            placeholder="What do you go by"
        >
        <button
            class="mt-5 px-30 py-3 bg-indigo-600 rounded-md text-indigo-100"
            alt="submit button" 
            type="button"
            @click="submitNameAndNavigate()"
        >
            Continue
        </button>
    </form>    
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { urls } from '../../services/urls';
import { useStore } from '../../stores/page';
import { helpersCtrl } from '../../services/helpers';

const store = ref(null)
const fullname = ref('');

async function submitNameAndNavigate() {
    const accessTokenFromCookies = helpersCtrl.getCookieByParam(['token'])
    console.log(accessTokenFromCookies)
    try {
    const response = await fetch(urls.setup.name, {
        method: 'PUT',
        headers: {
            Accept: 'application/json',
            Authorization: `Bearer ${accessTokenFromCookies}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(fullname.value)
    });
    const data = response.json()
    return data
    } catch(err) {
        console.error(err)
    }
}

onMounted(() => {
    store.value = useStore();
})

</script>