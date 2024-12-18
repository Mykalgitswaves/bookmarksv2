CLUB_REVIEW_CONSTRAIN_INDEX = (
    """
CREATE CONSTRAINT unique_clubreview
IF NOT EXISTS
FOR (r:ClubReview)
REQUIRE (r.user_id, r.book_club_book_id) IS UNIQUE;
    """
)