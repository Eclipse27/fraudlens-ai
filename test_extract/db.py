"""
DynamoDB abstraction layer for FraudLens AI investigation history.

Uses boto3 with the standard AWS credential provider chain.
No hardcoded AWS credentials — in production, uses the EC2 instance profile / IAM role.
Locally, uses credentials from `aws configure` or environment variables.

Environment variables:
    AWS_REGION           — AWS region (default: us-east-1)
    DYNAMODB_TABLE_NAME  — DynamoDB table name (default: FraudInvestigationHistory)
    DYNAMODB_ENDPOINT_URL — Optional custom endpoint for DynamoDB Local testing
"""

import os
import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
from decimal import Decimal

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "FraudInvestigationHistory")
DYNAMODB_ENDPOINT_URL = os.environ.get("DYNAMODB_ENDPOINT_URL", None)


def _get_dynamodb_resource():
    """Create a boto3 DynamoDB resource using the standard credential chain."""
    kwargs = {"region_name": AWS_REGION}
    if DYNAMODB_ENDPOINT_URL:
        kwargs["endpoint_url"] = DYNAMODB_ENDPOINT_URL
    return boto3.resource("dynamodb", **kwargs)


def _get_table():
    """Get a reference to the DynamoDB table."""
    dynamodb = _get_dynamodb_resource()
    return dynamodb.Table(DYNAMODB_TABLE_NAME)


def _convert_floats(obj):
    """
    Recursively convert float values to Decimal for DynamoDB compatibility.
    DynamoDB does not accept Python float types.
    """
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: _convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_floats(i) for i in obj]
    return obj


def _convert_decimals(obj):
    """
    Recursively convert Decimal values back to float for JSON serialization.
    DynamoDB returns Decimal types which are not JSON-serializable.
    """
    if isinstance(obj, Decimal):
        # Return int if it's a whole number, otherwise float
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_decimals(i) for i in obj]
    return obj


def check_dynamodb_connection() -> dict:
    """
    Check if DynamoDB is reachable and the table exists.
    Returns a status dict. This is informational only and does NOT determine API health.
    """
    try:
        table = _get_table()
        table.table_status  # Triggers a DescribeTable call
        return {"status": "connected", "table": DYNAMODB_TABLE_NAME, "region": AWS_REGION}
    except NoCredentialsError:
        return {"status": "no_credentials", "detail": "AWS credentials not configured"}
    except EndpointConnectionError:
        return {"status": "unreachable", "detail": "Cannot reach DynamoDB endpoint"}
    except ClientError as e:
        return {"status": "error", "detail": str(e)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def save_history_record(record: dict) -> dict:
    """
    Save an investigation history record to DynamoDB.
    
    Args:
        record: Dict containing id, type, timestamp, riskScore, riskLevel, status, result
    
    Returns:
        The saved record
    
    Raises:
        Exception if DynamoDB is unavailable or credentials are missing
    """
    table = _get_table()
    item = _convert_floats(record)
    table.put_item(Item=item)
    return record


def get_all_history() -> list:
    """
    Retrieve all investigation history records from DynamoDB.
    Results are sorted by timestamp (newest first).
    
    Returns:
        List of history record dicts
    
    Raises:
        Exception if DynamoDB is unavailable or credentials are missing
    """
    table = _get_table()
    response = table.scan()
    items = response.get("Items", [])
    
    # Handle pagination for large datasets
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))
    
    # Convert Decimals back to native Python types
    items = [_convert_decimals(item) for item in items]
    
    # Sort by timestamp descending (newest first)
    items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return items


def get_history_by_id(record_id: str) -> dict | None:
    """
    Retrieve a single history record by its ID.
    
    Args:
        record_id: The partition key value
    
    Returns:
        The history record dict, or None if not found
    
    Raises:
        Exception if DynamoDB is unavailable or credentials are missing
    """
    table = _get_table()
    response = table.get_item(Key={"id": record_id})
    item = response.get("Item")
    if item:
        return _convert_decimals(item)
    return None


def delete_all_history() -> int:
    """
    Delete all investigation history records from DynamoDB.
    DynamoDB does not have a native 'truncate' operation, so this scans
    and deletes records individually. Acceptable for this low-volume project.
    
    Returns:
        Number of records deleted
    
    Raises:
        Exception if DynamoDB is unavailable or credentials are missing
    """
    table = _get_table()
    response = table.scan(ProjectionExpression="id")
    items = response.get("Items", [])
    
    while "LastEvaluatedKey" in response:
        response = table.scan(
            ExclusiveStartKey=response["LastEvaluatedKey"],
            ProjectionExpression="id"
        )
        items.extend(response.get("Items", []))
    
    deleted = 0
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={"id": item["id"]})
            deleted += 1
    
    return deleted
