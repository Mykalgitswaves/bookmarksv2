export const ClubNotification = {
    types: {
        peerPressure: 'peer-pressure'
    },

    generateToastFromNotification: (toast) => {
        if (toast.notification_type === types.peerPressure) {
            return {
                message: `Your fellow club member has been encouraged to read`,
            } 
        }
    }
}