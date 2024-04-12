<template>
    <h1 class="work-feed-heading">Currently Reading</h1>

    <div class="currently-reading">
        <div class="currently-reading-book">
            <img class="book-img loading"/>

            <div class="book-metadata">
                <div>
                    <h4 class="book-title loading">Book title</h4>

                    <p class="progress">70 / 140</p>
                </div>

                <button>update</button>
            </div>
        </div>

        <div class="currently-reading-book loading">
            <img class="book-img loading"/>

            <div class="book-metadata">
                <div>
                    <h4 class="book-title loading">Book title</h4>

                    <p class="progress">70 / 140</p>
                </div>

                <button>update</button>
            </div>
        </div>

        <div class="currently-reading-book">
            <img class="book-img loading"/>

            <div class="book-metadata">
                <div>
                    <h4 class="book-title loading">Book title</h4>

                    <p class="progress">70 / 140</p>
                </div>

                <button type="button"
                    class="btn"
                >update</button>
            </div>
        </div>
    </div>
</template>
<script setup>

</script>
<style scoped lang="scss">
    .currently-reading {
        --x-axis-offset: 28px;
        @media screen and (max-width: 768px) {
            --x-axis-offset: 14px;
        }

        margin-top: var(--margin-sm);
        margin-bottom: var(--margin-sm);
        margin-left: auto;
        margin-right: auto;
        display: flex;
        column-gap: var(--margin-md);
        justify-content: start;
        height: fit-content;
        overflow-x: scroll;
        padding-left: var(--x-axis-offset);
    }

    .currently-reading-book {
        --min-width-cr-card: 300px;
        min-width: var(--min-width-cr-card);

        .book-metadata {
            display: flex;
            align-items: start;
            justify-content: space-between;
            padding-left: var(--margin-sm);
            padding-right: var(--margin-sm);
            
            .book-title {
                font-size: var(--font-xl);
                color: var(--stone-700);
                font-style: italic;
            }
            .progress {
                color: var(--indigo-700);
                font-weight: 500;
            }
        }
        .book-img {
            border-radius: var(--radius-md);

            &.loading{  
                background-color: var(--stone-200);
                width: 100%;
                height: 240px;
                margin-bottom: 8px;
            }
        }

    }
</style>