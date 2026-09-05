from typing import Annotated

from fastapi import APIRouter, Depends, Form, Path, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import starlette.status as status

from .deps import category_repo
from database.repo import CategoryRepo


templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def cat_list(
    request: Request,
    service: Annotated[CategoryRepo, Depends(category_repo)],
):
    items = service.get_all()

    context = {
        "items": items,
    }

    return templates.TemplateResponse(
        request=request, name="category/list.html", context=context
    )


@router.get("/category/add")
async def category_add(
    request: Request,
):
    return templates.TemplateResponse(
        request=request, name="category/add.html",
    )


@router.post("/category/add")
async def add_org(
    service: Annotated[CategoryRepo, Depends(category_repo)],
    name: str = Form(...),
):
    service.add_item(
        {
            "name": name,
        }
    )

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
