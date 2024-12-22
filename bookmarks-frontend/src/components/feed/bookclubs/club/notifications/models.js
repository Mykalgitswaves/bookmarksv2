const PEER_PRESSURE = 'peer-pressure'
const FINISHED_READING = 'finished-reading'

export const ClubNotification = {
    types: {
        peerPressure: PEER_PRESSURE,
        finishedReading: FINISHED_READING,
    },

    labels: {
        [PEER_PRESSURE]: 'Peer pressure',
        [FINISHED_READING]: 'Finished reading',
    },

    generateToastFromNotification: (toast) => {
        if (toast.notification_type === ClubNotification.types.peerPressure) {
            return {
                message: `Your fellow club member has been encouraged to read`,
            } 
        }
    }
}