import { defineStore } from 'pinia';
import { ref } from 'vue';
/**
 * Interface declaration for Question, contains properties id (of a question),
 * Q: The actual question itself, 
 * response: default is empty string, gets modeled in js and sent back as filled out entry.
 * is_spoiler: Default is false, otherwise user can set true.
 * @param {Question} - dictionary sent to server
 * @returns { 
 *  id: Number,
 *  q: String
 *  response: String,
 *  is_spoiler: Boolean,
 * } 
 */
// Simple two part store, we use maps to keep track of overwriting questions and on change set arr.value = state.
// for easy access in our ui.
export const createQuestionStore = defineStore('questions', () => {
    const state = new Map();
    const arr = ref([]);

    // Convert the Map to an array for easier rendering in the Vue template
    function updateArr() {
        arr.value = [...state.values()];
    }
    
    // Add or update a question in the map
    function addOrUpdateQuestion(question) {
        if (!state.has(question)) {
            state.set(question.id, question);
            updateArr();
        }
    }
          
    // Delete a question from the map based on id
    function  deleteQuestion(question) {
        state.delete(question.id);
        updateArr();
    }

    return { state, arr, addOrUpdateQuestion, deleteQuestion }
})