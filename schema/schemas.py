def individual_serial(todo) -> dict:
    return {
        "id": str(todo["_id"]),
        "name": todo["name"],
        "description": todo["description"],
        "complete": todo["complete"]
    }


def list_serial(todos) -> list:
    return [individual_serial(todo) for todo in todos]


def business_serial(business) -> dict:
    return {
        "id": str(business["_id"]),
        "business_id": business["business_id"],
        "email": business["email"],
        "businessName": business["businessName"],
        "businessDescription": business["businessDescription"],
        "businessAddress": business["businessAddress"],
        "businessPhone": business["businessPhone"],
        "businessEmailAddress": business.get("businessEmailAddress"),
        "businessCategory": business["businessCategory"],
        "businessOpenHours": business.get("businessOpenHours"),
        "businessOpenDays": business.get("businessOpenDays"),
        "businessWebsite": business.get("businessWebsite"),
        "businessPicture": business.get("businessPicture"),
        "extra_information": business.get("extra_information"),
        "faqs": business.get("faqs", []),
        "items": business.get("items", [])
    }


def business_list_serial(businesses) -> list:
    return [business_serial(business) for business in businesses]


def business_minimal_serial(business) -> dict:
    """Serialize business with only business_id, name, and description"""
    return {
        "business_id": business["business_id"],
        "name": business["businessName"],
        "description": business["businessDescription"]
    }


def business_minimal_list_serial(businesses) -> list:
    """Serialize list of businesses with minimal info"""
    return [business_minimal_serial(business) for business in businesses]
