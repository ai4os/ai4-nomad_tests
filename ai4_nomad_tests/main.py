#TODO: move to proper test package

import logging

from rich import print

from ai4_nomad_tests.nomad_utils import Nomad
import ai4_nomad_tests.tests as tests


#todo: add typer
def run(
    datacenter: str = None,
    nodes: list = None,
    ):

    if datacenter:  # test entire datacenter

        print(f'Testing datacenter: [yellow bold]{datacenter}[/yellow bold]')

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

        print('\n:green_circle: [green bold]All tests successfully passed![/green bold] :green_circle: \n')

    # Test nodes nodes individually
    name2id = {n['Name']: n['ID'] for n in Nomad.nodes.get_nodes()}

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
                # GPU specific tests
                tests.node.gpu.node_info(nid)

            elif "cpu" in tags or "gpu" in tags:
                # GPU nodes should also be tested as CPU nodes
                tests.node.cpu.node_info(nid)
                tests.node.cpu.deployment(nid)

            else:
                raise Exception(
                    "Invalid node type: \n" \
                    f"- Node tags: {tags} \n" \
                    "- Supported tags: [cpu, gpu, traefik]"
                    )

            print('\n:green_circle: [green bold]All tests successfully passed![/green bold] :green_circle: \n')

        except AssertionError:
            logging.error("Assertion error:", exc_info=True)
            print('\n:red_circle: [red bold]Some tests failed![/red bold] :red_circle: \n')

    #todo: reenable
    # # Check the whole cluster
    # print('Testing whole cluster')
    # tests.cluster.consistency()


# run(datacenter='ifca-ai4eosc')
# run(datacenter='ifca-imagine')
# run(nodes=['node-ifca-traefik'])  # traefik
# run(nodes=['node-ifca-1'])  # cpu
# run(nodes=['node-ifca-gpu-0'])  # gpu
# run(nodes=['node-ifca-imagine-1'])  # cpu
# run(nodes=['node-ifca-imagine-gpu-0'])  # gpu
