import boto3

launch_template_id = 'lt-015a761f26cefb08e'

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
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