BOOKCLUBS_INDEX = (
"""
Create FULLTEXT INDEX bookclubsFullText
for (n:BookClub)
on each [n.name, n.description]    
"""
)

BOOKSHELVES_INDEX = (
"""
Create FULLTEXT INDEX bookshelvesFullText
for (n:Bookshelf)
on each [n.title, n.description]    
"""
)

MAKE_AWARDS = (
    """
    CREATE (:ClubAward {
        name: "Dunce cap",
        description: "Granted after a series of unfortunate takes.",
        id: "award_" + randomUUID(),
        type: "Questionable"
    })
    
    CREATE (:ClubAward {
        name: "Strange hill to die on",
        description: "Granted to a post that takes an \"interesting\" stance.",
        id: "award_" + randomUUID(),
        type: "Questionable"
    })
    
    CREATE (:ClubAward {
        name: "Definitely didn't read it",
        description: "You read something, not this book, but something...",
        id: "award_" + randomUUID(),
        type: "Questionable"
    })
    
    CREATE (:ClubAward {
        name: "Nice gippity",
        description: "Something about this feels... generated (respectfully).",
        id: "award_" + randomUUID(),
        type: "Questionable"
    })
    
    CREATE (:ClubAward {
        name: "Doubt",
        description: "Calling this into question",
        id: "award_" + randomUUID(),
        type: "Questionable"
    })
    
    CREATE (:ClubAward {
        name: "Hot take",
        description: "Controversial, but brave.",
        id: "award_" + randomUUID(),
        type: "Commendable"
    })
    
    CREATE (:ClubAward {
        name: "Facts",
        description: "Not a lie in sight. Granted to takes you agree with.",
        id: "award_" + randomUUID(),
        type: "Commendable"
    })
    
    CREATE (:ClubAward {
        name: "100",
        description: "100%, granted to takes you agree with.",
        id: "award_" + randomUUID(),
        type: "Commendable"
    })
"""
)