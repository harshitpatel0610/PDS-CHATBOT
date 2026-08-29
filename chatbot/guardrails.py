PDS_KEYWORDS = {
    "ration",
    "ration card",
    "pds",
    "public distribution system",
    "nfsa",
    "onorc",
    "fair price shop",
    "fps",
    "beneficiary",
    "food security",
    "antyodaya",
    "aay",
    "phh",
    "ration shop",
    "dealer",
    "subsidy",
}


def is_pds_related(user_message: str) -> bool:
    message = user_message.lower()

    return any(keyword in message for keyword in PDS_KEYWORDS)