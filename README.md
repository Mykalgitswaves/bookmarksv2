# bookmarksv2
CASHMONEYKYLE

DEPENDENCIES: 
  
    $ pip install "python-jose[cryptography]"
    $ pip install "passlib[bcrypt]"
RUNNING A LOCAL PROTOTYPE OF APP:
  1) For backend, you need to activate your local env with conda.
     from project root dir 
        
        
         $ conda activate bookmarks
  2) For backend, you need to activate fastapi
    from project backend dir 
        
         $ uvicorn src.main:backend_app —reload
  3) For front end, you need to run a dev server for vue/vite
    cd into bookmarks-frontend/ and run this command 
        
         $ npm run dev
  4) now you should be able to use app / develop and test locally.

TESTING ROUTES:

To test new routes with pytest:

1) Open a terminal, activate the conda environment

        $ conda activate bookmarks

2) Start the backend

        $ uvicorn src.main:backend_app —reload

3) Open a new terminal, activate the conda environment

        $ conda activate bookmarks

4) Navigate to the test directory
        
        $ cd backend/tests

5) To run all tests, simply type pytest

        $ pytest

6) To run a single test, choose the name of your test
        
        $ pytest test_book_clubs.py

7) If you want to see print statement even when tests pass, add the -s flag

        $ pytest test_book_clubs.py -s
