
/**
    user (dict): A user object containing the following fields:
        id (str): The id of the user
    chapter (int): The chapter that the update is posted for
    response (str | None): The response that was created with the update
    headline (str): The headline for the post
    quote (str): The quote to include with the post
*/

export function formatUpdateForBookClub(updateBlob, user_id) {
    let payload = Object.create(null);

    payload.user = { id: user_id} ;
    payload.chapter = updateBlob.chapter;
    payload.response = updateBlob.response;
    payload.headline = updateBlob.headline;
    payload.quote = updateBlob.quote;

    return payload;
}