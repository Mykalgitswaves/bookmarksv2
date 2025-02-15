#!/bin/bash

cd /home/ubuntu/bookmarksv2

eval "$(ssh-agent -s)"

git pull -r

aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:788511695961:secret:prod/config_prod-438QTR --query 'SecretString' --region 'us-east-1' --output text > /home/ubuntu/bookmarksv2/backend/src/config/config.prod.json
aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:788511695961:secret:prod/config_prod-438QTR --query 'SecretString' --region 'us-east-1' --output text > /home/ubuntu/bookmarksv2/backend/tests/config.json

systemctl restart book.service

sleep 40

cd /home/ubuntu/bookmarksv2/backend/tests

pytest
# if [ $? -ne 0 ]; then
#     echo "Tests failed, stopping the deployment."
#     exit 1
# fi

touch /home/ubuntu/bookmarksv2/backend/health

systemctl restart book.service