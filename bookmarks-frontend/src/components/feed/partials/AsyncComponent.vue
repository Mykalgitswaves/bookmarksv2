<template>
    <slot name="resolved" v-if="loaded">

    </slot>
    <slot name="loading" v-else>

    </slot>
</template>
<script setup>
// --------------------------------------------------------
// Async component for a generic loading state so you don't 
// have to keep on adding loaded logic all over the place;
// --------------------------------------------------------
import { ref } from 'vue';
import { PubSub } from '../../../services/pubsub';

const props = defineProps({
    // singular function look at notifications.vue for examples
    promiseFactory: {
        type: Function,
    },
    promises: {
        type: Array[Function],
    },
    /**
     * @description
     * This is our implementation of a pub sub pattern. It is being used here in conjunction with promiseFactory 
     * to recall data from the server whenever a publisher publishes an event. The convention for naming goes like this:
     * <lower case name of component you are publishing from>-<request type: get, put, post, delete (you will probably only ever need get)>-<whatever it is you are loading>
     */
    subscribedTo: {
        type: String,
        required: false,
    }
});

const loaded = ref(false);

function load() {
    if (props.promises) {
        Promise.all(props.promises).then(() => {
            console.log('calling this stuff again')
            loaded.value = true;
        });
    // Needed for when you want to manually trigger calling new data via pub sub pattern.
    // You can't recall a raw promise. passing in the factory gives us a way to recreate 
    // as many as we need where we need to get fresh data.
    } else if (props.promiseFactory) {
        Promise.resolve(props.promiseFactory()).then(() => {
            console.log('inside load promise factory')
            loaded.value = true;
        });
    }
}

load();

// You need both dependencies for this to work because when you pass in a raw promise
// you can't call it again once its been resolved
if (props.subscribedTo && props.promiseFactory) {
    const refreshEvent = () => {
        loaded.value = false;    
        load()
    }

    PubSub.subscribe(props.subscribedTo, refreshEvent);
}
</script>