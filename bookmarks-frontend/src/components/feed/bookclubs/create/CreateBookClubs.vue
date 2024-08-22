<template>
    <form @submit.prevent="createAndNavigateToBookClub(model)">
        <h1 class="t-3xl font-medium text-slate-800">Create a book club</h1>
        
        <div>
            <label for="bookclub_title" class="title-input">
                <p>Add a title for your bookclub</p>

                <input 
                    id="bookclub_title" 
                    type="text" 
                    v-model="model.bookclub_name" 
                    :maxlength="XSMALL_TEXT_LENGTH"
                />
            </label>

            <label for="bookclub_description" class="summary-update bookclub">
                <p>Add a description for your bookclub</p>

                <textarea id="bookclub_description" 
                    v-model="model.bookclub_description"
                    :maxlength="MEDIUM_TEXT_LENGTH"
                />
            </label>

            <button 
                class="create-bookclub-btn"
                type="submit"
            >
                Create
            </button>

            <transition name="content">
                <div 
                    v-if="isShowingErrorMessage" 
                    class="error-message"
                >
                    <p>{{ error_message }}</p>
                </div>
            </transition>
        </div>
    </form>
</template>
<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router'
import { urls } from '../../../../services/urls';
import { db } from '../../../../services/db';
import { XSMALL_TEXT_LENGTH, MEDIUM_TEXT_LENGTH } from '../../../../services/forms';    

</script>