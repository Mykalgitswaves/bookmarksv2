<template>
    <!-- Top nav bar that is absolute positioned, for making posts and filtering posts -->
    <div class="feed-menu-nav" role="menubar">
      <div class="btn-relative">
        <button 
          ref="show-modal-btn"
          class="flex items-center gap-2 justify-center px-2 py-2 rounded-md text-white bg-indigo-600"
          type="button"
          @click="modals.selectDropdown = !modals.selectDropdown"
        >
          <IconPlus />
          
          <span>Make a Post</span>
        </button>

        <div v-close-modal="{
          exclude: ['show-modal-btn'],
          handler: closeModal,
          args: ['selectDropdown']
        }">
          <div v-if="modals.selectDropdown"
            class="popout-flyout shadow-lg"
          >
            <button type="button" 
              v-for="(option, index) in postOptions"
              :key="index"
              @click="navigate(createPostBaseRoute, option)"  
            >
              {{ option }}
            </button>
          </div>
        </div>
      </div>


      <div class="btn-relative">
        <button
          v-if="!toggleCreateReviewType"
          ref="create-review-btn"
          type="button"
          class="flex items-center justify-center gap-2 px-2 py-2 bg-indigo-100 text-indigo-600 rounded-md"
          @click="modals.filterPopout = !modals.filterPopout"
        >
            <IconFilter />
            Filter
        </button>

        <div v-close-modal="{
          exclude: ['create-review-btn'],
          handler: closeModal,
          args: ['filterPopout']
        }">
          <div
            v-if="modals.filterPopout"
            class="popout-right shadow-lg px-2 py-2"
          >
            <div 
              v-for="(option, index) in filterOptions" 
              :key="index"
              class="is_ai my-2"
            >
              <label :for="index + '-option'">
                <input 
                  type="checkbox"
                  :id="option.pk + '-option'"
                  v-model="option.is_active"
                  :value="false"
                />
                {{ option.filter }}
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>
<script setup>
import { reactive } from 'vue';
import { navigate } from './createPostService';
import { filterOptions } from './filters.js';
import IconPlus from '../svg/icon-plus.vue'
import IconExit from '../svg/icon-exit.vue';
import IconFilter from '../svg/icon-filter.vue';

const props = defineProps({
    user: {
        type: String,
        required: true,
    },
});

const createPostBaseRoute = `/feed/${props.user}/create`;
const postOptions = ['review', 'update', 'comparison'];
// Used to show and hide modals.
const modals = reactive({
  selectDropdown: false,
  filterPopout: false,
});

function closeModal(reactiveKey) {
  modals[reactiveKey] = false;
}
</script>
<style scoped>
  .feed-menu-nav {
    position: sticky;
    display: flex;
    column-gap: 10px;
    justify-content: space-between;
    padding: 10px;
    top: 5px;
  }

  .text-white {
    color: white;
  }
</style>