export const dates = {
    /**
     * @description takes a date time and returns a localized string
     * @param { string|Date } datetime 
     * @returns { eg: 'mm/dd/yyyy @ 0:00 PM' }
     */
    dateAtTime: (datetime) => {
        if (!datetime) return null;
        let date;

        if (typeof datetime === 'string'){
            date = new Date(datetime);
        }
        
        const day = date.getDay();
        const month = date.getMonth();
        const year = date.getFullYear();
        const time = date.toLocaleTimeString();
        return `${month}/${day}/${year} @ ${time}`;
    },
    /**
     * Given a period of time, return how long ago it is 
     * relative to know it was. 
     * NOTE: Does not deal with locale.
     * @param {datetime} datetime 
     * @returns {string}
     */
    timeAgoFromNow: (datetime) => {
        if (!datetime) return null;
        let date;

        if (typeof datetime === 'string') {
            date = new Date(datetime)
        }

        let now = new Date();
        let diff = Math.ceil((now - date) / 3600000);

        if (diff < 24) return `${diff} hours ago`;

        else if (diff >= 24 && diff < 168) {
            let days = Math.floor(diff / 24);
            return `${days} days ago`; 
        } 

        else if (diff >= 168 && diff < 730) {
            let weeks = Math.floor(diff / 168)
            return `${weeks} weeks ago`;
        }

        else if (diff > 730) {
            let months = Math.floor(diff / 730);
            return `${months} months ago`;    
        }
    }
}