const paceIntervals = {
    DAY: 'days',
    WEEK: 'weeks',
    MONTH: 'months',
}

const paceNames = {
    BLAZING: 'blazing',
    CASUAL: 'casual',
    STEADY: 'steady'
}

export const BookClub = {
    paceIntervals,
    paceNames,
        // num_books: 1,
        // num_time_period: 1,
        // time_period: BookClub.paceIntervals.MONTH,
        // name: BookClub.paceNames.CASUAL,
    pacePresets: {
        // casual - 1 book per 3 months
        1: {
            num_books: 1,
            num_time_period: 3,
            time_period: paceIntervals.MONTH,
            name: paceNames.CASUAL,
        },
        // steady - 1 book per month
        2: {
            num_books: 1,
            num_time_period: 1,
            time_period: paceIntervals.MONTH,
            name: paceNames.STEADY,
        },
        // blazing - 1 book per week
        3: {
            num_books: 1,
            num_time_period: 1,
            time_period: paceIntervals.WEEK,
            name: paceNames.BLAZING,
        }
    }
}
