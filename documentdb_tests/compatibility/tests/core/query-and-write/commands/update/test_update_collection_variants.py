"""
Tests for update command with different collection variants.

Validates behavior on views (error) and capped collections.
"""

from documentdb_tests.framework.assertions import assertFailureCode, assertSuccess
from documentdb_tests.framework.error_codes import COMMAND_NOT_SUPPORTED_ON_VIEW_ERROR
from documentdb_tests.framework.executor import execute_command


def test_update_on_view_errors(database_client):
    """Test update command targeting a view errors (views are read-only)."""
    coll = database_client["base_coll"]
    coll.insert_one({"_id": 1, "x": 1})
    database_client.command("create", "my_view", viewOn="base_coll", pipeline=[])
    view = database_client["my_view"]
    result = execute_command(
        view,
        {
            "update": "my_view",
            "updates": [{"q": {"_id": 1}, "u": {"$set": {"x": 2}}}],
        },
    )
    assertFailureCode(result, COMMAND_NOT_SUPPORTED_ON_VIEW_ERROR)


def test_update_on_capped_collection_same_size(database_client):
    """Test update on capped collection that doesn't change doc size succeeds."""
    database_client.command("create", "capped_coll", capped=True, size=4096)
    coll = database_client["capped_coll"]
    coll.insert_one({"_id": 1, "x": 1})
    result = execute_command(
        coll,
        {
            "update": "capped_coll",
            "updates": [{"q": {"_id": 1}, "u": {"$set": {"x": 2}}}],
        },
    )
    assertSuccess(result, {"ok": 1.0, "n": 1, "nModified": 1}, raw_res=True)
