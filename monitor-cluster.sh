#!/bin/bash

# Automated script to test the cluster.
# We run as a cronjob on Sundays:
# 0 0 * * 7 /bin/bash /home/ubuntu/ai4-nomad_tests/monitor-cluster.sh

# Export proper Nomad variables
export NOMAD_ADDR=https://193.146.75.205:4646  # federated cluster cluster
export NOMAD_CACERT=/home/ubuntu/nomad-certs/nomad-federated/nomad-ca.pem
export NOMAD_CLIENT_CERT=/home/ubuntu/nomad-certs/nomad-federated/cli.pem
export NOMAD_CLIENT_KEY=/home/ubuntu/nomad-certs/nomad-federated/cli-key.pem
export NOMAD_TLS_SERVER_NAME=node-ifca-0

# Move to main directory (where this script is located)
cd $(dirname "$0")

# Redirect all output to a log file with date/time stamp
exec 1> >(tee "monitor-cluster.log")
exec 2>&1

# Pull to always run the latest tests
git pull


# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/ubuntu/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/ubuntu/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/ubuntu/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/ubuntu/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# Run .py script
conda activate ai4-nomad-tests
ai4-nomad-tests --cluster
conda deactivate
