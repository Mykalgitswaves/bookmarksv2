export const db = {
    // Note params must be an object for this to work. Use key value.
    get: async (url, params, debug) => {
        try {
            const response = await fetch(url + '?' + new URLSearchParams(params));
            const data = await response.json();
                if(debug) {
                    console.log(data, 'data');
                    console.log(response, 'response');
                }
            return data
        } catch(err) { return console.error(err); }
    }
}