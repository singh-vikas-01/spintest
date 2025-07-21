import pytest
from spintest.e2e_task import E2ETask
from unittest.mock import AsyncMock
from spintest import spintest

# async def target(url):
#     # Simulate a successful E2E task
#     assert url == "http://test.com"


@pytest.fixture
def valid_task():
    return {
        "type": "e2e",
        "name": "test_task",
        "target": AsyncMock(),
        "ignore": False,
    }


def test_valid_task_target_callable(valid_task):
    assert callable(valid_task["target"])


@pytest.fixture
def invalid_task():
    return {
        "type": "e2e",
        "name": "test_task",
        "target": None,  # Invalid target
        "ignore": False,
    }


@pytest.fixture
def url():
    return "http://example.com"


def test_e2e_task_initialization(valid_task, url):
    task = E2ETask(url, valid_task)
    assert task.url == url
    assert task.task == valid_task
    assert task.name == valid_task["name"]
    assert task.target == valid_task["target"]
    assert task.ignore == valid_task["ignore"]
    assert task.response is None


def test_e2e_task_response_success(valid_task, url):
    task = E2ETask(url, valid_task)
    response = task._response("SUCCESS", "mock_target", "Task executed successfully.")
    assert response["status"] == "SUCCESS"
    assert response["message"] == "Task executed successfully."
    assert response["name"] == valid_task["name"]
    assert response["url"] == url


def test_e2e_task_response_failure(valid_task, url):
    task = E2ETask(url, valid_task)
    response = task._response("FAILURE", "mock_target", "Task failed.")
    assert response["status"] == "FAILURE"
    assert response["message"] == "Task failed."
    assert response["name"] == valid_task["name"]
    assert response["url"] == url


@pytest.mark.asyncio
async def test_e2e_task_run_success(valid_task, url):
    valid_task["target"].return_value = None
    task = E2ETask(url, valid_task)
    response = await task.run()
    assert response["status"] == "SUCCESS"
    assert response["message"] == "Task executed successfully."
    assert response["duration_sec"] is not None


@pytest.mark.asyncio
async def test_e2e_task_run_failure_assertion(valid_task, url):
    async def failing_target(url):
        raise AssertionError("Test assertion error")

    valid_task["target"] = failing_target
    task = E2ETask(url, valid_task)
    response = await task.run()
    assert response["status"] == "FAILURE"
    assert "assertion error" in response["message"]


@pytest.mark.asyncio
async def test_e2e_task_run_failure_exception(valid_task, url):
    valid_task["target"].side_effect = Exception("Test exception")
    task = E2ETask(url, valid_task)
    response = await task.run()
    assert response["status"] == "ERROR"
    assert "encountered an error" in response["message"]


@pytest.mark.asyncio
async def test_e2e_task_initialization_invalid_task(invalid_task, url):
    task = E2ETask(url, invalid_task)
    response = await task.run()
    assert response["status"] == "FAILURE"
    assert "schema validation failed" in response["message"]


def test_e2e_task_success():

    async def target(url):
        # Simulate a successful E2E task
        assert url == "http://test.com"

    result = spintest(["http://test.com"], [{"type": "e2e", "target": target}])

    assert True is result


def test_e2e_task_invalid_target_not_callable():

    target = "invalid_target"  # Not callable

    result = spintest(["http://test.com"], [{"type": "e2e", "target": target}])

    assert False is result


def test_e2e_task_invalid_target_not_async():

    def target(url):
        # Simulate a non-async target
        assert url == "http://test.com"

    result = spintest(["http://test.com"], [{"type": "e2e", "target": target}])

    assert False is result
