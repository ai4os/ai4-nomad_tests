#TODO: move to proper test package?

import logging
from typing import List
from time import time

from rich import print
import typer

from ai4_nomad_tests.nomad_utils import Nomad, update_node_metadata
import ai4_nomad_tests.tests as tests


app = typer.Typer()


@app.command()
def main(
    cluster: bool = False,  # tests the whole cluster
    datacenter: str = None,  # tests a single datacenter
    nodes: List[str] = None,  # test a list of nodes
    mark_ineligible: bool = False,  # mark node as ineligible if fails to pass
    ):

    t0 = time()

    if not any([cluster, datacenter, nodes]):
        raise Exception(
            "You must either test the whole cluster, a single datacenter or a list " \
            "of nodes."
        )

    if datacenter:  # test entire datacenter

        print(f"Testing datacenter: [yellow bold]{datacenter}[/yellow bold]")

        # Parse nodes belonging to datacenter
        nodes, node_ids, datacenters = [], [], set()
        for node in Nomad.nodes.get_nodes():
            datacenters.add(node['Datacenter'])
            if node['Datacenter'] == datacenter:
                nodes.append(node['Name'])
                node_ids.append(node['ID'])

        # Check datacenter_name input is correct
        assert datacenter in datacenters, \
            f"Provided datacenter {datacenter} does not exists: \n" \
            f"{datacenters}"

        # Run datacenter specific checks
        tests.datacenter.consistency(node_ids)

        print(
            "\n:green_circle: [green bold]All tests successfully passed!" \
            "[/green bold] :green_circle: \n"
            )

    # Map names to node IDs
    name2id = {n['Name']: n['ID'] for n in Nomad.nodes.get_nodes()}

    # If testing the whole cluster, select all nodes
    if cluster:
        print("Testing whole cluster")
        tests.cluster.consistency()
        nodes = list(name2id.keys())

    # Check node_name input is correct
    name_test = [i in name2id.keys() for i in nodes]
    assert all(name_test), \
        "Some names you provided do not exists: \n" \
        f"Provided: {nodes} \n" \
        f"Existing: {name2id.keys()}"

    for node in nodes:
        try:
            print(f"Testing node: [yellow bold]{node}[/yellow bold]")

            nid = name2id[node]
            tests.node.common.node_info(nid)
            n = Nomad.node.get_node(nid)
            tags = n['Meta']['tags']

            if "traefik" in tags:
                tests.node.traefik.node_info(nid)

            elif "gpu" in tags:
                tests.node.gpu.node_info(nid)
                tests.node.cpu.deployment(nid)  # deployment test is same as CPU

            elif "cpu" in tags:
                tests.node.cpu.node_info(nid)
                tests.node.cpu.deployment(nid)

            else:
                raise Exception(
                    "Invalid node type: \n" \
                    f"- Node tags: {tags} \n" \
                    "- Supported tags: [cpu, gpu, traefik]"
                    )

            print(
                "\n:green_circle: [green bold]All tests successfully passed!" \
                "[/green bold] :green_circle: \n"
                )

        except AssertionError:
            logging.error("Assertion error:", exc_info=True)
            print(
                "\n:red_circle: [red bold]Some tests failed![/red bold] :red_circle: \n"
                )

            # Mark node as ineligible (we might not want it to mark as ineligible
            # because we might need to run test jobs in the node to fix it)
            if mark_ineligible:
                print("Marking node as ineligible.")
                Nomad.node.eligible_node(nid, ineligible=True)

            # Set the node status as "error"
            update_node_metadata(nid, 'status', 'error')

        # Set the node status as "ready"
        update_node_metadata(nid, 'status', 'ready')

    t1 = time()
    print(f"Tests duration: {t1-t0:.1f} seconds")
