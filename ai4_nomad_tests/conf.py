"""
Manage configuration
"""

from pathlib import Path
from string import Template


# Paths
main_pth = Path(__file__).parent.absolute()
jobs_pth = main_pth / "nomad-jobs"


def load_nomad_job(fpath):
    """
    Load default Nomad job configuration
    """
    with open(fpath, 'r') as f:
        raw_job = f.read()
        job_template = Template(raw_job)
    return job_template


NOMAD_JOBS = {
    j.stem: load_nomad_job(jobs_pth / j) for j in jobs_pth.glob('**/*.hcl')
}

DOMAINS = {
    'ai4eosc': 'deployments.cloud.ai4eosc.eu',
    'imagine': 'deployments.cloud.imagine-ai.eu',
    'tutorials': 'deployments.cloud.ai4eosc.eu',
}
