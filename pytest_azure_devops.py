# -*- coding: utf-8 -*-

import os
import pytest

env_vars_error = (
            "pytest-azure-devops installed but not in Azure DevOps (plugin disabled). "
            "To run plugin either run tests in CI Azure DevOps "
            "or set environment variables "
            "TF_BUILD, SYSTEM_TOTALJOBSINPHASE and "
            "SYSTEM_JOBPOSITIONINPHASE."
        )


def grouper(items, total_groups):
    group_map = {}
    for item in items:
        marker = item.get_closest_marker('xdist_group')
        key = marker.args[0] if marker and marker.args else item.nodeid
        group_map.setdefault(key, []).append(item)

    # Sort groups by size (largest first)
    groups = sorted(group_map.values(), key=len, reverse=True)

    agent_tests = [[] for _ in range(total_groups)]
    agent_counts = [0] * total_groups

    for group in groups:
        least_loaded = agent_counts.index(min(agent_counts))
        agent_tests[least_loaded].extend(group)
        agent_counts[least_loaded] += len(group)

    return agent_tests


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    if not os.environ.get("TF_BUILD"):
        print(env_vars_error)
        return

    total_agents = int(os.environ.get("SYSTEM_TOTALJOBSINPHASE", 1))
    agent_index = int(os.environ.get("SYSTEM_JOBPOSITIONINPHASE", 1)) - 1

    # Distribute all identified tests
    distributed_tests = grouper(items, total_agents)

    # Select tests for this agent
    agent_tests = distributed_tests[agent_index]
    items[:] = agent_tests
