<template>
   <div class="mt-5" v-for="(comment, index) in comments" :key="index">
        <p class="text-slate-500 italic">
            <span class="font-bold">"</span>{{ comment.comment }}"
        </p>

        <div class="mt-2">
            <span class="text-slate-600 underline cursor-pointer" @click="showReply = !showReply"> View {{ comment.replies.length }} {{ repliesPluralization(comment) }}</span>    
            <span class="text-slate-600 ml-5">{{ comment.likes }} Likes</span> 
        </div>

        <div v-if="!showReply" class="ml-5 mt-4">
            <span
                class="text-slate-600 italic" 
                v-for="(reply) in comment.replies" 
                :key="reply"
            >
                "{{ reply.comment }}"

                <span class="not-italic block">
                    {{ reply.likes }} Likes
                </span>
            </span>
        </div>
   </div>  
</template>

<script>
    export default {
       props: {
        comments: {
            type: Array,
            required: true,
        }
       },   
        data() {
          return {
            showReply: {
                type: Boolean,
                default: false
            }
          }
       },
       methods: {
        repliesPluralization(comment) {
            return comment.replies.length >= 0 ? 'Reply' : 'Replies'
        }
       }
    }
</script>