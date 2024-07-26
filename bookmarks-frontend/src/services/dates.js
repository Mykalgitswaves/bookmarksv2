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
    }
}