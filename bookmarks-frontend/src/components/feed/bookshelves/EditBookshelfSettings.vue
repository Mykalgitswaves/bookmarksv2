<template>
    <section class="settings-section mt-10">
            <RouterLink class="btn btn-tiny text-sm btn-nav" 
                :to="navRoutes.toBookshelfPage(user, bookshelf)"
            >
                Back to shelf
            </RouterLink>

            <div class="settings-info-form">
                <FormInputCluster 
                    input-id="bookshelfTitle" 
                    name="Title" 
                    type="text"    
                    :value="data.title"
                    @new-value-set="($event) => updateFieldName($event, 'title')"
                    @new-value-saved="saveFieldName('title')"
                />

                <FormInputCluster 
                    :is-text-area="true" 
                    name="Description" 
                    type="text"    
                    :value="data.description"
                    @new-value-set="($event) => updateFieldName($event, 'description')"
                    @new-value-saved="saveFieldName('description')"
                />

                <!-- <div>
                    <textarea 
                        name="description" id="" cols="30" rows="3"
                        placeholder=""
                        :disabled="isEditing"
                        v-model="data.shelfDescription"
                    ></textarea>

                    <button 
                        type="button"
                        class="save-btn mt-5"
                        @click="updateFieldName(userData.bio, 'description')"
                    >
                        save
                    </button>
                </div> -->
            </div>

            <div class="settings-info-form danger-zone">
                <h3 class="danger-zone-text text-center">Danger zone</h3>
                
                <RadioGroup 
                    id="visibility-options"
                    :default="data.visibility"
                    :options="BOOKSHELVES_VISIBLITY_OPTIONS" 
                    @updated:modelValue="(value) => { 
                        data.visibility = value
                    }"
                    >
                    <template #heading>
                        Club visibility 
                    </template>
                </RadioGroup>


                <button type="button" class="btn btn-delete" @click="">
                    Delete bookshelf
                </button>
            </div>
    </section>    
    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import { onMounted, reactive } from 'vue';
import { useRoute } from 'vue-router';
import FormInputCluster from '../settings/FormInputCluster.vue';
import { db } from '../../../services/db';
import { urls, navRoutes } from '../../../services/urls';
import RadioGroup from '../partials/RadioGroup.vue';
import { BOOKSHELVES_VISIBLITY_OPTIONS } from '@/components/shared/models.js';

const route = useRoute();
const { user, bookshelf } = route.params;

// TODO: Fix this shit.
const data = reactive({
    loaded: false,
    title: 'Untitled',
    description: 'Add a description',
    visibility: 'private',
    // TODO double check that designs dont have any other shit in them.
});

const urlsMapping = {
    // TODO make endpoints for bookshelf pages.
    "title": urls.rtc.setShelfTitle(bookshelf),
    "description": urls.rtc.setShelfDescription(bookshelf),
    "visibility": urls.rtc.setShelfVisibility(bookshelf),
}

function updateFieldName(newDataToSave, keyForMapping) {
    // TODO Make this into an external forms.js service function accepting urls mapping as an option.
    // Need this to say whether or not email save is disabled
    console.log(data);
    data[keyForMapping] = newDataToSave;
}

function saveFieldName(keyForMapping){
    db.put(urlsMapping[keyForMapping], data[keyForMapping], true).then((res) => {
        data[keyForMapping] = res.data;
    });
}

async function load_shelf() {
    await db.get(urls.rtc.bookShelfTest(bookshelf)).then((res) => { 
        data.description = res.bookshelf.description
        data.title = res.bookshelf.title
        data.loaded = true;
    });
}

onMounted(async () => {
    await load_shelf();
});
</script>

<style scoped>

.danger-zone-section {
    margin-left: auto;
    margin-right: auto;
}
</style>