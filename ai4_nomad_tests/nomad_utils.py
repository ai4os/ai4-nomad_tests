"""
Miscellaneous Nomad patches
"""

import subprocess

import nomad

from rich import print

Nomad = nomad.Nomad()

def update_node_metadata(
    node_id: str,
    metadata_key: str,
    metadata_value: str,
):
    """
    Update a Nomad node metadata from CLI (not available in the Nomad Python client)
    """
    try:
        s = subprocess.run(
            f"nomad node meta apply -node-id {node_id} {metadata_key}={metadata_value}",
            shell=True,
        )
        if s.returncode != 0:
            # When the node is down, we cannot update metadata [1]. We don't want to
            # raise an Exception to avoid interrupting the testing of other nodes.
            # [1]: "Error applying dynamic node metadata: Unexpected response code: 404 (No path to node)"
            print(
                ":warning-emoji: [orange_red1] Failed to update the node's metadata. [/orange_red1]"
            )

    except Exception:
        raise Exception(
            "Failed to update the node's metadata.",
            "Make sure your Nomad client version is >= 1.5.",
        )
