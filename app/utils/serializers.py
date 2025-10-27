from datetime import datetime
from bson import ObjectId

def to_serializable(doc):
    if isinstance(doc, list):
        return [to_serializable(d) for d in doc]
    if isinstance(doc, dict):
        return {k: to_serializable(v) for k, v in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime):
        return doc.isoformat()
    return doc
