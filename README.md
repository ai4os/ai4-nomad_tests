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
* Before being able to run the tests you should provide an EGI token:
  ```bash
  export TMP_EGI_TOKEN="$(oidc-token egi-checkin)"
  ```
  See [PAPI docs](https://github.com/ai4os/ai4-papi#generating-a-valid-refresh-token)
  in order know how to generate an EGI token.


Once this is ready, you can install the tests suite with:
```bash
python -m venv --system-site-packages myenv
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
