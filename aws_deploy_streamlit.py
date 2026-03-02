#!/usr/bin/env python3
"""
Reusable EC2 deployment script for Streamlit dashboards.
Creates security group, launches instance, assigns Elastic IP.

Usage:
    python aws_deploy_streamlit.py --name stock-dashboard --key-name my-key
    python aws_deploy_streamlit.py --name stock-dashboard --key-name my-key --instance-type t3.small --storage 30

Requirements:
    pip install boto3
    aws configure  # one-time setup with your credentials
"""
import argparse
import json
import sys
import time
import urllib.request

import boto3
from botocore.exceptions import ClientError

# AMI IDs for Ubuntu 22.04 LTS by region (as of 2024)
UBUNTU_AMIS = {
    "us-east-1": "ami-0c7217cdde317cfec",
    "us-east-2": "ami-05fb0b8c1424f266b",
    "us-west-1": "ami-0ce2cb35386fc22e9",
    "us-west-2": "ami-008fe2fc65df48dac",
    "eu-west-1": "ami-0905a3c97561e0b69",
    "eu-central-1": "ami-0faab6bdbac9486fb",
    "ap-southeast-1": "ami-078c1149d8ad719a7",
    "ap-northeast-1": "ami-0d52744d6551d851e",
}

SECURITY_GROUP_NAME = "streamlit-apps"


def get_my_ip():
    """Get current public IP address for SSH access."""
    try:
        with urllib.request.urlopen("https://checkip.amazonaws.com", timeout=5) as response:
            return response.read().decode("utf-8").strip()
    except Exception:
        print("Warning: Could not determine your IP. SSH will be open to 0.0.0.0/0")
        return None


def get_or_create_security_group(ec2_client, ec2_resource, my_ip):
    """Create security group if it doesn't exist, return its ID."""
    try:
        # Check if security group exists
        response = ec2_client.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": [SECURITY_GROUP_NAME]}]
        )
        if response["SecurityGroups"]:
            sg_id = response["SecurityGroups"][0]["GroupId"]
            print(f"Using existing security group: {sg_id}")
            return sg_id
    except ClientError:
        pass

    # Create new security group
    print(f"Creating security group: {SECURITY_GROUP_NAME}")
    try:
        response = ec2_client.create_security_group(
            GroupName=SECURITY_GROUP_NAME,
            Description="Security group for Streamlit web applications",
        )
        sg_id = response["GroupId"]
    except ClientError as e:
        if "already exists" in str(e):
            response = ec2_client.describe_security_groups(
                Filters=[{"Name": "group-name", "Values": [SECURITY_GROUP_NAME]}]
            )
            sg_id = response["SecurityGroups"][0]["GroupId"]
            print(f"Security group already exists: {sg_id}")
            return sg_id
        raise

    # Add inbound rules
    security_group = ec2_resource.SecurityGroup(sg_id)

    # SSH access
    ssh_cidr = f"{my_ip}/32" if my_ip else "0.0.0.0/0"
    ingress_rules = [
        {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "IpRanges": [{"CidrIp": ssh_cidr, "Description": "SSH access"}],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80,
            "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "HTTP"}],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 443,
            "ToPort": 443,
            "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "HTTPS"}],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 8501,
            "ToPort": 8501,
            "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "Streamlit"}],
        },
    ]

    for rule in ingress_rules:
        try:
            security_group.authorize_ingress(IpPermissions=[rule])
            print(f"  Added rule: port {rule['FromPort']}")
        except ClientError as e:
            if "already exists" not in str(e):
                print(f"  Warning: Could not add rule for port {rule['FromPort']}: {e}")

    print(f"Created security group: {sg_id}")
    return sg_id


def launch_instance(ec2_resource, name, instance_type, key_name, sg_id, storage, ami):
    """Launch EC2 instance with specified configuration."""
    print(f"Launching EC2 instance...")
    print(f"  AMI: {ami}")
    print(f"  Type: {instance_type}")
    print(f"  Storage: {storage} GB")

    instances = ec2_resource.create_instances(
        ImageId=ami,
        InstanceType=instance_type,
        KeyName=key_name,
        SecurityGroupIds=[sg_id],
        MinCount=1,
        MaxCount=1,
        BlockDeviceMappings=[
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "VolumeSize": storage,
                    "VolumeType": "gp3",
                    "DeleteOnTermination": True,
                },
            }
        ],
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": name},
                    {"Key": "Application", "Value": "streamlit"},
                ],
            }
        ],
    )

    instance = instances[0]
    print(f"Instance created: {instance.id}")
    print("Waiting for instance to be running...")

    instance.wait_until_running()
    instance.reload()

    print(f"Instance is running!")
    return instance


