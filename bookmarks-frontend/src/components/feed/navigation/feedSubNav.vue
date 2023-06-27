<template>
    <div class="subnav-layout-wrapper">
        <img class="profile-image" :src="props.profilePicture" alt="">
        <div>
            <p class="text-slate-800 font-semibold text-xl">
                Aaron Wordnerd III
            </p>
            <p>Fiction, Poetry, contemporary...</p>
        </div>
    </div>    
</template>

<script setup>
    import { defineProps } from "vue"

    const props = defineProps({
        profilePicture: String
    })
</script>

<style>
    .profile-image {
        height: 7rem;
        border-radius: 50%;
        opacity: 1;
        cursor: pointer;
    }

    .subnav-layout-wrapper {
        display: flex;
        flex-direction: row;
        align-items: center;
        padding-top: 1rem;
        padding-bottom: 1rem;
        margin-left: 5vw;
        gap: .5rem;
        justify-content: start;
    }
</style>