from typing import Annotated

from fastapi import APIRouter, Depends, Form, Path, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import starlette.status as status

from .deps import answer_repo
from database.repo import AnswerRepo

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/answers", response_class=HTMLResponse)
async def answers_list(
    request: Request,
    service: Annotated[AnswerRepo, Depends(answer_repo)],
):
    """Список всех вопросов"""
    items = service.get_all()

    context = {
        "items": items,
    }

    return templates.TemplateResponse(
        request=request, name="answer/list.html", context=context
    )


@router.get("/answers/{answer_id}", response_class=HTMLResponse)
async def answer_detail(
    request: Request,
    answer_id: int = Path(...),
    service: Annotated[AnswerRepo, Depends(answer_repo)] = None,
):
    """Детальная страница вопроса с формой для ответа"""
    if service is None:
        service = AnswerRepo()
    
    item = service.get_by_id(answer_id)
    
    if not item:
        return RedirectResponse(url="/answers", status_code=status.HTTP_302_FOUND)

    context = {
        "item": item,
    }

    return templates.TemplateResponse(
        request=request, name="answer/detail.html", context=context
    )


@router.post("/answers/{answer_id}/reply")
async def reply_to_answer(
    answer_id: int = Path(...),
    answer_text: str = Form(...),
    service: Annotated[AnswerRepo, Depends(answer_repo)] = None,
):
    """Обработка ответа на вопрос"""
    if service is None:
        service = AnswerRepo()
    
    # Обновляем ответ в базе данных
    updated_answer = service.update_answer(answer_id, answer_text)
    
    if updated_answer:
        # Отправляем сообщение пользователю в Telegram
        try:
            from presentation.tgbot.main import bot
            await bot.send_message(
                chat_id=updated_answer["user_id"],
                text=f"📩 Ответ на ваш вопрос:\n\n"
                     f"❓ Ваш вопрос: {updated_answer['question_text']}\n\n"
                     f"💬 Ответ: {answer_text}"
            )
        except Exception as e:
            # Логируем ошибку, но не прерываем процесс
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error sending message to user {updated_answer['user_id']}: {e}")

    return RedirectResponse(url="/answers", status_code=status.HTTP_302_FOUND)
