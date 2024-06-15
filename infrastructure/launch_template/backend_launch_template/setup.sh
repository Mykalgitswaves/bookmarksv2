#!/bin/bash

cd /data/bookmarksv2

eval "$(ssh-agent -s)"

ssh-add /root/.ssh/id_rsa

git pull -r

systemctl restart book.service

sleep 40

source /data/book_env/bin/activate

cd /data/bookmarksv2/backend/tests

pytest
if [ $? -ne 0 ]; then
    echo "Tests failed, stopping the deployment."
    exit 1
fi

touch /data/bookmarksv2/backend/health