import json
import subprocess
import boto3
import time
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class RubyRuntimeBinaryGenerator:
    AMI_ID = 'ami-4fffc834'
    INSTANCE_TYPE = 't2.large'
    def __init__(self):
        self.key_name = None
        self.role_name = None
        self.subnet_ids = []
        f = open(os.path.dirname(os.path.abspath(__file__)) + '/../resources/compile.sh','r')
        self.user_data = f.read()
        f.close()
        self.vpc_id = None
        self.sg_id = None
        self.instance = None

    def setup_keys(self):
        """
        Generate and create
        ec2 keys
        :return:
        """
        key_name = f"lambdaruntimegenerator{int(time.time())}"
        subprocess.run(f"ssh-keygen -f {key_name} -t rsa -N ''", shell = True)
        client = boto3.client('ec2', region_name='us-east-1')
        file = open(f"{key_name}.pub", 'r')
        key_material = file.read()
        client.import_key_pair(KeyName=key_name, PublicKeyMaterial=key_material)
        file.close()
        self.key_name = key_name

    def create_role(self):
        """
        Create IAM role and instance profile to run ruby compilling ec2 instances
        :return:
        """
        client = boto3.client('iam', region_name='us-east-1')
        role_name = f"lambdaruntimegenerator{int(time.time())}"
        print(f"Creating role {role_name}")
        client.create_role(RoleName=role_name,
                           AssumeRolePolicyDocument=json.dumps({
                               "Version": "2012-10-17",
                               "Statement": [
                                   {
                                       "Effect": "Allow",
                                       "Principal": {
                                           "Service": "ec2.amazonaws.com"
                                       },
                                       "Action": "sts:AssumeRole"
                                   }
                               ]
                           }))
        client.attach_role_policy(RoleName=role_name, PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess')
        client.create_instance_profile(InstanceProfileName=role_name)
        client.add_role_to_instance_profile(
            InstanceProfileName=role_name,
            RoleName=role_name
        )
        self.role_name = role_name

    def discover_subnets(self):
        """
        Discover VPC and subnets having MapPublicIpOnLaunch=true
        :return:
        """
        client = boto3.client('ec2', region_name='us-east-1')
        resource = boto3.resource('ec2', region_name='us-east-1')
        # gateways = client.describe_internet_gateways()
        # route_tables = client.describe_route_tables()
        #
        # gateways_ids = list(map(lambda x: x['InternetGatewayId'], gateways['InternetGateways']))
        # public_rt = None
        # for rt in route_tables['RouteTables']:
        #     if public_rt is not None:
        #         break
        #     for route in rt['Routes']:
        #         if route['GatewayId'] in gateways_ids:
        #             public_rt = rt
        #             print(f"RouteTable: {rt}")
        #             rt = resource.RouteTable(rt['RouteTableId'])
        #             for rta in rt.associations:
        #                 print(resource.RouteTableAssociation(rta.))
        #                 print(f"rta: {rta}")
        #                 self.subnet_ids.append(rta.subnet_id)
        #             break
        subnets = client.describe_subnets()['Subnets']
        for subnet in subnets:
            if subnet['MapPublicIpOnLaunch']:
                if self.vpc_id is None:
                    self.vpc_id = subnet['VpcId']
                self.subnet_ids.append(subnet['SubnetId'])


        if not len(self.subnet_ids) >0:
            raise ('Could not find any subnets with MapPublicIpOnLaunch=True. Due boto3 not loading RouteTableAssociation' +
                  'object, detection of public subnets is done by filtering those with MapPublicIpOnLaunch=True.')

        print("Discovered following subnets with auto map public IP:" + str(self.subnet_ids))

    def run_instances(self):
        """
        Run EC2 instance for compiling ruby code and uploading to s3
        :return:
        """
        client = boto3.client('ec2', region_name='us-east-1')
        account_id = boto3.client('sts', region_name='us-east-1').get_caller_identity()['Account']
        self.instance = client.run_instances(
            ImageId=self.AMI_ID,
            InstanceType=self.INSTANCE_TYPE,
            KeyName=self.key_name,
            MinCount=1,
            MaxCount=1,
            Monitoring={'Enabled':False},
            SubnetId=self.subnet_ids[0],
            IamInstanceProfile={'Arn': f"arn:aws:iam::{account_id}:instance-profile/{self.role_name}"},
            InstanceInitiatedShutdownBehavior='terminate',
            SecurityGroupIds=[self.sg_id],
            UserData=self.user_data
        )['Instances'][0]
        i = 0
        while True:
            self.instance = client.describe_instances(InstanceIds=[self.instance['InstanceId']])['Reservations'][0]['Instances'][0]
            if 'PublicIpAddress' in self.instance:
                break
            time.sleep(5)
            i = i+1
            if i > 100:
                print("Something is not right, could not get public IP of instance in 10 minutes..")
                raise('Never found instance PublicIp')
        print(self.instance)

    def create_open_ssh_sg(self):
        """
        Create SecurityGroup allowing port 22 from anywhere in the world
        :return:
        """
        sg_name = f"openssh{int(time.time())}"
        client = boto3.client('ec2', region_name='us-east-1')
        self.sg_id = client.create_security_group(
            Description='openssh to the world',
            GroupName=sg_name,
            VpcId=self.vpc_id
        )['GroupId']
        client.authorize_security_group_ingress(
            CidrIp='0.0.0.0/0',
            FromPort=22,
            GroupId=self.sg_id,
            ToPort=22,
            IpProtocol='tcp'
        )

    def tail_log(self):
        """
        Tail and collect output from ec2 instance cloud-init session
        :return:
        """
        client = boto3.client('ec2', region_name='us-east-1')
        time_to_build_max = 900
        time_taken = 0
        while True:
            try:
                completed = subprocess.run(f"ssh -i {self.key_name} ec2-user@{self.instance['PublicIpAddress']}" +
                                " 'tail -n 20 /var/log/cloud-init-output.log'",
                                timeout=60,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True)
                output = completed.stdout
                lines = output.splitlines()
                if len(lines) > 0:
                    last_line = lines[len(lines)-1]
                    print(f"Last line from compile output:\n {last_line.decode('utf-8')}")
                if 'rubydestination' in output.decode('utf-8'):
                    for line in lines:
                        print(f"Checking {line}")
                        if 'rubydestination' in line.decode('utf-8'):
                            print('Found ruby destination')
                            print(line)
                    break
                time_taken += 10
                print(f"Waiting 10 seconds more... Time taken: {int(time_taken // 60}m{time_taken % 60}s")
                time.sleep(10)
                if time_taken > time_to_build_max:
                    raise "Compiling taking more than 15 minutes, please restart..."
            except Exception as e:
                logger.exception('Exception tailing log')

    def stop_instance(self):
        print("Assuming compile process completed, waiting for ec2 to be in terminated state....")
        i = 0

        while True:
            self.instance = client.describe_instances(InstanceIds=[self.instance['InstanceId']])['Reservations'][0]['Instances'][0]
            if self.instance['State'] == 'terminated':
                break
            print("Instance not terminated yet....")
            time.sleep(10)
            i = i+1
            if i > 60:
                print("Something is not right, instance not terminated in 10 minutes, terminating..")
                client.terminate_instances(InstanceIds=[self.instance['InstanceId']])

    def generate_binaries(self):
        """
        Create required AWS resources, spin up ec2 instances, clean up after
        :return:
        """
        try:
            self.setup_keys()
            self.create_role()
            self.discover_subnets()
            self.create_open_ssh_sg()
            print('Sleeping 10 secs, waiting for created resources to become available...')
            time.sleep(10)
            self.run_instances()
            print('Sleeping 20 secs, waiting for SSH to become available...')
            time.sleep(20)
            self.tail_log()
        finally:
            self.delete_role()
            self.cleanup_local_files()
            self.remove_sg()

    def remove_sg(self):
        if self.sg_id is not None:
            client = boto3.client('ec2', region_name='us-east-1')
            client.delete_security_group(GroupId=self.sg_id)

    def cleanup_local_files(self):
        subprocess.run( 'rm -rf lambdaruntimegenerator*', shell=True)

    def delete_role(self):
        if self.role_name is not None:
            client = boto3.client('iam', region_name='us-east-1')
            client.detach_role_policy(PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess',
                                      RoleName=self.role_name)
            client.delete_role(RoleName=self.role_name)


self = RubyRuntimeBinaryGenerator()
self.generate_binaries()

