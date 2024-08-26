<template>
    <form @submit.prevent="createAndNavigateToBookClub(form)" class="mt-10">
        <h1 class="t-3xl font-medium text-slate-800 mb-5 fancy">Create a book club</h1>
        
        <div>
            <label for="bookclub_title" class="title-input">
                <p class="font-medium">Add a title for your bookclub
                    <span class="text-red-500">*</span>
                </p>

                <input 
                    id="bookclub_title" 
                    type="text" 
                    v-model="form.name" 
                    :maxlength="XSMALL_TEXT_LENGTH"
                />
            </label>
            
            <label for="bookclub_description" 
                class="summary-update bookclub display-block mt-10"
            >
                <p class="pb-5 font-medium">Add a description for your bookclub</p>

                <textarea id="bookclub_description" 
                    v-model="form.description"
                    :maxlength="MEDIUM_TEXT_LENGTH"
                />
            </label>

            <SetBookClubPacing @set-rating="
                (pacing) => setPacingAndIncrementStep(pacing)" 
            />

            <CreateCustomPacingForm 
                v-show="isShowingCustomPaceForm" 
                @update-form-data="(customPaceData) => form.book_club_pace = customPaceData"
            />

            <button 
                class="btn btn-submit btn-wide mt-10"
                :class="{'disabled': !isValid}"
                type="submit"
                :disabled="submitting || !isValid"
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
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router'
import { urls } from '../../../../services/urls';
import { db } from '../../../../services/db';
import { XSMALL_TEXT_LENGTH, MEDIUM_TEXT_LENGTH } from '../../../../services/forms';    
import { BookClub } from './../models/models.js';
import SetBookClubPacing from './SetBookClubPacing.vue';
import CreateCustomPacingForm from './CreateCustomPacingForm.vue';


/**
 * ----------------------------------------------------------------------------
 * @Constants
 * ----------------------------------------------------------------------------
*/

const form = ref({
    name: '',
    description: '',
    book_club_pace: {
        num_books: 1,
        num_time_period: 1,
        time_period: BookClub.paceIntervals.MONTH,
        name: BookClub.paceNames.CASUAL,
    },
});

const isValid = computed(() => {
    if (form.value) {
        // check to make sure you have a name and every prop inside book club pace is not undefined nor null.
        if (form.value.name.length && Object.values(form.value.book_club_pace).every((value) => (value !== undefined || value !== null))) {
            return true;
        }
    }

    return false;
});

// For creating bespoke paces. 
const isShowingCustomPaceForm = ref(false);
const errorMessage = ref('');
const submitting = ref(false);

const route = useRoute();
const router = useRouter();
const { user } = route.params;


/**
 * ----------------------------------------------------------------------------
 * @endOFConstants
 * ----------------------------------------------------------------------------
 */


/**
 * ----------------------------------------------------------------------------
 * @functions
 * ----------------------------------------------------------------------------
 */

async function createAndNavigateToBookClub() {
    form.value.user_id = user;
    submitting.value = true;
    
    await db.post(urls.bookclubs.create(), form.value, null, (res) => {
        submitting.value = false;

        let id = res.book_club_id;
        
        if (user && id) {
            router.push(navRoutes.toBookclub(user, res.book_club_id))
        }
    }, (error) => {
        errorMessage.value = error.detail; 
        submitting.value = false;
    });
}

/**
 * 
 * @function setPacingAndIncrementStep
 * @param {int} pacing
 * @returns void
 * @description used to either show the custom pacing form or load a preset into formdata 
 */

function setPacingAndIncrementStep(pacing) {
    // if pacing is not constant
    if (pacing !== 4) {
        // Make sure you are not coming from a custom preset
        isShowingCustomPaceForm.value = false;
        form.value.book_club_pace = BookClub.pacePresets[pacing];
        return
    }
    else {
        isShowingCustomPaceForm.value = true;
    }
}
/**
 * ----------------------------------------------------------------------------
 * @endOfFunctions
 * ----------------------------------------------------------------------------
 */
</script>