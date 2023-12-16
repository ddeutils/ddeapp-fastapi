import json.decoder

import pydantic
from fastapi import Request, HTTPException, status
from app.models import ADFObject


async def parameters(request: Request) -> ADFObject:
    """Mapping json data from request to ProcessObject model
        - P_PRCS_OBJ: Union[str, dict]
        - P_LD_ID: str
    """
    try:
        data = await request.json()
        return ADFObject.parse_obj(data)
    except json.decoder.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Json decoder error from parsing data to ADFObject."
        )
    except pydantic.ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Process object does not valid with model."
        )
