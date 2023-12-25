<template>
    <div class="friend-request"
        :class="{
            'friends': rel_to_user === 'friends',
            'declined': rel_to_user === 'declined',
            'blocked': rel_to_user === 'blocked'
        }"
    >
        <img :src="profileImg || placeholder" alt="">
        <div class="friend-request-heading">
            <h3 class="text-slate-800">{{ username }}</h3>

            <p class="text-slate-600 text-small" v-if="rel_to_user !== 'blocked'"> mutual friends </p>
        </div>

        <div class="friend-request-btns">
            <FriendBtn
                v-for="(button, index) in buttons[rel_to_user]"
                :key="index"
                :type="button.type"
                :alt="button.alt"
                :class="button.classes"
                :click="button.click"
                :text="button.text"
                :payload-data="payloadData"
                @rel-to-user-changed="($event) => relToUserChangedFn($event)"
            >   
                <template 
                    v-if="button.icon" 
                    v-slot:icon
                >
                    <component :is="button.icon" />
                </template>
            </FriendBtn>
        </div>
    </div>
</template>

<script setup>
import { friendRequestButtons } from './friendRequestButton';
import { computed, ref, onMounted, reactive } from 'vue';
import { useRoute } from 'vue-router';
import FriendBtn from './FriendBtn.vue';

const route = useRoute();
const { user } = route.params
const username = computed(() => props.userData.from_user.username);
const user_id = computed(() => props.userData.from_user.user_id);
const rel_to_user = ref(props.userData.from_user.relationship_to_current_user);
const buttons = friendRequestButtons;

const props = defineProps({
    userData: {
        type: Object,
        required: true
    }
});

function relToUserChangedFn(data) {
    rel_to_user.value = data;
}

const payloadData = reactive({});
const profileImg = props.userData.profile_img_url;

onMounted(() => {
    payloadData.user = user;
    payloadData.user_id = user_id;
});
</script>
<style scoped>
    .friend-request {
        display: grid;
        grid-template-columns: min-content auto .35fr;
        height: min-content;
        padding: 12px;
        border-radius: 8px; 
        background-color: var(--surface-primary);
        border: 1px solid var(--stone-200);
    }

    .friend-request.friends {
        border-color: var(--green-300);
        background-color: var(--green-50);
    }

    .friend-request.blocked {
        border-color: var(--red-200);
        background-color: var(--red-50);
    }

    .friend-request.declined {
        border-color: var(--stone-200);
        background-color: var(--stone-50);
    }

    .friend-request img {
            border-radius: 50%;
            background: var(--slate-300);
            width: 50px;
            margin-right: 24px;
        }
    .friend-request-btns {
        display: grid;
        grid-template-columns: repeat(2, minmax(40px, min-content));
        margin-right: 12px;
        column-gap: 1em;
        justify-content: flex-end;
    }

    .friend-request-heading {
        overflow-wrap: anywhere;
    }

    .friend-request-accept-btn {
        background-color: var(--indigo-400);
        border-radius: 8px;
        color: var(--gray-50);
        justify-self: center;
        padding: 12px;
        transition: all 250ms ease;
    }

    .friend-request-accept-btn:hover {
            background-color: var(--indigo-600);
    }

    .friend-request-reject-btn {
        background-color: var(--red-600);
        border-radius: 8px;
        color: var(--gray-50);
        justify-self: center;
        padding: 12px;
        transition: all 250ms ease;
    }

    .friend-request-reject-btn:hover {
        background-color: var(--red-800);
    }

    .friend-request-declined-text {
        color: var(--red-600);
        font-style: italic;
        font-size: 12px;
        padding-right: 12px;
    }

    .friend-request-reject-btn.block {
        background-color: var(--red-600);
    }

    .friend-request-reject-btn.block:hover {
        background-color: var(--red-800);
    }
</style>