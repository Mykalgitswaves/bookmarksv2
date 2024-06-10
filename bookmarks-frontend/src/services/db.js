import { toRaw } from 'vue'
import { useRouter } from 'vue-router'
import { helpersCtrl } from './helpers';
/**
// @param successRouterFunction: This is an optional param to control the routes after a successfull request,
 must be passed in as a regular function
// @param debug: This is an optional param to console log the request data at differnt points to help debug endpoints
// 
 */

export const db = {

    // THis assumes you already have accessToken saved onto cookies.
    authenticate: async (url, uuid) => {
        const router = useRouter();
        const accessTokenFromCookies = helpersCtrl.getCookieByParam(['token'])
        
        try {
            const response = await fetch(url + '?' + new URLSearchParams({'uuid': uuid}), {
                method: 'GET',
                headers: {
                    Authorization: `Bearer ${accessTokenFromCookies}`,
                    'Content-Type': 'application/json',
                }
            })
            const data = response.json()
            
            if(response.ok) {
                return data
            } else {
                router.push('/');
            }
        } catch(err) {
            console.error(err)
            router.push('/')
        }
    },
        // Note params must be an object for this to work. Use key value.
    get: async (url, params, debug, successRouterFunction) => {
        params = (typeof params === Proxy ? toRaw(params) : params)
        try {
            const token = helpersCtrl.getCookieByParam(['token'])
            const response = await fetch(url + '?' + new URLSearchParams(params), {
                method: 'GET',
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const data = await response.json();
                if(debug) {
                    console.log(data, 'data');
                    console.log(response, 'response');
                }
                if(response.ok || response.status === 200) {
                    if(successRouterFunction) {
                        return data && successRouterFunction
                    }
                    console.log('returning', data)
                    return data
                }
        } catch(err) { return console.error(err); }
    },
    // Can use raw params not strinfigied,can even pass in proxy
    post: async (url, params, debug, successRouterFunction, failureFunction) => {
        const token = helpersCtrl.getCookieByParam(['token']);
        console.log(token)
        // Check if you are passing in proxy and if you are convert it to a raw object before posting to database.
        try {
        params = typeof params === Proxy ? toRaw(params) : params
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${token}`,
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
                    successRouterFunction(data)
                }
                return data
            }
            if(!response.ok){
                if(failureFunction){
                    failureFunction(data)
                }
            }
            
        } catch(err) {
            console.error(err)
        }
    },
    // Can use raw params not strinfigied,can even pass in proxy
    put: async (url, params, debug, successRouterFunction) => {
        const token = helpersCtrl.getCookieByParam(['token']);
        console.log(token)
        // Check if you are passing in proxy and if you are convert it to a raw object before posting to database.
        try {
        params = typeof params === Proxy ? toRaw(params) : params
            const response = await fetch(url, {
                method: 'put',
                headers: {
                    Authorization: `Bearer ${token}`,
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
    },
    delete: async function(url, params, debug, successRouterFunction, failureFunction) {
        const token = helpersCtrl.getCookieByParam(['token']);
        console.log(token)
        try {
            params = typeof params === Proxy ? toRaw(params) : params
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    Authorization: `Bearer ${token}`,
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