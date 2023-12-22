"""
Test a CPU node
"""

from copy import deepcopy
import time
import warnings

import requests
from rich import print

from ai4_nomad_tests.conf import DOMAINS, NOMAD_JOBS
from ai4_nomad_tests.nomad_utils import Nomad


def node_info(
        node_id: str,
        ):

    print('  Running test: [hot_pink3 bold]node.cpu.node_info[/hot_pink3 bold]')

    n = Nomad.node.get_node(node_id)

    assert n['Attributes']['unique.storage.volume'] == '/dev/vdb1', "No volume mounted"
    assert n['ReservedResources']['Memory']['MemoryMB'] >= 4096, "No minimal RAM reserved"
    disk_GB = int(n['Attributes']['unique.storage.bytesfree']) / 10**9
    cpu_cores = int(n['Attributes']['cpu.reservablecores'])
    assert disk_GB / cpu_cores > 5, "Node should have at least 5 GB disk per CPU core"

    # Check node metadata
    assert n['Meta']['compute'] == 'true'


def deployment(
        node_id: str,
        ):
    """
    Make a CPU deployment.

    Possible breaking features:
    * Volume not properly configured
      --> filesystem xfs with pquota option
    * Traefik not making accessing job
    """
    print('  Running test: [hot_pink3 bold]node.cpu.deployment[/hot_pink3 bold]')

    n = Nomad.node.get_node(node_id)

    # Retrieve supported domains
    namespaces = ['ai4eosc', 'imagine', 'tutorials']
    namespaces[:] = [i for i in namespaces if i in n['Meta']['namespace']]
    domains = [f"{n['Meta']['domain']}-{DOMAINS[i]}" for i in namespaces]

    # Launch job
    nomad_conf = deepcopy(NOMAD_JOBS['cpu'])
    nomad_conf = nomad_conf.safe_substitute(  # replace the Nomad job template
        {
            'NODE_ID': node_id,
            'DOMAIN_0': domains[0] if len(domains) > 0 else '',
            'DOMAIN_1': domains[1] if len(domains) > 1 else '',
            'DOMAIN_2': domains[2] if len(domains) > 2 else '',
        }
    )
    nomad_conf = Nomad.jobs.parse(nomad_conf)  # convert template to Nomad conf
    _ = Nomad.jobs.register_job({'Job': nomad_conf})  # submit job

    # Wait a few seconds till the job is deployed
    time.sleep(60)

    # Reorder allocations based on recency
    allocs = Nomad.job.get_allocations('nomad-tests-cpu')
    dates = [a['CreateTime'] for a in allocs]
    allocs = [x for _, x in sorted(
        zip(dates, allocs),
        key=lambda pair: pair[0],
        )][::-1]  # more recent first
    a = allocs[0]

    # Check status is running
    assert a['ClientStatus'] == 'running'

    # Check deepaas is accessible
    for domain in domains:
        print(f'  [grey50]Testing domain: [bold]{domain}[/bold][/grey50]')

        url = f'https://api-nomad-tests-cpu.{domain}'
        r = requests.get(url)
        assert r.status_code == 200, \
            "DEEPaaS API not accessible. Please check: \n" \
            "1. you have a running Traefik job \n" \
            "2. you have properly set up the security groups in Openstack \n" \
            f"3. you have created SSL certs for *.{domain} \n" \
            "4. you have copied the SSL certs in your Traefik job \n"

    # Delete job
    Nomad.job.deregister_job(
        id_='nomad-tests-cpu',
        purge=True,
        )
