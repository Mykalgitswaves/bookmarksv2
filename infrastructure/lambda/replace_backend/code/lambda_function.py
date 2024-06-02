import boto3
import time 

ec2 = boto3.client('ec2')
elb = boto3.client('elbv2')

target_group_arn = 'arn:aws:elasticloadbalancing:us-east-1:788511695961:targetgroup/backend-target-group/4f0e31fe3e1b28be'

def lambda_handler(event, context):
    print(event)
    new_instance_id = event['body']
    
    response = elb.describe_target_health(TargetGroupArn=target_group_arn)

    if len(response['TargetHealthDescriptions']) == 0:
        print('No instance to replace, just adding the new one')
    else:
        old_instance_id = response['TargetHealthDescriptions'][0]['Target']['Id']

    

    elb.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{'Id': new_instance_id}]
    )

    time.sleep(30)

    # Check if the new instance is healthy
    response = elb.describe_target_health(TargetGroupArn=target_group_arn)
    if len(response['TargetHealthDescriptions']) == 0:
        return {
            'statusCode': 500,
            'body': 'no instances are healthy!'
        }
    
    for target in response['TargetHealthDescriptions']:
        if target['Target']['Id'] == new_instance_id and target['TargetHealth']['State'] == 'healthy':
            break
        else:
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

    return {
        'statusCode': 200,
        'body': 'replacement complete!'
    }