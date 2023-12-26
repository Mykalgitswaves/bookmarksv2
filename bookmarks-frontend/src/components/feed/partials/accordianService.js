// Docu Ment Ation 🤯
// service for functions related to using accordian component. You can see example usage in social page. TLDR Create a reactive (vue) dict of booleans for toggling open and closed state. Events are emitted upward from accordian function with truthy or falsy values to set new state from user interaction.

// See how we use const social_dropdowns = reactive({}); in socialPage.vue
// We set social_dropdowns['is-pending-requests-expanded'] over template v-ifs to hide and show.

export function accordianFn(keyword, mapObject, payload) {
    mapObject[keyword] = payload;
}