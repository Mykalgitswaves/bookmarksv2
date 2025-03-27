<template>
        <div class="bookclub-header flex justify-between items-start">
            <div>
                <h1 class="text-3xl fancy text-stone-700">
                    {{ clubHeading.title }}
                </h1>
                
                <p class="text-stone-500 mt-5">
                    {{ clubHeading.description || 'Add a description for your book club' }}    
                </p>
            </div>

            <button type="button" class="pt-5 text-stone-500" @click="openClubSettingsOverlay">
                <span class="visually-hidden">Settings</span>
                
                <IconNote />
            </button>
        </div>

        <section v-if="loaded" 
            class="club-main-padding"
            :class="{
                'is-user-finished-with-current-book': club.currently_reading_book?.is_user_finished_reading
            }"
        >
            <CurrentlyReadingBook 
                :is-finished-reading="currentlyReadingBook?.is_user_finished_reading"
                :book="currentlyReadingBook" 
                @currently-reading-settings="router.push(
                    navRoutes.bookClubSettingsCurrentlyReading(
                        route.params.user, 
                        route.params.bookclub
                    )
                )"
            />

            <CurrentPacesForClubBook :total-chapters="currentlyReadingBook?.chapters"/>

            <!-- Sticky toolbar containing buttons for creating and filtering posts -->
            <BookClubFeedActions 
                v-if="currentlyReadingBook"
                @start-club-update-post-flow="showUpdateForm()"
                @finished-reading="showFinishedReadingForm()"
            />

            <Overlay :ref="(el) => overlays.updateOverlay = el?.dialogRef">
                <template #overlay-header>

                </template>
                <template #overlay-main>
                    <CreateUpdateForm 
                        style="width: 768px; margin-left: auto; margin-right: auto;"
                        :book="currentlyReadingBook" 
                        @post-update="(update) => postUpdateForBookClub(update)"
                    />
                </template>
            </Overlay>

            <Overlay :ref="(el) => overlays.finishedReadingOverlay = el?.dialogRef">
                <template #overlay-header>

                </template>
                <template #overlay-main>
                    <CreateReviewPost 
                        :book="currentlyReadingBook"
                        unique="bookclub"
                        @is-postable-data="(post) => reviewPost = post" 
                        @post-data="postReviewAndFinishReadingCurrentBook(reviewPost)"
                        @user-skipped-review="postReviewAndFinishReadingCurrentBook(null)"
                    />
                </template>
            </Overlay>

            <Overlay :ref="(el) => overlays.clubSettingsOverlay = el?.dialogRef">
                <template #overlay-main>
                    <form 
                        :validation-schema="formSchema" 
                        class="grid gap-y-5 w-[80vw] md:w-[60vw] max-w-[800px]"
                        @submit="onSubmit"
                    > 
                        <FormField v-slot="{ componentField }" name="title" :validate-on-blur="!isFieldDirty">
                            <FormItem>
                                <FormLabel class="fancy text-base text-stone-600">Title</FormLabel>
                                
                                <FormControl>
                                    <Input name="title" v-bind="componentField" />
                                </FormControl>

                                <FormDescription>
                                    Change the title of your bookclub
                                </FormDescription>

                                <FormMessage />
                            </FormItem>
                        </FormField>
                        <FormField v-slot="{ componentField }" name="description" :validate-on-blur="!isFieldDirty">
                            <FormItem>
                                <FormLabel class="fancy text-base text-stone-600">Description</FormLabel>
                                
                                <FormControl>
                                    <Textarea name="description" v-bind="componentField" />
                                </FormControl>

                                <FormDescription>
                                    Change the description of your bookclub
                                </FormDescription>
                            </FormItem>
                        </FormField>

                        <div class="flex items-center ml-auto mr-auto gap-5">
                            <Button 
                                type="submit" 
                                class="btn btn-submit fancy" 
                                :disabled="!metaValuesHaveChanged">Save
                            </Button>

                            <Button 
                                type="button" 
                                class="btn btn-red fancy w-fit" 
                                @click="overlays.clubSettingsOverlay.close()"
                            >Cancel
                            </Button>
                        </div>
                    </form>
                    
                
                </template>

            </Overlay>

            <!-- index for now until we can grab the id from the updates -->
            <ClubPost
                v-for="(post, index) in data.posts" 
                :key="index" 
                :post="post"
            />
        </section>

        <LoadingCard v-else />

        <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
// ----------------------------------
// Vue
import { ref, watch, defineAsyncComponent } from 'vue';
import { useRoute, useRouter } from 'vue-router';
// ----------------------------------
// Services
import { navRoutes, urls } from '../../../../services/urls';
import { db } from '../../../../services/db';
import { createConfetti } from '../../../../services/helpers';
import { formatUpdateForBookClub } from '../bookClubService';
// ----------------------------------
// Stores

import { currentUser } from '../../../../stores/currentUser.ts';

// ----------------------------------
// Form stuff
// ----------------------------------
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';

// ----------------------------------
// Components
// ----------------------------------

