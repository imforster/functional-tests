"""
Error case tests for $max update field operator.

Tests $max conflict errors, invalid field paths, dollar-prefixed fields,
and operand type validation.
"""

from datetime import datetime, timezone

import pytest
from bson import Binary, Code, Decimal128, Int64, MaxKey, MinKey, ObjectId, Regex, Timestamp

from documentdb_tests.compatibility.tests.core.operator.update.utils import UpdateTestCase
from documentdb_tests.framework.assertions import assertFailureCode
from documentdb_tests.framework.error_codes import (
    BAD_VALUE_ERROR,
    CONFLICTING_UPDATE_OPERATORS_ERROR,
    DOLLAR_PREFIXED_FIELD_NAME_ERROR,
    FAILED_TO_PARSE_ERROR,
)
from documentdb_tests.framework.executor import execute_command
from documentdb_tests.framework.parametrize import pytest_params

# Property [Error Cases]: $max rejects conflicting operators on same field and invalid field names.
ERROR_TESTS: list[UpdateTestCase] = [
    UpdateTestCase(
        "conflict_with_min_same_field",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": {"val": 20}, "$min": {"val": 5}},
        error_code=CONFLICTING_UPDATE_OPERATORS_ERROR,
        msg="$max and $min on same field should produce conflict error",
    ),
    UpdateTestCase(
        "conflict_with_set_same_field",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": {"val": 20}, "$set": {"val": 5}},
        error_code=CONFLICTING_UPDATE_OPERATORS_ERROR,
        msg="$max and $set on same field should produce conflict error",
    ),
    UpdateTestCase(
        "conflict_with_inc_same_field",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": {"val": 20}, "$inc": {"val": 5}},
        error_code=CONFLICTING_UPDATE_OPERATORS_ERROR,
        msg="$max and $inc on same field should produce conflict error",
    ),
    UpdateTestCase(
        "dollar_prefixed_field_error",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": {"$field": 20}},
        error_code=DOLLAR_PREFIXED_FIELD_NAME_ERROR,
        msg="$max with dollar-prefixed field name should produce error",
    ),
    UpdateTestCase(
        "bare_dollar_field_error",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": {"$": 20}},
        error_code=BAD_VALUE_ERROR,
        msg="$max with bare '$' as field name should produce BadValue error",
    ),
]

# Property [Operand Type Validation]: $max operand must be a document;
# non-document types are rejected.
OPERAND_TYPE_TESTS: list[UpdateTestCase] = [
    UpdateTestCase(
        "operand_double",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": 3.14},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject double as operand",
    ),
    UpdateTestCase(
        "operand_string",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": "hello"},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject string as operand",
    ),
    UpdateTestCase(
        "operand_array",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": [1, 2, 3]},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject array as operand",
    ),
    UpdateTestCase(
        "operand_empty_array",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": []},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject empty array as operand",
    ),
    UpdateTestCase(
        "operand_binary",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": Binary(b"\x00\x01")},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject Binary as operand",
    ),
    UpdateTestCase(
        "operand_objectid",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": ObjectId()},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject ObjectId as operand",
    ),
    UpdateTestCase(
        "operand_bool_true",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": True},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject boolean true as operand",
    ),
    UpdateTestCase(
        "operand_bool_false",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": False},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject boolean false as operand",
    ),
    UpdateTestCase(
        "operand_datetime",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": datetime(2023, 1, 1, tzinfo=timezone.utc)},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject datetime as operand",
    ),
    UpdateTestCase(
        "operand_null",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": None},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject null as operand",
    ),
    UpdateTestCase(
        "operand_regex",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": Regex("^abc", "i")},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject Regex as operand",
    ),
    UpdateTestCase(
        "operand_int32",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": 42},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject int32 as operand",
    ),
    UpdateTestCase(
        "operand_int64",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": Int64(42)},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject Int64 as operand",
    ),
    UpdateTestCase(
        "operand_decimal128",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": Decimal128("42.5")},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject Decimal128 as operand",
    ),
    UpdateTestCase(
        "operand_timestamp",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": Timestamp(0, 1)},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject Timestamp as operand",
    ),
    UpdateTestCase(
        "operand_javascript",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": Code("function(){}")},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject JavaScript Code as operand",
    ),
    UpdateTestCase(
        "operand_minkey",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": MinKey()},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject MinKey as operand",
    ),
    UpdateTestCase(
        "operand_maxkey",
        setup_docs=[{"_id": 1, "val": 10}],
        query={"_id": 1},
        update={"$max": MaxKey()},
        error_code=FAILED_TO_PARSE_ERROR,
        msg="$max should reject MaxKey as operand",
    ),
]


@pytest.mark.parametrize("test", pytest_params(ERROR_TESTS))
def test_max_errors(collection, test: UpdateTestCase):
    """Test $max error cases produce expected error codes."""
    if test.setup_docs:
        collection.insert_many(test.setup_docs)

    result = execute_command(
        collection,
        {"update": collection.name, "updates": [{"q": test.query, "u": test.update}]},
    )
    assertFailureCode(result, test.error_code, msg=test.msg)  # type: ignore[arg-type]


@pytest.mark.parametrize("test", pytest_params(OPERAND_TYPE_TESTS))
def test_max_operand_type_rejection(collection, test: UpdateTestCase):
    """Test $max rejects non-document operand types."""
    if test.setup_docs:
        collection.insert_many(test.setup_docs)

    result = execute_command(
        collection,
        {"update": collection.name, "updates": [{"q": test.query, "u": test.update}]},
    )
    assertFailureCode(result, test.error_code, msg=test.msg)  # type: ignore[arg-type]
