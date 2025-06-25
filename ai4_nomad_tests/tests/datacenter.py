"""
Datacenter wide checks
"""

from rich import print

from ai4_nomad_tests.nomad_utils import Nomad
from ai4_nomad_tests.tests.node import common


def consistency(
    node_ids: list,
):
    print("  Running test: [hot_pink3 bold]datacenter.consistency[/hot_pink3 bold]")

    domains, ntypes = set(), []
    for nid in node_ids:
        print(f"[grey50]    Retrieving node info: {nid}[/grey50]")

        n = Nomad.node.get_node(nid)

        # Add info for extra checks
        domains.add(n["Datacenter"])
        ntypes.append(n["Meta"]["type"])

    # Check all nodes in datacenter have same domain
    assert len(domains) == 1, (
        f"You have defined more than one domain in your datacenter: \n{domains}"
    )

    # Check *at least* one node is a Traefik node
    assert any([i == "traefik" for i in ntypes]), (
        "It looks you are missing a Traefik node"
    )
