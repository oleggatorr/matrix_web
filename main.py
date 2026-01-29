# main.py
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, Base
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from TaskStemps import TaskStemps
from starlette.exceptions import HTTPException as StarletteHTTPException
from tasks_config import TASKS

# Создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Код завершения
FINISH_CODE = 12345

# Символы для задач (можно вынести в конфиг)
SYMBOLS = [
    {"image": "/static/images/phone2.png", "message": "Сообщение 1", "id": "0"},
]

# Dependency для базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def update_user_progress(db: Session, user: User, task_id: int, done: bool):
    """Обновляет прогресс пользователя после попытки решить задачу."""
    ts = TaskStemps()
    ts.set_task(task_id, done)
    user.solved_tasks = ts.value
    user.active_task = task_id
    db.commit()  # user уже отслеживается сессией


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id or not user_id.isdigit():
        return RedirectResponse(url="/login")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login")

    # Если сессия не начата — показываем домашнюю страницу
    if user.start_time is None:
        return templates.TemplateResponse(
            "home.html",
            {"request": request, "username": user.username, "grade": user.grade, "task_id": 0}
        )

    # Если уже завершил — на финиш
    if user.end_time is not None:
        return RedirectResponse(url=f"/finish?pass_code={FINISH_CODE}")

    # Иначе — перенаправляем на следующую задачу
    next_task_id = user.solved_tasks + 1
    if next_task_id > max(TASKS.keys()):
        return RedirectResponse(url=f"/finish?pass_code={FINISH_CODE}")

    next_pass_code = TASKS.get(next_task_id, {}).get("key")
    if not next_pass_code:
        raise HTTPException(status_code=404)

    return RedirectResponse(url=f"/tasks/{next_task_id}?pass_code={next_pass_code}")


