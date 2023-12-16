import random
import string
from datetime import date
from typing import Any, Dict


async def generate_data(
        constant: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Generate Dummy Data"""
    return {
        'id': ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        ),
        'type': random.choices(['normal', 'special', 'rare']),
        'create_date': f"{date.today():%Y-%m-%d}",
        'value': random.randrange(10, 100),
        **(constant or {}),
    }
