import json
import uuid

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("items")


def respond(status_code, data):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data, default=str),
    }


def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    try:
        if method == "GET":
            result = table.scan()
            return respond(200, result.get("Items", []))

        if method == "POST":
            body = json.loads(event.get("body") or "{}")
            if not body:
                return respond(400, {"error": "Request body is required"})
            item = dict(body)
            item["id"] = str(body.get("id") or uuid.uuid4())
            table.put_item(Item=item)
            return respond(201, item)

        return respond(405, {"error": f"Method {method} not allowed"})
    except Exception as exc:
        return respond(500, {"error": str(exc)})
