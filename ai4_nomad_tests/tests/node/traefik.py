"""
Tests a Traefik node.
"""
from rich import print

from ai4_nomad_tests.nomad_utils import Nomad


def node_info(
        node_id: str,
        ):

    print('  Running test: [hot_pink3 bold]node.traefik.node_info[/hot_pink3 bold]')

    n = Nomad.node.get_node(node_id)

    # Check node metadata
    assert n['Meta']['compute'] == 'false'
