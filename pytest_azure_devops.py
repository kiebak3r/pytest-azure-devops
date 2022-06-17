# -*- coding: utf-8 -*-

import os
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
    Traceback (most recent call last):
    ...
    RuntimeError: Could not divide items with length 8 into 5 groups try with a smaller number of groups
    """
    if total_groups <= 0:
        raise ValueError(
            f"total_groups should be bigger than zero but got {total_groups}"
        )

    chunk_size = ceil(len(items) / total_groups)

    groups = [
        [y for y in x if y]
        for x in zip_longest(*([iter(items)] * chunk_size), fillvalue=None)
    ]

    if (len(groups)) != total_groups:
        raise RuntimeError(
            f"Could not divide items with length {len(items)} "
            f"into {total_groups} groups try with a smaller number of groups"
        )

    return groups


def pytest_collection_modifyitems(config, items):
    if not os.environ.get("TF_BUILD"):
        print("pytest-azure-devops installed but not in azure devops (plugin disabled). "
              "To run plugin either run in tests in CI azure devops "
              "or set environment variables "
              "TF_BUILD, SYSTEM_TOTALJOBSINPHASE and "
              "SYSTEM_JOBPOSITIONINPHASE.")
        return

    total_agents = int(os.environ.get("SYSTEM_TOTALJOBSINPHASE", 1))
    agent_index = int(os.environ.get("SYSTEM_JOBPOSITIONINPHASE", 1)) - 1

    agent_tests = grouper(items, total_agents)[agent_index]

    print(
        f"Agent nr. {agent_index + 1} of {total_agents} "
        f"selected {len(agent_tests)} of {len(items)} tests "
        "(other filters might apply afterwards, e.g. pytest marks)"
    )

    items[:] = agent_tests
