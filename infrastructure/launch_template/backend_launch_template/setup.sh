#!/bin/bash

cd /data/bookmarksv2

git pull -r

systemctl restart book.service

sleep 20

source /data/book_env/bin/activate

cd /data/bookmarksv2/backend/tests

pytest
if [ $? -ne 0 ]; then
    echo "Tests failed, stopping the deployment."
    exit 1
fi

touch /data/bookmarksv2/backend/health