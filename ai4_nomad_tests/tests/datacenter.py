"""
Datacenter wide checks
"""
from rich import print

from ai4_nomad_tests.nomad_utils import Nomad
from ai4_nomad_tests.tests.node import common


def consistency(
        node_ids: list,
        ):
    print('  Running test: [hot_pink3 bold]datacenter.consistency[/hot_pink3 bold]')

    domains, traefik = set(), []
    for nid in node_ids:
        n = Nomad.node.get_node(nid)

        # Check basic node info
        common.node_info(nid)

        # Add info for extra checks
        domains.add(n['Datacenter'])
        traefik.append(
            ('traefik' in n['Meta']['tags']) and (n['Meta']['compute']=='false')
        )

    # Check all nodes in datacenter have same domain
    assert len(domains) == 1, \
        "You have defined more than one domain in your datacenter: \n" \
        f"{domains}"

    # Check *at least* one node in datacenter has `compute=false` and `tag=traefik`
    assert any(traefik), \
        "It looks you are missing a Traefik node"
