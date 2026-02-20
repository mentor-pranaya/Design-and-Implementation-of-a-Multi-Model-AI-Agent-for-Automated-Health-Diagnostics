UNIT_ALIASES = {
    "mg per dl": "mg/dL",
    "mg per dL": "mg/dL",
    "mg/dl": "mg/dL",
    "milligrams per deciliter": "mg/dL",
    "g per dl": "g/dL",
    "g/dl": "g/dL",
    "cells/ul": "cells/uL",
    "cells/µl": "cells/uL",
    "cells/uL": "cells/uL",
    "mmhg": "mmHg",
    "mm hg": "mmHg",
}


def normalize_unit(raw_unit: str) -> str:
    if not raw_unit:
        return raw_unit
    key = raw_unit.strip().lower()
    return UNIT_ALIASES.get(key, raw_unit)
