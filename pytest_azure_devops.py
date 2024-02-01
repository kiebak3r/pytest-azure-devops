# -*- coding: utf-8 -*-

import os
import pytest
from itertools import zip_longest
from math import ceil


def grouper(items, total_groups: int):
    """
    >>> grouper([1,2,3,4,5,6,7,8], 1)
    [[1, 2, 3, 4, 5, 6, 7, 8]]

    >>> grouper( [1,2,3,4,5,6,7,8], 2 )
    [[1, 2, 3, 4], [5, 6, 7, 8]]

    >>> grouper([1,2,3,4,5,6,7,8], 3)
    [[1, 2, 3], [4, 5, 6], [7, 8]]

    >>> grouper([1,2,3,4,5,6,7,8], 4)
    [[1, 2], [3, 4], [5, 6], [7, 8]]

    >>> grouper([1,2,3,4,5,6,7,8], 5)
    [[1, 2], [3, 4], [5, 6], [7], [8]]

    >>> grouper([1,2,3,4,5,6,7,8], 6)
    [[1, 2], [3, 4], [5], [6], [7], [8]]

    >>> grouper([1,2,3,4,5,6,7,8], 7)
    [[1, 2], [3], [4], [5], [6], [7], [8]]

    >>> grouper([1,2,3,4,5,6,7,8], 8)
    [[1], [2], [3], [4], [5], [6], [7], [8]]
    """
    if total_groups <= 0:
        raise ValueError(f"total_groups should be bigger than zero but got {total_groups}")

    if total_groups < (len(items) / 2):
        chunk_size = ceil(len(items) / total_groups)
    else:
        chunk_size = 1

    groups = [
        [y for y in x if y] for x in zip_longest(*([iter(items)] * chunk_size), fillvalue=None)
    ]

    num_extra_groups = len(groups) - total_groups

    if not num_extra_groups:
        return groups
    elif num_extra_groups > 0:
        # re balance extra groups
        redist_groups = [groups[idx * 2] + groups[idx * 2 + 1] for idx in range(num_extra_groups)]
        redist_groups += groups[num_extra_groups * 2:]
        return redist_groups
    else:
        raise RuntimeError(f"Expected {total_groups} groups but got {groups}")


def get_module_name(item):
    """Get the module name of a pytest item."""
    return item.parent.name

# ... (previous code)

def pytest_collection_modifyitems(config, items):
    if not os.environ.get("TF_BUILD"):
        print(
            "pytest-azure-devops installed but not in azure devops (plugin disabled). "
            "To run plugin either run in tests in CI azure devops "
            "or set environment variables "
            "TF_BUILD, SYSTEM_TOTALJOBSINPHASE and "
            "SYSTEM_JOBPOSITIONINPHASE."
        )
        return

    total_agents = int(os.environ.get("SYSTEM_TOTALJOBSINPHASE", 1))
    agent_index = int(os.environ.get("SYSTEM_JOBPOSITIONINPHASE", 1)) - 1

    # Group tests by module
    module_groups = {}
    for item in items:
        module_name = get_module_name(item)
        if module_name not in module_groups:
            module_groups[module_name] = []
        module_groups[module_name].append(item)

    # Distribute module groups to agents
    agent_module_groups = grouper(list(module_groups.values()), total_agents)[agent_index]

    # Flatten the distributed module groups
    agent_tests = [test for module_group in agent_module_groups for test in module_group]

    # Print information about assigned module groups
    print(
        f"Agent nr. {agent_index + 1} of {total_agents} "
        f"selected {len(agent_tests)} of {len(items)} tests "
        "(other filters might apply afterwards, e.g. pytest marks)"
    )

    for idx, module_group in enumerate(agent_module_groups):
        print(f"Agent {agent_index + 1} - Assigned Module Group {idx + 1}: {module_group}")

    items[:] = agent_tests


if __name__ == "__main__":
    import doctest

    print(doctest.testmod(raise_on_error=True))
