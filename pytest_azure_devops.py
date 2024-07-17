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
    """Distribute items to groups in a balanced way using round-robin."""
    agent_tests = [[] for _ in range(total_groups)]
    for i, item in enumerate(items):
        agent_tests[i % total_groups].append(item)
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
