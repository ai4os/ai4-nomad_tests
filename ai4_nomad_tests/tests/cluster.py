"""
Tests whole cluster consistency.
"""
from rich import print

from ai4_nomad_tests.nomad_utils import Nomad
from ai4_nomad_tests.tests.node import common


def consistency():

    print('  Running test: [hot_pink3 bold]cluster.consistency[/hot_pink3 bold]')

    # Check that nodes on different datacenters do not share same domain
    pairs = set()
    for node in Nomad.nodes.get_nodes():
        node = Nomad.node.get_node(node['ID'])
        common.node_info(node['ID'])
        pairs.add(
            (node['Datacenter'], node['Meta']['domain'])
        )

    datacenters = {i[0] for i in pairs}
    assert len(datacenters) == len(pairs), \
        f"At least one datacenter has two domains defined: \n {pairs}"

    domains = {i[1] for i in pairs}
    assert len(domains) == len(pairs), \
        f"At least two datacenters share the same domain: \n {pairs}"
