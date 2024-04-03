"""
Test a GPU node.

We do not test deploying a GPU because it might break because
all GPUs are booked, but the node is still properly configured.
"""
from rich import print

from ai4_nomad_tests.nomad_utils import Nomad


def node_info(
        node_id: str,
        ):
    print('  Running test: [hot_pink3 bold]node.gpu.node_info[/hot_pink3 bold]')

    n = Nomad.node.get_node(node_id)

    assert n['Attributes']['unique.storage.volume'] in ['/dev/vdb1', '/dev/sdb1'], "No volume mounted"
    assert n['ReservedResources']['Memory']['MemoryMB'] >= 4096, "No minimal RAM reserved"
    #todo: check minimal disk per GPU device

    # Check node metadata
    assert n['Meta']['compute'] == 'true'

    # Check if GPU devices are detected
    devices = n['NodeResources']['Devices']
    assert devices, "No (GPU) device detected in node"
    assert [d['Type'] == 'gpu' for d in devices], "Devices detected in node but not GPU"
