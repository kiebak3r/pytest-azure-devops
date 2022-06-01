# -*- coding: utf-8 -*-


def test_azure_devops_group_selection(testdir, monkeypatch):
    monkeypatch.setenv('TF_BUILD', '1')
    monkeypatch.setenv('SYSTEM_TOTALJOBSINPHASE', '3')
    monkeypatch.setenv('SYSTEM_JOBPOSITIONINPHASE', '1')

    testdir.makepyfile("""
        def test_1(): assert True
        def test_2(): assert True
        def test_3(): assert True
        def test_4(): assert False
        def test_5(): assert False
        def test_6(): assert False
        def test_7(): assert False
        def test_8(): assert False
        def test_9(): assert False
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_* PASSED*',
    ])

    assert result.ret == 0


def test_not_in_azure_devops(testdir, monkeypatch):
    monkeypatch.setenv('TF_BUILD', '')

    testdir.makepyfile("""
        def test_1(): assert True
        def test_2(): assert True
        def test_3(): assert True
        def test_4(): assert True
        def test_5(): assert True
        def test_6(): assert True
        def test_7(): assert True
        def test_8(): assert True
        def test_9(): assert True
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_1 PASSED*',
        '*::test_2 PASSED*',
        '*::test_3 PASSED*',
        '*::test_4 PASSED*',
        '*::test_5 PASSED*',
        '*::test_6 PASSED*',
        '*::test_7 PASSED*',
        '*::test_8 PASSED*',
        '*::test_9 PASSED*',
    ])

    assert result.ret == 0
