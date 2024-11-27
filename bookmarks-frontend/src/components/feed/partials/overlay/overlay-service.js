export function showOverlay (templateRef) {
    const { dialogRef } = templateRef;
    dialogRef.showModal();
}

export function hideOverlay(templateRef) {
    const { dialogRef } = templateRef;
    dialogRef.close();
    
}