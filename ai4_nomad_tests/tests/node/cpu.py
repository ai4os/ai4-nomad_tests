"""
Test a CPU node
"""

from copy import deepcopy
import time
import uuid

import requests
from rich import print

from ai4_nomad_tests.conf import DOMAINS, NOMAD_JOBS
from ai4_nomad_tests.nomad_utils import Nomad


session = requests.Session()


def node_info(
        node_id: str,
        ):

    print('  Running test: [hot_pink3 bold]node.cpu.node_info[/hot_pink3 bold]')

    n = Nomad.node.get_node(node_id)

    assert n['Attributes']['unique.storage.volume'] in ['/dev/vdb1', '/dev/sdb1'], "No volume mounted"
    assert n['ReservedResources']['Memory']['MemoryMB'] >= 4096, "No minimal RAM reserved"
    disk_GB = int(n['Attributes']['unique.storage.bytesfree']) / 10**9
    cpu_cores = int(n['Attributes']['cpu.reservablecores'])
    assert disk_GB / cpu_cores > 5, "Node should have at least 5 GB disk per CPU core"

    # Check node metadata
    assert n['Meta']['compute'] == 'true'


def deployment(
        node_id: str,
        timeout_nomad: int = 300,  # timeout for deploying Nomad job (5 mins)
        timeout_deepaas: int = 60,  # timeout for running deepaas (1 mins)
        ):
    """
    Make a CPU deployment.

    Possible breaking features:
    * Volume not properly configured
      --> filesystem xfs with pquota option
    * Traefik not making accessing job
    """
    print('  Running test: [hot_pink3 bold]node.cpu.deployment[/hot_pink3 bold]')

    # Before running anything make sure to purge old tests jobs
    Nomad.job.deregister_job(
        id_='nomad-tests-cpu',
        purge=True,
        )

    n = Nomad.node.get_node(node_id)

    # Assert node is eligible (might have been marked as ineligible by some previous
    # test failure)
    if n['SchedulingEligibility'] == 'ineligible':
        # We could mark the node eligible here, but for the moment let's keep this step
        # manual
        raise Exception(
            "The node status is ineligible, so `tests.cpu.deployment()` cannot be ran" \
            ". The node might have been automatically flagged as ineligible due to "  \
            "some previous tests failing to successfully run there. This is done to "  \
            "avoid new user deployments landing in a failing node. " \
            "If your tests have ran successfully up to this point and you want to "  \
            "run these final `tests.cpu.deployment()`, please mark the node as " \
            "`eligible` in the Nomad UI and run the tests again."
        )

    # Retrieve supported domains
    namespaces = ['ai4eosc', 'imagine', 'tutorials']
    namespaces[:] = [i for i in namespaces if i in n['Meta']['namespace']]
    domains = [f"{n['Meta']['domain']}-{DOMAINS[i]}" for i in namespaces]

    # Configure job
    nomad_conf = deepcopy(NOMAD_JOBS['cpu'])
    test_uuid =  str(uuid.uuid1())[:8]
    nomad_conf = nomad_conf.safe_substitute(  # replace the Nomad job template
        {
            'NODE_ID': node_id,
            'UUID': test_uuid,
            'DOMAIN_0': domains[0] if len(domains) > 0 else '',
            'DOMAIN_1': domains[1] if len(domains) > 1 else '',
            'DOMAIN_2': domains[2] if len(domains) > 2 else '',
        }
    )
    nomad_conf = Nomad.jobs.parse(nomad_conf)  # convert template to Nomad conf

    # Remove unneeded services (cosmetic)
    services = nomad_conf['TaskGroups'][0]['Services']
    services = services[:len(domains)]
    nomad_conf['TaskGroups'][0]['Services'] = services

    # Submit job
    _ = Nomad.jobs.register_job({'Job': nomad_conf})

    # Wait some seconds until the allocation is made
    time.sleep(5)

    # Reorder allocations based on recency
    allocs = Nomad.job.get_allocations('nomad-tests-cpu')
    dates = [a['CreateTime'] for a in allocs]
    allocs = [x for _, x in sorted(
        zip(dates, allocs),
        key=lambda pair: pair[0],
        )][::-1]  # more recent first
    a = allocs[0]

    # Check allocation status every 5 seconds until timeout
    deployed = False
    check_freq = 5
    for _ in range(timeout_nomad // check_freq):
        a = Nomad.allocation.get_allocation(a['ID'])
        if a['ClientStatus'] == 'running':
            deployed = True
            break
        time.sleep(check_freq)

    if not deployed:
        raise Exception(
            "Timeout: The job has *not* been successfully deployed after "\
            f"{timeout_nomad} seconds timeout."
            )

    # Check status is running
    assert a['ClientStatus'] == 'running'

    # Check deepaas is accessible every 5 seconds until timeout
    for i, domain in enumerate(domains):
        print(f'  [grey50]Testing domain: [bold]{domain}[/bold][/grey50]')

        url = f'https://api{i}-nomad-tests-cpu-{test_uuid}.{domain}'
        for _ in range(timeout_deepaas // check_freq):
            r = session.get(url)
            if r.status_code == 200:
                break
            time.sleep(check_freq)

        if r.status_code != 200:
            raise Exception(
                f"DEEPaaS API not accessible after a {timeout_deepaas} seconds timeout. \n" \
                f"    {url} \n" \
                "Please check: \n" \
                "1. you have a running Traefik job \n" \
                "2. you have properly set up the security groups in Openstack \n" \
                f"3. you have created SSL certs for *.{domain} \n" \
                "4. you have copied the SSL certs in your Traefik job \n"
            )

    # Delete job
    Nomad.job.deregister_job(
        id_='nomad-tests-cpu',
        purge=True,
        )
