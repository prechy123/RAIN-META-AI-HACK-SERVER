"""
Shared session utilities for WhatsApp and Web chatbot routes
"""
from config.database import business_collection
from difflib import SequenceMatcher
import logging

logger = logging.getLogger("session_utils")


class SessionState:
    """Session state constants"""
    INITIAL = "INITIAL"
    AWAITING_NAME = "AWAITING_NAME"
    AWAITING_BUSINESS = "AWAITING_BUSINESS"
    CHATTING = "CHATTING"


def is_exit_command(message: str) -> bool:
    """Check if message is a command to end/reset session"""
    exit_commands = ['exit', 'quit', 'end', 'stop', 'restart',
                     'reset', 'new', 'change business', 'switch business']
    return message.lower().strip() in exit_commands


def find_business_by_id(business_id: str) -> dict:
    """Find business by exact ID match"""
    return business_collection.find_one({"business_id": business_id})


def find_business_by_name(search_term: str, threshold: float = 0.6) -> dict:
    """
    Find business by name using fuzzy matching
    Returns the closest match if similarity >= threshold
    """
    businesses = list(business_collection.find({}))

    if not businesses:
        return None

    best_match = None
    best_ratio = 0

    search_term_lower = search_term.lower().strip()

    for business in businesses:
        business_name = business.get("businessName", "").lower().strip()

        # Calculate similarity ratio
        ratio = SequenceMatcher(None, search_term_lower, business_name).ratio()

        if ratio > best_ratio:
            best_ratio = ratio
            best_match = business

    # Return match only if similarity meets threshold
    if best_ratio >= threshold:
        logger.info(
            f"Found business match: '{best_match.get('businessName')}' with {best_ratio:.2%} similarity")
        return best_match

    logger.info(
        f"No business match found for '{search_term}' (best: {best_ratio:.2%})")
    return None