def allocate_elastic_ip(ec2_client, instance_id):
    """Allocate and associate Elastic IP."""
    print("Allocating Elastic IP...")

    # Allocate new Elastic IP
    allocation = ec2_client.allocate_address(Domain="vpc")
    allocation_id = allocation["AllocationId"]
    elastic_ip = allocation["PublicIp"]

    print(f"Allocated Elastic IP: {elastic_ip}")

    # Associate with instance
    ec2_client.associate_address(
        AllocationId=allocation_id,
        InstanceId=instance_id,
    )

    print(f"Associated Elastic IP with instance")
    return elastic_ip, allocation_id


def main():
    parser = argparse.ArgumentParser(
        description="Deploy EC2 instance for Streamlit dashboard"
    )
    parser.add_argument(
        "--name", required=True, help="App name (used for tagging and output file)"
    )
    parser.add_argument(
        "--key-name", required=True, help="Existing EC2 key pair name"
    )
    parser.add_argument(
        "--instance-type", default="t3.small", help="EC2 instance type (default: t3.small)"
    )
    parser.add_argument(
        "--storage", type=int, default=30, help="EBS volume size in GB (default: 30)"
    )
    parser.add_argument(
        "--region", default="us-east-1", help="AWS region (default: us-east-1)"
    )

    args = parser.parse_args()

    # Validate region
    if args.region not in UBUNTU_AMIS:
        print(f"Error: Region '{args.region}' not supported.")
        print(f"Supported regions: {', '.join(UBUNTU_AMIS.keys())}")
        sys.exit(1)

    ami = UBUNTU_AMIS[args.region]

    # Initialize boto3 clients
    print(f"Connecting to AWS ({args.region})...")
    ec2_client = boto3.client("ec2", region_name=args.region)
    ec2_resource = boto3.resource("ec2", region_name=args.region)

    # Verify key pair exists
    try:
        ec2_client.describe_key_pairs(KeyNames=[args.key_name])
    except ClientError:
        print(f"Error: Key pair '{args.key_name}' not found in region {args.region}")
        print("Create a key pair in the AWS Console or use:")
        print(f"  aws ec2 create-key-pair --key-name {args.key_name} --query 'KeyMaterial' --output text > {args.key_name}.pem")
        sys.exit(1)

    # Get current IP for SSH rule
    my_ip = get_my_ip()
    if my_ip:
        print(f"Your IP address: {my_ip}")

    # Create or get security group
    sg_id = get_or_create_security_group(ec2_client, ec2_resource, my_ip)

    # Launch instance
    instance = launch_instance(
        ec2_resource,
        args.name,
        args.instance_type,
        args.key_name,
        sg_id,
        args.storage,
        ami,
    )

    # Allocate Elastic IP
    elastic_ip, allocation_id = allocate_elastic_ip(ec2_client, instance.id)

    # Prepare output
    output = {
        "name": args.name,
        "instance_id": instance.id,
        "elastic_ip": elastic_ip,
        "allocation_id": allocation_id,
        "security_group_id": sg_id,
        "region": args.region,
        "instance_type": args.instance_type,
        "ssh_command": f"ssh -i {args.key_name}.pem ubuntu@{elastic_ip}",
        "next_steps": [
            f"1. SSH into instance: ssh -i {args.key_name}.pem ubuntu@{elastic_ip}",
            "2. Clone your repository: git clone https://github.com/YOUR_USERNAME/options_dashboard.git",
            "3. Run setup script: cd options_dashboard && bash ec2_setup.sh",
            "4. Set up domain at https://www.duckdns.org",
            "5. Install SSL: sudo apt install certbot python3-certbot-nginx -y && sudo certbot --nginx -d yourdomain.duckdns.org",
        ],
    }

    # Save to JSON file
    output_file = f"{args.name}_ec2_info.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("DEPLOYMENT SUCCESSFUL")
    print("=" * 60)
    print(f"Instance ID:    {instance.id}")
    print(f"Elastic IP:     {elastic_ip}")
    print(f"Security Group: {sg_id}")
    print(f"Region:         {args.region}")
    print("")
    print("SSH Command:")
    print(f"  ssh -i {args.key_name}.pem ubuntu@{elastic_ip}")
    print("")
    print("Quick Access URLs (after setup):")
    print(f"  http://{elastic_ip}:8501  (direct Streamlit)")
    print(f"  http://{elastic_ip}       (after nginx setup)")
    print("")
    print("Next Steps:")
    for step in output["next_steps"]:
        print(f"  {step}")
    print("")
    print(f"Instance details saved to: {output_file}")
    print("")
    print("To terminate this instance later:")
    print(f"  aws ec2 terminate-instances --instance-ids {instance.id}")
    print(f"  aws ec2 release-address --allocation-id {allocation_id}")


if __name__ == "__main__":
    main()
