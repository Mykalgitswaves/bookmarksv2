import boto3

launch_template_id = 'lt-015a761f26cefb08e'
event_name = 'TriggerStepFunctionAt5AM_EST'

ec2 = boto3.client('ec2')
events_client = boto3.client('events')

def lambda_handler(event, context):
    response = events_client.disable_rule(
        Name=event_name
    )

    response = ec2.run_instances(
        LaunchTemplate={'LaunchTemplateId': launch_template_id},
        MinCount=1,
        MaxCount=1
    )

    new_instance_id = response['Instances'][0]['InstanceId']

    return {
        'statusCode': 200,
        'body': new_instance_id
    }