# Nomad tests

These scripts test that a given set of Nomad nodes are correctly configured
for the project requirements.

The tests are useful for checking:
* when a given actor adds their resources to the existing Nomad cluster.
* whether everyone in the cluster has applied Ansible role updates.
* check is jobs can be still deployed because some resource usage (eg. disk)
  is not monitor by Nomad
* test that newly develop Ansible roles do not break the expected functionality of the
  Nomad cluster

## Requirements

* You need to have the [appropriate certs](https://github.com/ai4os/ai4-papi#installation)
  to connect to the Nomad cluster

* [Install Nomad](https://developer.hashicorp.com/nomad/docs/install) (this is needed to be able to update the node metadata, which is not supported in the `python-nomad` package)

* Install the Python package:

  ```bash
  python3 -m venv --system-site-packages myenv
  source myenv/bin/activate
  pip install -e .
  deactivate
  ```

## Usage

You can test:

* the whole cluster:
  ```bash
  ai4-nomad-tests --cluster
  ```

* a single datacenter:
  ```bash
  ai4-nomad-tests --datacenter ifca-ai4eosc
  ```

* a list of individual nodes:
  ```bash
  ai4-nomad-tests --nodes ifca-node-gpu-1 --nodes ifca-node-gpu-2
  ```

> 💡 **Tip**: Periodic testing
>
> You can schedule a cronjob that executes periodically the tests in the whole cluster
> and automatically mark the nodes that fail to pass the tests as _ineligible_, to avoid
> having jobs landing there (and failing). For this use the
> [`monitoring-cluster.sh`](./monitor-cluster.sh) script.
>
> Once the admin responsible for that Nomad nodes fixes the issues, node can be
> manually marked again as _eligible_ in the Nomad UI.

## Implementation notes

* GPU deployment testing is using a Nomad job that doesn't ask for GPUs. This Nomad job
  is mainly intended to check that the Traefik endpoints of that node work fine.
  We don't test with a GPU job because GPUs are a scarce resource so the deployment
  could fail because no GPUs are available, not because malfunctioning.

  To find any GPU misconfigurations without actually making a GPU deployment, we try
  to catch as many error as possible parsing the node metadata (cf.
  [`gpu.node_info()`](./ai4_nomad_tests/tests/node/gpu.py)).
  This is not perfect but it catches most GPU errors (eg. device not available).
