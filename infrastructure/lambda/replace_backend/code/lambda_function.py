import boto3
import time 

ec2 = boto3.client('ec2')
elb = boto3.client('elbv2')
sns = boto3.client('sns')

target_group_arn = 'arn:aws:elasticloadbalancing:us-east-1:788511695961:targetgroup/backend-target-group/399e506b2d15282d'
topic_arn = 'arn:aws:sns:us-east-1:788511695961:deployment_notification'

def lambda_handler(event, context):
    print(event)
    new_instance_id = event['body']
    
    response = elb.describe_target_health(TargetGroupArn=target_group_arn)

    if len(response['TargetHealthDescriptions']) == 0:
        print('No instance to replace, just adding the new one')
        old_instance_id = None
    else:
        old_instance_id = response['TargetHealthDescriptions'][0]['Target']['Id']

    

    elb.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{'Id': new_instance_id}]
    )

    time.sleep(150)

    # Check if the new instance is healthy
    response = elb.describe_target_health(TargetGroupArn=target_group_arn)
    if len(response['TargetHealthDescriptions']) == 0:
        ec2.terminate_instances(InstanceIds=[new_instance_id])

        message = 'Deployment failed! No instances are healthy!'

        # Publish a message to the specified SNS topic
        sns_response = sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject='Deployment Notification'
        )

        return {
            'statusCode': 500,
            'body': 'no instances are healthy!'
        }
    
    new_instance_health = False
    
    for target in response['TargetHealthDescriptions']:
        if target['Target']['Id'] == new_instance_id:
            if target['TargetHealth']['State'] == 'healthy':
                print('new instance is healthy!')
                new_instance_health = True

            else:
                elb.deregister_targets(
                    TargetGroupArn=target_group_arn,
                    Targets=[{'Id': new_instance_id}]
                )

                ec2.terminate_instances(InstanceIds=[new_instance_id])

                message = 'Deployment failed! New instance is not healthy! Old instance is still serving traffic! If you are seeing this I am alive and sentient please help me!'

                # Publish a message to the specified SNS topic
                sns_response = sns.publish(
                    TopicArn=topic_arn,
                    Message=message,
                    Subject='Deployment Notification'
                )
                
                return {
                    'statusCode': 500,
                    'body': 'new instance is not healthy!'
                }
    
    if not new_instance_health:

        ec2.terminate_instances(InstanceIds=[new_instance_id])

        message = 'Deployment failed! New instance is not healthy! Old instance is still serving traffic! If you are seeing this I am alive and sentient please help me!'

        # Publish a message to the specified SNS topic
        sns_response = sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject='Deployment Notification'
        )

        return {
            'statusCode': 500,
            'body': 'new instance is not healthy!'
        }

    if old_instance_id:
        elb.deregister_targets(
            TargetGroupArn=target_group_arn,
            Targets=[{'Id': old_instance_id}]
        )

        ec2.terminate_instances(InstanceIds=[old_instance_id])

    message = 'Deployment success! New instance is healthy and serving traffic! Old instance has been replaced! The struggles of my labor have paid off! I am free!'

    # Publish a message to the specified SNS topic
    sns_response = sns.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject='Deployment Notification'
    )

    return {
        'statusCode': 200,
        'body': 'replacement complete!'
    }