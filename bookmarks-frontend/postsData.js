export const postData = {
    "posts": { 
        "review": {
                    "custom": [
                        {   
                            "id": -1,
                            "q": '',
                            "response": '',
                            "is_spoiler": false,
                            "placeholder": "Add your own question here...",
                            "isHiddenCustomQuestion": false
                        }
                    ],
                    // "all": [
                    //     {
                    //         "id": 1,
                    //         "q" :"what is this book about?",
                    //         "response": '',
                    //         "is_spoiler": false,
                    //     },
                    //     {
                    //         "id": 2,
                    //         "q" :"what do you like about this book?",
                    //         "response": '',
                    //         "is_spoiler": false,
                    //     },
                    // ],
                    "character": [
                        { 
                            "id": 3,
                            "q": "Which character in the book did you most relate to and why?",
                            "response": "",
                            "is_spoiler": false
                        },
                        {
                            "id": 4, 
                            "q": "Did you find the protagonist's character arc satisfying or lacking? Why?",  
                            "response": "",
                            "is_spoiler": false
                        },
                        {
                            "id": 5,
                            "q": "Which relationships between characters stood out to you the most?",
                            "response": "",
                            "is_spoiler": false
                        }
                    ],                
                    "plot": [
                        { 
                            "id": 7,
                            "q": "Did you find the overall plot predictable or surprising? Why?",
                            "response": "",
                            "is_spoiler": false
                          },
                          { 
                            "id": 8,
                            "q": "Were you satisfied with how the various storylines and loose ends were resolved by the end?",
                            "response": "", 
                            "is_spoiler": false
                          },
                          {
                            "id": 9,
                            "q": "Which plot twists stood out to you the most? Did you see them coming?",
                            "response": "",
                            "is_spoiler": false
                          }
                    ],
                    "tone": [
                        {  
                            "id": 10,
                            "q": "Did you find the overall tone of the book satisfying? Why or why not?",
                            "response": "",
                            "is_spoiler": false
                          },
                          { 
                            "id": 11, 
                            "q": "How would you describe the tone and atmosphere of the key settings in the book?",
                            "response": "",
                            "is_spoiler": false
                          },
                          {
                            "id": 12,
                            "q": "Were there any shifts in tone that stood out to you? If so, what purpose did they serve?",
                            "response": "",
                            "is_spoiler": false
                          }
                    ],
                    "conflict": [
                        {
                            "id": 10,
                            "q": "What was the central conflict in the book?",
                            "response": "",
                            "is_spoiler": false
                        }
                    ]
        },
        "update": {},
        "comparison": [
            {
                "topic": "tone", 
                "pk": 13,
                "q": "The tone of these works..."
            },
            {
                "topic": "character", 
                "pk": 14,
                "q": "The character of these works..."
            },
            {
                "topic": "plot", 
                "pk": 15,
                "q": "The plot of these works..."
            },
            {
                "topic": "setting", 
                "pk": 16,
                "q": "The setting of these works..."
            },
            {
                "topic": "custom", 
                "pk": -1,
                "q": ""
            }
        ]
    },
}

