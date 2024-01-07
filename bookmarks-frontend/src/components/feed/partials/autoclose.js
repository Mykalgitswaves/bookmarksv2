// This looks at a function and determines whether a user clicked inside of the ref element. Called only when element exists.
function clickedInsideElement(
    clientX, clientY, xStartingPoint,
    xEndingPoint, yStartingPoint, yBottomPoint,
) {
    if(clientX >= xStartingPoint && clientX <= xEndingPoint && clientY >= yStartingPoint && clientY <= yBottomPoint){
        return true
    } else {
        return false
    }
}

let bool;

export function autoCloseElementWithRef(ref, isMenuOpen){
    // if client clicks outside the width and height of a 
    // Specific element then change the second argument to false.
    // We need to know the space the element in question takes up inside the document
    // So if the click event target is greater than the left x and less than the right x (calculated by adding element width to left x?), and less than the height, and greater than the height + the top y point (bottom of element) we can deduce the client clicked inside of the element.
    if(isMenuOpen){
            const menu = ref.value;
            const width = menu.clientWidth;
            const yStartingPoint = menu.offsetTop;
            const xStartingPoint = menu.offsetLeft;
            const yBottomPoint = yStartingPoint + menu.clientHeight
            const xEndingPoint = xStartingPoint + width;
            
            document.addEventListener('click', (e) => {
            let clientX = e.clientX;
            let clientY = e.clientY;
            
            bool = clickedInsideElement(
                clientX, clientY, xStartingPoint, xEndingPoint, yStartingPoint, yBottomPoint
                );
            });
        } else {
            // Remove event listeners after destroy. 
            return;
        }
    return bool;
}