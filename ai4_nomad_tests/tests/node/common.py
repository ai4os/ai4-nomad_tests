"""
Common test to all nodes
"""
from rich import print

from nomad_utils import Nomad


def node_info(
        node_id: str,
        ):

    print('  Running test: [hot_pink3 bold]node.common.node_info[/hot_pink3 bold]')

    n = Nomad.node.get_node(node_id)

    assert n['Status'] == 'ready'

    # Check drivers
    assert n['Drivers']['exec']['Detected'] is True
    assert n['Drivers']['docker']['Detected'] is True
    assert n['Drivers']['raw_exec']['Detected'] is True

    assert n['Attributes']['driver.docker.volumes.enabled']  == 'true'
    assert n['Attributes']['driver.docker.privileged.enabled'] == 'true'

    # Check compute metadata
    compute = ['true', 'false']
    assert 'compute' in n['Meta']
    assert  n['Meta']['compute'] in compute, \
        "Compute metadata incorrect: \n" \
        f"Provided: {n['Meta']['domain']} \n" \
        f"Allowed: {compute}"

    # Check domain metadata
    assert 'domain' in n['Meta']
    assert n['Meta']['domain'], \
        "Domain should not be empty"

    # Check namespace metadata
    namespaces = ['ai4eosc', 'imagine', 'tutorials']
    assert 'namespace' in n['Meta']
    assert [i in n['Meta']['namespace'] for i in namespaces], \
        "Namespace metadata incorrect: \n" \
        f"Provided: {n['Meta']['namespace']} \n" \
        f"Allowed: {namespaces}"

    # Check tags metadata
    tags = ['cpu', 'gpu', 'traefik']
    assert 'tags' in n['Meta']
    assert [i in n['Meta']['tags'] for i in tags], \
        "Tags metadata incorrect: \n" \
        f"Provided: {n['Meta']['tags']} \n" \
        f"Allowed: {tags}"
