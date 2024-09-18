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
    },
}


export const ClubUpdatePost = {
        cls:  'club_update_post'
}

export const ClubReviewPost = {
    cls: 'club_review_post'
}

export const Invitation = {
    cls: 'invitation',
    // Invites might be to users that are not members of our app.
    // We need to specify...

    types: {
        email: 'email',
        existing_user: 'existing_user',
    },

    statuses: {
        uninvited: 'uninvited',
        invited: 'invited',
        accepted: 'accepted',
        refused: 'refused',
    }
};

// Default for new invitations
export class BaseInvitation {
    static invitations = [];

    constructor() {
        this.id = BaseInvitation.invitations.length + 1;
        this.email = '';
        this.user_id = '';
        this.selected = false;
        this.type = Invitation.types.email;
        this.status = Invitation.statuses.uninvited;

        BaseInvitation.invitations.push(this);
    }
    
    /**
     * @param { int } id 
     * @returns Void
     */
    static delete(id) {
        let inviteToDelete = this.invitations.find(invitation => invitation.id === id);
        let index = this.invitations.indexOf(inviteToDelete)
        this.invitations.splice(index, 1);
        // TODO: think about adding some unit test coverage for this class
    }   
};