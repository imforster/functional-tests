"""
Tests for update command interaction with schema validation.

Validates bypassDocumentValidation behavior with valid and invalid updates.
"""

from documentdb_tests.framework.assertions import assertFailureCode, assertSuccess
from documentdb_tests.framework.error_codes import DOCUMENT_VALIDATION_FAILURE_ERROR
from documentdb_tests.framework.executor import execute_command


def test_update_violating_validation_fails(database_client):
    """Test update violating schema validation fails with bypass:false."""
    database_client.command(
        "create",
        "validated_coll",
        validator={"$jsonSchema": {"required": ["x"], "properties": {"x": {"bsonType": "int"}}}},
    )
    coll = database_client["validated_coll"]
    coll.insert_one({"_id": 1, "x": 1})
    result = execute_command(
        coll,
        {
            "update": "validated_coll",
            "updates": [{"q": {"_id": 1}, "u": {"$set": {"x": "not_int"}}}],
        },
    )
    assertFailureCode(result, DOCUMENT_VALIDATION_FAILURE_ERROR)


def test_update_violating_validation_succeeds_with_bypass(database_client):
    """Test update violating schema validation succeeds with bypass:true."""
    database_client.command(
        "create",
        "validated_coll2",
        validator={"$jsonSchema": {"required": ["x"], "properties": {"x": {"bsonType": "int"}}}},
    )
    coll = database_client["validated_coll2"]
    coll.insert_one({"_id": 1, "x": 1})
    result = execute_command(
        coll,
        {
            "update": "validated_coll2",
            "updates": [{"q": {"_id": 1}, "u": {"$set": {"x": "not_int"}}}],
            "bypassDocumentValidation": True,
        },
    )
    assertSuccess(result, {"ok": 1.0, "n": 1, "nModified": 1}, raw_res=True)


def test_update_passing_validation_succeeds(database_client):
    """Test update passing schema validation succeeds normally."""
    database_client.command(
        "create",
        "validated_coll3",
        validator={"$jsonSchema": {"required": ["x"], "properties": {"x": {"bsonType": "int"}}}},
    )
    coll = database_client["validated_coll3"]
    coll.insert_one({"_id": 1, "x": 1})
    result = execute_command(
        coll,
        {
            "update": "validated_coll3",
            "updates": [{"q": {"_id": 1}, "u": {"$set": {"x": 42}}}],
        },
    )
    assertSuccess(result, {"ok": 1.0, "n": 1, "nModified": 1}, raw_res=True)