@app.post("/")
async def start_session(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id or not user_id.isdigit():
        return RedirectResponse(url="/login", status_code=303)

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    user.start_time = datetime.utcnow()
    db.commit()

    first_pass_code = TASKS.get(1, {}).get("key")
    return RedirectResponse(url=f"/tasks/1?pass_code={first_pass_code}", status_code=303)


@app.get("/list", response_class=HTMLResponse)
async def show_list(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("list.html", {"request": request, "users": users})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    grade: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()

    if user:
        user.grade = grade
        db.commit()
        db.refresh(user)
    else:
        new_user = User(
            username=username,
            grade=grade,
            start_time=None,
            end_time=None,
            solved_tasks=0,
            active_task=-1
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id), max_age=86400)
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("user_id")
    return response


@app.get("/finish", response_class=HTMLResponse)
async def finish_page(
    request: Request,
    db: Session = Depends(get_db)
):
    print(1)
    user_id = request.cookies.get("user_id")
    if not user_id or not user_id.isdigit():
        return RedirectResponse(url="/login")
    print(2)
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("finish.html", {"request": request, "username": user.username})


@app.get("/tasks/{task_id}", response_class=HTMLResponse)
async def task_page(
    request: Request,
    task_id: int,
    pass_code: int,
    db: Session = Depends(get_db)
):
    # Проверка pass_code
    task_config = TASKS.get(task_id)
    if not task_config or pass_code != task_config.get("key"):
        raise HTTPException(status_code=404)

    # Аутентификация пользователя
    user_id = request.cookies.get("user_id")
    if not user_id or not user_id.isdigit():
        return RedirectResponse(url="/login")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login")

    # Уже завершил — на финиш
    if user.end_time is not None:
        return RedirectResponse(url=f"/finish?pass_code={FINISH_CODE}")

    # Превышен номер задачи
    if task_id > max(TASKS.keys()):
        return RedirectResponse(url=f"/finish?pass_code={FINISH_CODE}")

    # Рендер шаблонов
    base_context = {
        "request": request,
        "username": user.username,
        "task_id": task_id,
        "pass_code": pass_code,
        "error": None
    }

    match task_id:
        case 1:
            context = {**base_context}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 2:
            context = {**base_context, "symbols": TASKS.get(task_id).get("SYMBOLS"), "correct_symbol_id": "0"}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 3:
            
            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 4:

            context = {**base_context, "symbols": TASKS.get(task_id).get("SYMBOLS")}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 5:

            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 6:

            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 7:

            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 8:

            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 9:

            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 10:

            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 11:

            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 12:

            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 13:

            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 14:

            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 15:

            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case 16:

            context = {**base_context, "symbols": SYMBOLS}
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        case _:
            raise HTTPException(status_code=404)


@app.post("/tasks/{task_id}", response_class=HTMLResponse)
async def task_submit(
    request: Request,
    task_id: int,
    db: Session = Depends(get_db)
):
    # Получаем пользователя
    user_id = request.cookies.get("user_id")
    if not user_id or not user_id.isdigit():
        return RedirectResponse(url="/login", status_code=303)
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    # Получаем конфиг задачи
    task_config = TASKS.get(task_id)
    if not task_config:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    # Анализируем форму
    form_data = await request.form()
    answers = {k: v.strip().upper() for k, v in form_data.items()}

    # Определяем успех
    input_fields = task_config.get("input_fields", [])
    if not input_fields:
        success = True  # Пустая форма = успех
    else:
        expected = task_config.get("expected", {})
        success = all(answers.get(k) == v for k, v in expected.items())

    # Обновляем прогресс (всегда обновляем, даже при ошибке)
    update_user_progress(db, user, task_id, success)
    #print(success, answers, expected)
    # Если ответ правильный — всегда идём дальше
    if success:
        next_task_id = task_id + 1
        if next_task_id > max(TASKS.keys()):
            return RedirectResponse(url=f"/finish?pass_code={FINISH_CODE}", status_code=303)

        next_pass_code = TASKS.get(next_task_id, {}).get("key")
        if not next_pass_code:
            raise HTTPException(status_code=404)
        return RedirectResponse(
            url=f"/tasks/{next_task_id}?pass_code={next_pass_code}",
            status_code=303
        )

    # Если ответ НЕПРАВИЛЬНЫЙ
    can_pass = task_config.get("can_pass", False)  # по умолчанию — нельзя пройти

    if can_pass:
        # Пропускаем даже при ошибке (редко нужно)
        next_task_id = task_id + 1
        if next_task_id > max(TASKS.keys()):
            return RedirectResponse(url=f"/finish?pass_code={FINISH_CODE}", status_code=303)
        next_pass_code = TASKS.get(next_task_id, {}).get("key")
        if not next_pass_code:
            raise HTTPException(status_code=404)
        return RedirectResponse(
            url=f"/tasks/{next_task_id}?pass_code={next_pass_code}",
            status_code=303
        )
    else:
        # Остаёмся на текущей задаче с ошибкой
        current_pass_code = task_config.get("key")
        if not current_pass_code:
            raise HTTPException(status_code=404)

        # Подготавливаем контекст для шаблона
        base_context = {
            "request": request,
            "username": user.username,
            "task_id": task_id,
            "pass_code": current_pass_code,
            "error": task_config.get("error_message", "Неверный ответ."),
            "submitted": answers  # можно использовать в шаблоне для восстановления ввода
        }

        # Добавляем специфичные данные (если нужно)
        if task_id in {2,4}:
            base_context.update({
                "symbols": TASKS.get(task_id).get("SYMBOLS"),
                "correct_symbol_id": "0"  # или из конфига
            })
        elif task_id == 3:
            base_context["symbols"] = SYMBOLS

        return templates.TemplateResponse(
            f"tasks/task{task_id}.html",
            base_context
        )


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "username": "???", "task_id": "???"},
            status_code=404
        )
    raise exc


# Тестовая страница (можно удалить в продакшене)
@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    symbols = [
        {"id": "alpha", "image": "/static/images/phone.png"},
        {"id": "beta", "image": "/static/images/phone.png"},
        {"id": "omega", "image": "/static/images/phone.png"},
        {"id": "gamma", "image": "/static/images/phone.png"},
    ]
    return templates.TemplateResponse("tasks/task2.html", {
        "request": request,
        "username": "test_user",
        "task_id": 2,
        "symbols": symbols,
        "correct_symbol_id": "omega",
        "pass_code": "TEST_KEY"
    })