# bookmarksv2
CASHMONEYKYLE

RUNNING A LOCAL PROTOTYPE OF APP:
  1) For backend, you need to activate your local env with conda.
     from project root dir $ conda activate bookmarks
  2) For backend, you need to activate fastapi
    from project root dir $ uvicorn main:app --reload
  3) For front end, you need to run a dev server for vue/vite
    cd into bookmarks-frontend/ and run this command $ npm run dev
  4) now you should be able to use app / develop and test locally.

FOR TESTING API:
  make sure you have the dependencies
    inside your conda env run:
      pip install 'fastapi[all]'
      pip install neo4j==5.8.1

  1) Load the thang up with
    from project root dir $ uvicorn main:app --reload
  2) Then go to:
    'http://127.0.0.1:8000/docs#/'

  You can now test all your saucey endpoints to see how things work.

TESTING QUERIES:
  Kyle can you help fill this out for documentation?
