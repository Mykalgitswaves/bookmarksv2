import { generateUUID } from '../../../../services/helpers';

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
    cls: 'club_update'
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
    static invitations = []
    constructor(invite) {
        const id = generateUUID();
        if (!invite) {
            this.id = id;
            this.email = '';
            this.user_id = '';
            this.type = Invitation.types.email;
            this.status = Invitation.statuses.uninvited;
        // Sent invitations don't need a type.
        } else {
            let user = invite.invited_user
            this.id = invite.invite_id
            this.email = user.email
            this.user_id = user.id;
            this.status = Invitation.statuses.invited;
            this.invited_on = formattedDateTime(invite.datetime_invited);
        }
    
        BaseInvitation.invitations.push(this);

        function formattedDateTime(dateTime){
            // If its not a valid datetime then return false
            if (isNaN(new Date(dateTime))) return false;

            const date = new Date(dateTime)
            const utcDate = new Date(date.toUTCString()); // Convert to UTC
            // Formatting the date in the desired format: "Weekday, HH:mm:ss YYYY"
            const options = { weekday: 'short', hour: '2-digit', minute: '2-digit', second: '2-digit', year: 'numeric', timeZone: 'UTC' };
            return utcDate.toLocaleDateString('en-GB', options).replace(',', ''); // Formatting
       }
    }
    
    /**
     * @param { int } id 
     * @returns Void
     */
    delete() {
        delete this;
    };
};

const ROLES = {
    
};

export class Member {

    constructor(member) {
        if (member) {
            this.user_id = member.user.user_id;
            this.username = member.user.username;
            this.email = member.user.email;
            this.role = member.role;
        } else {
            const id = generateUUID();;
            this.id = id;
            this.email = '';
            this.user_id = '';
            this.role = '';
        }
    }

}