// -- shadcdn vue port
import {
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from '@/lib/registry/default/ui/form';
import { Input } from '@/lib/registry/default/ui/input';
import { Textarea } from '@/lib/registry/default/ui/textarea/index.ts';
import { Button } from '@/lib/registry/default/ui/button';

import LoadingCard from '../../../shared/LoadingCard.vue';

// -- hardcover
const CurrentlyReadingBook = defineAsyncComponent(() => import('./CurrentlyReadingBook.vue'));
const BookClubFeedActions = defineAsyncComponent(() => import('./BookClubFeedActions.vue'));
const ClubPost = defineAsyncComponent(() => import('./posts/ClubPost.vue'));
const Overlay = defineAsyncComponent(() => import('@/components/feed/partials/overlay/Overlay.vue'));
const CreateUpdateForm = defineAsyncComponent(() => import('@/components/feed/createPosts/update/createUpdateForm.vue'));
const CreateReviewPost = defineAsyncComponent(() => import('@/components/feed/createPosts/createReviewPost.vue'));
const CurrentPacesForClubBook = defineAsyncComponent(() => import('./CurrentPacesForClubBook.vue'));
// SVG
import IconNote from '@/components/svg/icon-note.vue';
// ----------------------------------

const props = defineProps({
    club: {
        type: Object,
        required: true,
    }
});

const clubHeading = ref({
    title: props.club.book_club_name || '',
    description: props.club.book_club_description || ''
});

const data = ref({
    posts: [],
});

const loaded = ref(false);

const overlays = ref({
    updateOverlay: null,
    finishedReadingOverlay: null,
    wrappedOverlay: null,
    clubSettingsOverlay: null,
});

const route = useRoute();
const router = useRouter();
const {user, bookclub} = route.params;
const isUserFinishedReadingBook = ref(false);
const reviewPost = ref(null);

let currentlyReadingBook = {};

function showUpdateForm() {
    const dialogRef = overlays.value?.updateOverlay;
    dialogRef?.showModal();
};

function showFinishedReadingForm() {
    const dialogRef = overlays.value.finishedReadingOverlay;
    dialogRef?.showModal(); 
}

function openClubSettingsOverlay() {
    const dialogRef = overlays.value.clubSettingsOverlay;
    dialogRef?.showModal();
};

/**
 * @form_metadata 
 * @description – Update the description of the form.
 */

 const formSchema = toTypedSchema(
  z.object({
    title: z.string().min(1, "Title is required"),
    description: z.string().optional(),
  })
);

const form = ref({
  title: props.club?.book_club_name || '',
  description: props.club?.book_club_description || '',
});

const { handleSubmit } = useForm({
  validationSchema: formSchema,
  initialValues: {
    title: form.value.title,
    description: form.value.description
  }
});

// Used to make the button clickable.
const metaValuesHaveChanged = (values) => {
    return clubHeading.value.title !== values.title || 
           clubHeading.value.description !== values.description;
};

const onSubmit = handleSubmit((values) => {
    if (!metaValuesHaveChanged(values)) {
        return;
    }

    db.put(urls.bookclubs.updateClubSettings(bookclub), values, false,
        (res) => {
            const { club } = res;
            clubHeading.value.title = club.title;
            clubHeading.value.description = club.description;
            // Close the overlay and refresh data
            const { dialogRef } = overlays.value.clubSettingsOverlay;
            dialogRef?.close();
            // You might want to refresh the club data here
            // or emit an event to the parent component
        },
        (err) => {
        console.error(err);
        }
    );
});


/**
 * @load
 * @description – Reruns every time the club loads
 */

// If you are done reading call a different url.
let feedUrl = urls.bookclubs.getClubFeed(route.params.bookclub);
if (props.club.currently_reading_book.is_user_finished_reading) {
    feedUrl = urls.bookclubs.getFinishedClubFeed(route.params.bookclub);
};

const clubFeedPromise = db.get(feedUrl, null, false, (res) => {
    data.value.posts = res.posts;
},
(err) => {
    console.log(err);
});

const clubFeedPromiseFactory = () => db.get(feedUrl, null, false, (res) => {
    data.value.posts = res.posts;
},
(err) => {
    console.log(err);
});

const currentlyReadingPromise = db.get(urls.bookclubs.getCurrentlyReadingForClub(bookclub), null, false, (res) => {
    currentlyReadingBook = res.currently_reading_book;
});

Promise.allSettled([clubFeedPromise, currentlyReadingPromise]).then(() => {
    loaded.value = true;
});



// If you are coming from notifications tab, then load the showUpdateForm, then unwatch watcher.
watch(() => overlays.value.updateOverlay, () => {
    if (route.query['make-update']) {
        showUpdateForm()
    }  
    watch()
}, {immediate: false});


// So users can scroll up and refresh feed. 
function refreshFeed() {
    loaded.value = false;
    Promise.resolve(clubFeedPromiseFactory()).then(() => {
        loaded.value = true;
    });
}


/**
 * @post
 */
function postUpdateForBookClub(update) {
    update = formatUpdateForBookClub(update, route.params.user)

    db.post(urls.bookclubs.createClubUpdate(bookclub), update, false, 
        (res) => {
            console.log(res);
            // Refresh;
            const { dialogRef } = overlays.value.updateOverlay;
            dialogRef?.close();
            createConfetti();
            refreshFeed();
        },
        (err) => {
            console.warn(err);
        },
    );
};


// Allow posting and then closing the overlay.
function postReviewAndFinishReadingCurrentBook(post) {
    post.user = {id: currentUser.value.id }

    if (!post) {
        db.post(
            urls.concatQueryParams(
                urls.bookclubs.postClubReviewAndFinishReading(bookclub, props.club.currently_reading_book.book_club_book_id),
                { no_review: true },
            ), 
            null, 
            false, 
            (res) => {
                isUserFinishedReadingBook.value = true;
            }, (err) => {
                console.error(err);
            }
        );
    } else {   
        db.post(urls.bookclubs.postClubReviewAndFinishReading(bookclub, props.club.currently_reading_book.book_club_book_id), 
            post, 
            false, 
            (res) => {
                isUserFinishedReadingBook.value = true;
            }, 
            (err) => {
                console.error(err);
            }
        );
    };

    const { dialogRef } = overlays.value.finishedReadingOverlay;
    dialogRef?.close();
    createConfetti();
}
</script>