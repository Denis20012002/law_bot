from typing import Annotated

from fastapi import APIRouter, Depends, Form, Path, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import starlette.status as status

from .deps import product_repo, category_repo
from database.repo import ProductRepo, CategoryRepo


templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/product", response_class=HTMLResponse)
async def product_list(
    request: Request,
    service: Annotated[ProductRepo, Depends(product_repo)],
):
    items = service.get_all()

    context = {
        "items": items,
    }

    return templates.TemplateResponse(
        request=request, name="product/list.html", context=context
    )


@router.get("/product/add")
async def product_add(
    request: Request,
    cat_service: Annotated[CategoryRepo, Depends(category_repo)],
):
    klass_items = cat_service.get_all()
    context = {"cats": klass_items}
    return templates.TemplateResponse(
        request=request, name="product/add.html", context=context
    )


@router.post("/product/add")
async def add_org(
    service: Annotated[ProductRepo, Depends(product_repo)],
    name: str = Form(...),
    price: int = Form(...),
    description: str = Form(...),
    category_id: int = Form(...),
    cnt: int = Form(...)
):
    service.add_item(
        {
            "name": name,
            "price": price,
            "description": description,
            "category_id": category_id,
            "cnt": cnt,
        }
    )

    return RedirectResponse(url="/product", status_code=status.HTTP_302_FOUND)
