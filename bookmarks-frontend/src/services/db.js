import { toRaw } from 'vue'

/**
// @param successRouterFunction: This is an optional param to control the routes after a successfull request,
 must be passed in as a regular function
// @param debug: This is an optional param to console log the request data at differnt points to help debug endpoints
// 
 */



export const db = {
    // Note params must be an object for this to work. Use key value.
    get: async (url, params, debug, successRouterFunction) => {
        params = typeof params === Proxy ? toRaw(params) : params
        try {
            const response = await fetch(url + '?' + new URLSearchParams(params));
            const data = await response.json();
                if(debug) {
                    console.log(data, 'data');
                    console.log(response, 'response');
                }
                if(response.ok) {
                    if(successRouterFunction) {
                        return data && successRouterFunction
                    }
                    return data
                }
        } catch(err) { return console.error(err); }
    },
    // Can use raw params not strinfigied,can even pass in proxy
    post: async (url, params, debug, successRouterFunction) => {
        // Check if you are passing in proxy and if you are convert it to a raw object before posting to database.
        try {
        params = typeof params === Proxy ? toRaw(params) : params
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    Accept: 'application.json',
                    'Content-Type': 'application/json',
                  },
                body: JSON.stringify(params)
            });
            const data = await response.json();

            // Debug state
            if(debug) {
                console.log(response, 'response')
                console.log(data, 'data')
            }
            // Success state
            if(response.ok) {
                if(successRouterFunction) {
                    return data && successRouterFunction
                }
                return data
            }
            
        } catch(err) {
            console.error(err)
        }
    }
}