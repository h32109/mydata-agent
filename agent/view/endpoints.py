from fastapi import APIRouter, status, Request
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from agent.utils import get_path_from_root

router = APIRouter()

templates = Jinja2Templates(directory=get_path_from_root("view/templates"))


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse
)
def get_index(request: Request):
    return templates.TemplateResponse(request, "index.html")
