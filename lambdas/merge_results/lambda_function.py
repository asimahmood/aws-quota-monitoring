import json

def lambda_handler(event, context):
    merged = { "results": {}, "alert_data": {} }

    for item in event.get("raw_bodies", {}).get("bodies", []):
        if isinstance(item, str):
            body = json.loads(item)
        else:
            body = item

        merged["results"].update(body.get("results", {}))
        merged["alert_data"].update(body.get("alert_data", {}))

    merged["alert_needed"] = len(merged["alert_data"]) > 0
    return merged