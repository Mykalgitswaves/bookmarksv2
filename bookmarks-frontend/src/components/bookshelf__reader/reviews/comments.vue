<template>
  <div class="comments">
    <div class="comment" v-for="(comment, index) in comments" :key="index">
      <div></div>
      <div class="comment-content">
        <p class="comment-text"><span class="comment-quote">"</span>{{ comment.comment }}"</p>
        <div class="comment-info">
          <span class="comment-link" @click="showReply = !showReply"
            >View {{ comment.replies.length }} {{ repliesPluralization(comment) }}</span
          >
          <span class="comment-likes">{{ comment.likes }} Likes</span>
        </div>
        <div v-if="!showReply" class="replies">
          <div class="reply" v-for="(reply, replyIndex) in comment.replies" :key="replyIndex">
            <div class="reply-line"></div>
            <span class="reply-text">"{{ reply.comment }}"</span>
            <span class="reply-likes">{{ reply.likes }} Likes</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    comments: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      showReply: {}
    }
  },
  methods: {
    repliesPluralization(comment) {
      return comment.replies.length === 1 ? 'Reply' : 'Replies'
    }
  }
}
</script>

<style scoped>
.comments {
  margin-top: 1rem;
  max-width: 700px;
}

.comment {
  display: flex;
  align-items: flex-start;
  margin-top: 1rem;
}

.comment-line::before {
  content: '';
  position: absolute;
  top: -1rem;
  left: -1px;
  height: calc(100% + 4px);
  border-left: 2px solid #6366f1;
}

.comment-content {
  flex: 1;
}

.comment-text {
  color: #374151;
  font-style: italic;
}

.comment-quote {
  font-weight: bold;
}

.comment-info {
  margin-top: 0.5rem;
}

.comment-link {
  color: #6366f1;
  text-decoration: underline;
  cursor: pointer;
}

.comment-likes {
  color: #6366f1;
  margin-left: 1rem;
}

.replies {
  margin-top: 1rem;
}

.reply {
  position: relative;
  margin-left: 2rem;
}

.reply-line {
  width: 2px;
  background-color: #6366f1;
  position: absolute;
  top: 0.25rem;
  left: -2ch;
  height: calc(90%);
  border-left: 2px solid #6366f1;
}

.reply-text {
  color: #374151;
  font-style: italic;
  display: block;
}

.reply-likes {
  color: #6366f1;
  font-style: normal;
}
</style>
