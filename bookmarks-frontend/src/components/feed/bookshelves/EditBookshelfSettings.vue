<template>
    <section class="settings-section mt-10">
            <div class="settings-info-form">
                <FormInputCluster 
                    input-id="bookshelfTitle" 
                    name="Title" 
                    type="text"    
                    :value="data.shelfTitle"
                    @new-value-saved="($event) => updateFieldName($event, 'bookshelfTitle')"
                />

                <p class="text-sm text-slate-600">Description</p>
                <textarea 
                    name="description" id="" cols="30" rows="3"
                    placeholder=""
                    :disabled="isEditing"
                    v-model="data.shelfDescription">
                </textarea>
                <button 
                    type="button"
                    class="save-btn mt-5"
                    @click="updateFieldName(userData.bio, 'bookshelfDescription')"
                >
                    save
                </button>
            </div>
    </section>    
    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import FormInputCluster from '../settings/FormInputCluster.vue';
import { reactive } from 'vue';

const data = reactive({
    loaded: false,
    shelfTitle: 'Untitled',
    shelfDescription: 'Add a description',
    // TODO double check that designs dont have any other shit in them.
});

const urlsMapping = {
    // TODO make endpoints for bookshelf pages.
    // "username": urls.user.updateUsername,
    // "email": urls.user.updateEmail,
    // "bio": urls.user.updateBio
}

function updateFieldName(newDataToSave, keyForMapping) {
    // TODO Make this into an external forms.js service function accepting urls mapping as an option.
    // Need this to say whether or not email save is disabled
    data[keyForMapping] = newDataToSave;
    db.put(urlsMapping[keyForMapping](route.params.user), newDataToSave, true).then((res) => {
        data[keyForMapping] = res.data;
    });
}
</script>