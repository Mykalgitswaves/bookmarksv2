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
            <p class="text-slate-600 text-small"> mutual friends </p>
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
        border: 1px solid #f5f5f4;
    }

    .friend-request.friends {
        border-color: ;
    }

    .friend-request img {
            border-radius: 50%;
            background: #d7d7d7;
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
        background-color: #a5b4fc;
        border-radius: 8px;
        color: #fff;
        justify-self: center;
        padding: 12px;
        transition: all 250ms ease;
    }

    .friend-request-accept-btn:hover {
            background-color: #818cf8;
    }

    .friend-request-reject-btn {
        background-color: #dc2626;
        border-radius: 8px;
        color: #fff;
        justify-self: center;
        padding: 12px;
        transition: all 250ms ease;
    }

    .friend-request-reject-btn:hover {
        background-color: #b91c1c;
    }

    .friend-request-declined-text {
        color: #b91c1c;
        font-style: italic;
        font-size: 12px;
        padding-right: 12px;
    }

    .friend-request-reject-btn.block {
        background-color: #991b1b;
    }

    .friend-request-reject-btn.block:hover {
        background-color: #7f1d1d;
    }
</style>