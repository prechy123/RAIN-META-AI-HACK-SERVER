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