#!/bin/bash

# Redirecting output to log file
exec > >(tee -i cl_st1_ph5_eyamrog.log)
exec 2>&1

# Usage: ubuntu@<IP address>:~/work/cl_st1_eyamrog$ nohup bash cl_st1_ph5_eyamrog.sh &

stop_instance() {
  # Do not forget to:
  # - have 'aws-cli' installed on the EC2 instance
  # - have the IAM role 'S3-Admin-Access' attached to the EC2 instance

  instance_id=$(aws ec2 describe-instances --filters "Name=private-dns-name,Values=$(hostname --fqdn)" --query "Reservations[*].Instances[*].InstanceId" --output text)
  aws ec2 stop-instances --instance-ids "$instance_id"
  echo "Instance $instance_id stopped."
}

# Activating the Python virtual environment
source "$HOME"/my_env/bin/activate || { echo "Failed to activate the virtual environment"; exit 1; }

# Running the 'cl_st1_ph5_eyamrog.py' programme
python cl_st1_ph5_eyamrog.py cl_st1_ph5_eyamrog cl_st1_ph5_eyamrog || { echo "Python programme failed"; exit 1; }

# Stopping the EC2 instance
stop_instance
