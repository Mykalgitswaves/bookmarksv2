<template>
    <div class="bookclub-header">
        <div>
            <h1 class="text-3xl fancy text-stone-700">
                Currently Reading
            </h1>
            
            <p class="text-stone-500 mt-5">
                <span v-if="!data.currentlyReadingBook">
                    Set what book you're members are currently reading
                </span>
                <span v-else>
                    What your club is currently reading
                </span>
            </p>
        </div>
    </div>

    <AsyncComponent :promises="[currentlyReadingPromises]">
        <template #resolved>
            <section class="transition">
                <div v-if="!!data.currentlyReadingBook" class="mb-10">
                    <SelectedBook 
                        :book="data.currentlyReadingBook" 
                        :set-book="true"
                        :finished="data.finished" 
                    />

                    <CurrentPacesForClubBook 
                        :start-open="true" 
                        :total-chapters="data.currentlyReadingBook.chapters" 
                    />

                    <div class="divider pb-5"></div>
                    
                    <!-- TODO: check to see if you are the owner and your club hasn't already finished reading -->
                    <div class="flex justify-around" v-if="!data.finished.club && data.user.isOwner">
                        <Dialog>
                            <DialogTrigger>
                                <span class="block fancy">We've finished reading</span>
                            </DialogTrigger>

                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>We've finished reading this book</DialogTitle>
                                    <DialogDescription>
                                    Your club members have all finished reading and are ready for their awards ceremony
                                    </DialogDescription>
                                </DialogHeader>

                                <Button variant="outline" :disabled="submitting" @click="finishCurrentlyReadingBookForClub()">
                                        Set current book as completed ✅
                                </Button>

                                <DialogFooter>
                                    <span class="text-xs text-stone-400">Note, This will set the currently read book as finished for all readers. No more updates can be posted</span>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>

                        <Dialog>
                            <DialogTrigger>
                                <span class="block fancy text-red-500">Stop reading this book</span>
                            </DialogTrigger>

                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Stop reading this book</DialogTitle>
                                    <DialogDescription>
                                        Might be the weather, might be the words, we aren't feeling it.
                                    </DialogDescription>
                                </DialogHeader>

                                <Button variant="destructive" :disabled="submitting" @click="stopReadingBook()">
                                        Stop reading {{ data.currentlyReadingBook.title }}
                                </Button>

                                <DialogFooter>
                                    <span class="text-xs text-stone-400">
                                        this will remove the current book, No more updates or reviews can be posted. Doing this bypasses your awards ceremony
                                    </span>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    </div>
                </div>

                <div v-else class="mt-10">
                    <SetCurrentlyReadingForm
                        v-if="data.isShowingSetCurrentBookForm"
                        @updated-current-book="(book) => {
                            data.currentlyReadingBook = book;
                            data.isShowingSetCurrentBookForm = false;
                            router.push(navRoutes.toBookClubFeed(route.params.user, route.params.bookclub))
                        }"
                    />
                </div>

                <Toaster />
            </section>
        </template>
        <template #loading>
            <div class="mt-10 gradient fancy text-center text-xl loading-box">
                Loading settings
            </div>
        </template>
    </AsyncComponent>

    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import { db } from '../../../../services/db';
import { urls, navRoutes } from '../../../../services/urls';
import { ref, h } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import SetCurrentlyReadingForm from './SetCurrentlyReadingForm.vue';
import SelectedBook from './SelectedBook.vue';
import CurrentPacesForClubBook from '../club/CurrentPacesForClubBook.vue';
import AsyncComponent from '../../partials/AsyncComponent.vue';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/lib/registry/default/ui/dialog';
import { Button } from '@/lib/registry/default/ui/button';
import { Toaster, ToastAction } from '@/lib/registry/default/ui/toast'
import { useToast } from '@/lib/registry/default/ui/toast/use-toast'

const { toast } = useToast()

const route = useRoute();
const router = useRouter(); 
const { bookclub } = route.params;
const submitting = ref(false);

const data = ref({
    currentlyReadingBook: null,
    isClubFinishedReading: false, // default to falsey value for starters.
    finished: {
        user: false,
        club: false,
    },
    user: {
        isOwner: false,
        isMember: false,
    }
});


const currentlyReadingPromiseFactory = () => db.get(urls.bookclubs.getCurrentlyReadingForClub(bookclub), 
    null, true, 
    (res) => {
        data.value.currentlyReadingBook = res.currently_reading_book;   
    }, 
    (err) => {
        console.log(err);
    }
);

const currentlyReadingStatusPromiseFactory = () => db.get(
    urls.bookclubs.getCurrentlyReadingStatusForClub(bookclub), 
    null, 
    false, 
    (res) => { 
        data.value.finished = {
            user: res.data.is_user_finished_with_current_book,
            club: res.data.is_club_finished_with_current_book,
        };
        data.value.user = {
            isOwner: res.data.is_owner,
            isMember: res.data.is_member,
        };
    }, (err) => {
        console.log(err);
    }
);

const currentlyReadingPromises = Promise.allSettled([currentlyReadingPromiseFactory(), currentlyReadingStatusPromiseFactory()]); 

async function finishCurrentlyReadingBookForClub() {
    submitting.value = true;
    db.post(urls.bookclubs.finishCurrentlyReadingBookForClub(bookclub), null, false, () => {
        submitting.value = false;
        data.value.currentlyReadingBook.isFinishedReading = true;
        toast({
            title: 'Finshed reading 🎉',
            description: `${data.value.currentlyReadingBook.title} on ${Date().toString()}`,
        });     
    }, () => {
        submitting.value = false;
        toast({
            title: 'Failed to set finshed reading ❌',
            description: 'Your request failed 🧐',
            action: h(ToastAction, {
                altText: 'Try again',
                }, {
                // lil recursive ness hopefull wont fuck everything up?
                default: async () => await finishCurrentlyReadingBookForClub()
            }),
        }); 
    })
}

async function stopReadingBook() {
    submitting.value = true;
    db.post(urls.bookclubs.stopCurrentlyReadingBookForClub(bookclub), null, false, () => {
        submitting.value = false;
        data.value.currentlyReadingBook = null;
        toast({
            title: 'Stopped reading',
            description: `You are no longer reading ${data.value.currentlyReadingBook.title}`,
        });
    }, () => {
        submitting.value = false;
        toast({
            title: 'Failed to stop reading ❌',
            description: 'Your request failed 🧐',
            action: h(ToastAction, {
                altText: 'Try again',
                }, {
                // lil recursive ness hopefull wont fuck everything up?
                default: async () => await stopReadingBook()
            }),
        }); 
    })
}

</script>
<style scoped>
    @starting-style {
        .transition {
            opacity: 0;
        }
    }

    .transition {
        transition: all 250ms ease; 
    }
</style>