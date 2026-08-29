from enum import Enum


class Intent(Enum):
    PDS = "pds"
    NON_PDS = "non_pds"
    UNKNOWN = "unknown"