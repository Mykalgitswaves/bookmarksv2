
// Helper functions used throughout our app!
export const helpersCtrl = {
    // Handles commas
    commanator: (index, arrayLength) => {
        let curr = index + 1
        if ((curr >= arrayLength)) {
            return '';
        } else {
            return ', '
        }
    }
}