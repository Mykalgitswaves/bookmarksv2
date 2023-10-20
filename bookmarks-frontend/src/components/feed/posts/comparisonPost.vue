<template>
    <div class="card">
        <div class="card-header">
            <p class="text-slate-600"><span class="text-indigo-600 underline italic cursor-pointer">@{{ props.username }}</span> made a comparison</p>
        </div>
        <div class="card-content-main">
            <h3><span class="book-title-span-wrap">{{ props.book_title[0] }}</span> and <span class="book-title-span-wrap">{{ props.book_title[1] }}</span></h3>

            <div class="comparison-images">
                <img class="comparison-image" :src="props.small_img_url[0]" alt="">

                <IconLinkArrow />
                
                <img class="comparison-image" :src="props.small_img_url[1]" alt="">
            </div>
        </div>
        <div class="card-responses">

        </div>
    </div>
</template>
<script setup>
import IconLinkArrow from '../../svg/icon-arrow-link.vue';
const props = defineProps({
    book: {
        type: Array,
        required: true
    },
    book_title: {
        type: Array,
        required: true,
    },
    small_img_url: {
        type: Array,
        required: true
    },
    headlines: {
        type: Array,
        required: false,
    },
    comparisons: {
        type: Array,
        required: true
    },
    comparator_ids: {
        type: Array,
        required: true
    },
    createdAt: {
        type: String,
        required: true,
    },
    username: {
        type: String,
        required: true,
    },
    id: {
        type: String,
        required: true,
    },
    isIronic: {
        type: Boolean,
        required: false,
        default: false,
    },
    isAiGeneratedHeadlines: {
        type: Boolean,
        required: false,
        default: false
    }
})
console.log(props)

// :headlines="post.book_specific_headlines"
// :book_title="post.book_title"
// :comparisons="post.responses"
// :comparator_ids="post.comparators"
// :created_at="post.created_date"
// :id="post.id"
// :username="post.user_username"
</script>

<style scoped>

.card {
    text-align: center;
    border: 1px solid #A0AEC0;
    border-radius: 5px;
    margin-top: 1rem;
    margin-bottom: 1rem;
    max-width: 800px;
}

.card-header {
    padding: 15px 20px;
    border-bottom: 1px solid #A0AEC0;
}

.card-content-main {
    padding: 15px 20px;
}

.card-content-main h3 {
    margin-bottom: 1rem;
}

.book-title-span-wrap {
    display: inline-block;
    overflow-wrap: break-word;
    width: 146px;
}
.comparison-images {
    display: flex;
    column-gap: 20px;
    align-items: center;
    justify-content: center;
    color: #4f46e5;
}

.comparison-image {
    object-fit: cover;
    height: 137px;
    width: 100px;
}
</style>