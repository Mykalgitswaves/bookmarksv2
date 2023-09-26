const state = new Set();

export const stateCtrl = {
    state: () => state,
    add: (q) => {
        // Make sure people arent just adding anything
        if(q.response !== "") {
            console.log(q, 'b4 add')
            state.add(q)
            console.log(state, 'after add')
        }
    },
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
    },
    delete: (q) => state.delete(q)
}