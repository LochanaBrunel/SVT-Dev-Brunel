from .db_client import fetch_from_db
from .testsystem_client import TestSystemClient as client


def GetAllTests():
    return client.get_all_tests()

def RunTest(data):
    params=data.get("params", {})
    chipType=params.get("chipName","")
    testName=params.get("testName","")
    return client.run_test(chipType, testName, params)

def AbortTest(testId):
    return client.abort_test(testId)

def TestStatus(testId):
    return client.test_status(testId)

def RunLoopTest(chipType, testName, params, iterations):
    return client.run_loop_test(chipType, testName, params, iterations)

def RunTestPlan(planName, params):
    return client.run_test_plan(planName, params)