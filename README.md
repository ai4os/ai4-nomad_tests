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

* You need to have the [appropriate certs](https://github.com/ai4os/ai4-papi#installation) to connect to the Nomad cluster
* Before being able to run the tests you should provide an EGI token:
```bash
export TMP_EGI_TOKEN="$(oidc-token egi-checkin)"
```
See [PAPI docs](https://github.com/ai4os/ai4-papi#generating-a-valid-refresh-token) in
order know how to generate an EGI token.


Once this is ready run:
```bash
pip install -e .
```

## Usage

You can test a whole datacenter:
```bash
python main.py --datacenter ifca-ai4eosc
```
or individual nodes:
```bash
python main.py --nodes ifca-node-gpu-1 ifca-node-gpu-2
```
<!-- todo: replace with entrypoint command -->

> Sometimes the test `node.cpu.deployment` fails the first time you run it.
> This is due to the fact that, the first time you run it, the docker image of module
> has to be pulled to the node. Although we sleep about 1 min to account for this fact,
> this is sometimes not enough.
> So in case of doubt, run the tests a second time and you should be fine.
