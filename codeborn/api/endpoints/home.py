from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse


router = APIRouter()


@router.get('/', include_in_schema=False)
async def root(request: Request) -> RedirectResponse:
    """Redirect user to docs."""
    return RedirectResponse(url=request.app.docs_url)
