const state = new Set();

export const stateCtrl = {
    state: () => state,
    add: (q) => (state.add(q)),
    has: (q) => (!!state.has(q)),
    toArray: () => (Array.from(state)),
    hasResponse: (q) => {
        const qs = Array.from(state)
        for(let question in qs) {
            if(question.response === q.response) {
                return true
            } 
        return false
        }
    }
}