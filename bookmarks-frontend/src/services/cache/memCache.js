/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
// MEM CACHE NERDAGE FOR YOU TO DECIDE TO USE AT A LATER DATE
// CHECK OUT OUR CACHE SYSTEM DESIGN ON THE PENPOT PAGE.
// Also view the png attached in the same directory.
/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////

const MEM_CACHE_MAP = {};
// Maybe a good starting point is to have a default be 1 minute.
const DEFAULT_EXPIRATION_DURATION = 600 //# milliseconds;


// USE the request URL as a way to cache info on the front end for better performance. 
export const memCache = {
    spinUp: () => {

    },
    checkAge: (url) => {
        // need to handle scenario that url isn't in cache yet so .age would throw.
        if(!MEM_CACHE_MAP[`${url}`]) return false;
        // otherwise take the Date.isString and find out if its later than
        // Date(dateIsoString) + DEFAULT_EXPIRATION_DURATION
        MEM_CACHE_MAP[`${url}`].age
    },
    get: (url, requestHasBody, dbFunc) => {
        if(!url || !dbFunc || !requestHasBody) throw new Error('Invalid args: missing a url[str], requestHasBody[bool], or dbFunc[Promise]')
        // Don't try and cache a db call that might have a different body.
        // Early out instead and call the function.
        if (requestHasBody) return dbFunc();
        
        // If there is a cache key set, return the value of that if its not expired.    
        if (cached_url.value && checkAge(cached_url.age)) return cached_url;
        
        MEM_CACHE_MAP[`${url}`] = {};
        let cached_url = MEM_CACHE_MAP[`${url}`];

        // OTHERWISE Call the dbFunc, store result of the promise
        // and return the data. 
        cached_url = {};
        cached_url.value = Promise.resolve(dbFunc()).then((res) => res);
        cached_url.age = new Date().toISOString;
        return cached_value.value;
    }
};


// How do we deal with invalidation?
// We need to persist a timestamp for the last time 
// we called the particular dbFunc in order to check and see if it's 
// time to refresh(revalidate) the cache.
// We could use some kind of a backgroundTask to do this.


//BIG BRAIN MOMENT
// EPOCH TIME. DATETIME DISPLAYED..... INTEGER, 