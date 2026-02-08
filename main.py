# main.py
from fastapi import FastAPI, Request, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, Base, print_user
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from TaskStemps import TaskStemps
from starlette.exceptions import HTTPException as StarletteHTTPException
from tasks_config import TASKS
import os
from pathlib import Path
import uuid


# Создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


UPLOADS_DIR = Path("static/uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

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


def update_user_task(db: Session, user: User, task_id: int, done: bool):
    """Обновляет прогресс пользователя после попытки решить задачу."""
    ts = TaskStemps(user.solved_tasks)

    ts.set_task(task_id,done)
    user.solved_tasks = ts.value
    db.commit()  # user уже отслеживается сессией


def update_user_progress(db: Session, user: User, task_id: int):
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
            {"request": request, "username": user.username, "task_id": 0, "admin": user.username == 'admin'}
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


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id or not user_id.isdigit():
        return RedirectResponse(url="/login")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login")

    print(user.username == 'admin')
    print(121212)
    # Показываем домашнюю страницу
    return templates.TemplateResponse("home.html", {
        "request": request,
        "username": user.username,
        "admin": user.username == 'admin'
    })

@app.post("/")
async def start_session(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id or not user_id.isdigit():
        return RedirectResponse(url="/login", status_code=303)

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    # Устанавливаем время начала
    user.start_time = datetime.utcnow()
    db.commit()

    # Переходим на первое задание
    first_pass_code = TASKS.get(1, {}).get("key")
    if not first_pass_code:
        raise HTTPException(status_code=404)
    
    return RedirectResponse(
        url=f"/tasks/1?pass_code={first_pass_code}",
        status_code=303
    )


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
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == username,
        User.password == password  # ← сравнение в открытом виде
    ).first()

    if not user:
        # Ошибка: неверный логин или пароль
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный логин или пароль"
        })

    # Успешный вход
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
    update_user_progress(db, user, task_id)
    context = {**base_context, "symbols": TASKS.get(task_id).get("SYMBOLS",None),
                       "correct_symbol_id": TASKS.get(task_id).get("correct_symbol_id","0")}
    
    if task_id:
        if task_id == 1:
            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 2:
            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 3:
            
            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 4:

            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 5:

            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 6:

            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 7:

            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 8:

            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 9:

            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 10:

            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 11:

            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 12:
            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 13:
            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 14:
            
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 15:
           
            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 16:

            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        elif task_id == 17:

            return templates.TemplateResponse(f"tasks/task{task_id}.html", context)
        else:
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
    print(answers)
    if not input_fields:
        success = True  # Пустая форма = успех
    else:
        expected = task_config.get("expected", {})
        success = all(answers.get(k) == v for k, v in expected.items())

    # Обновляем прогресс (всегда обновляем, даже при ошибке)
    
    update_user_task(db, user, task_id, success)

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
        if TASKS.get(task_id).get("SYMBOLS", None) != None:
            base_context.update({
                "symbols" : TASKS.get(task_id).get("SYMBOLS"),
                "correct_symbol_id" : TASKS.get(task_id).get("correct_symbol_id", 0)# или из конфига
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
@app.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    """Отображение страницы регистрации"""
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "errors": None,
            "form_data": None,
            "success": False
        }
    )


@app.post("/register", response_class=HTMLResponse)
async def register_post(
    request: Request,
    username: str = Form(...),
    participants_full_names: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    photo: UploadFile = File(None),
    password: str = Form(...),
    db: Session = Depends(get_db)

):
    # 1. Проверка уникальности названия команды
    if db.query(User).filter(User.username == username).first():
        errors = {"username": "Команда с таким названием уже существует"}
        return templates.TemplateResponse("register.html", {
            "request": request,
            "errors": errors,
            "form_data": {
                "username": username,
                "participants_full_names": participants_full_names,
                "email": email,
                "phone": phone
            }
        })

    # 2. Обработка фото
    photo_path = None
    if photo and photo.filename:
        # Проверяем расширение
        ext = Path(photo.filename).suffix.lower()
        if ext in {".png", ".jpg", ".jpeg", ".gif"}:
            filename = f"team_{uuid.uuid4().hex}{ext}"
            filepath = UPLOADS_DIR / filename
            with open(filepath, "wb") as f:
                f.write(await photo.read())
            photo_path = f"uploads/{filename}"

    # 3. Создание записи
    new_team = User(
        username=username,
        participants_full_names=participants_full_names,
        email=email,
        phone=phone,
        photo_path=photo_path,
        start_time=None,
        end_time=None,
        solved_tasks=0,
        active_task=-1,
        password = password
    )
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    # 4. Устанавливаем куку и показываем успех
    response = RedirectResponse(url="/login", status_code=303)
    return response


# Админка — проверка прав
def require_admin(request: Request, db: Session):
    user_id = request.cookies.get("user_id")
    if not user_id or not user_id.isdigit():
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or user.username != "admin":
        raise HTTPException(status_code=403, detail="Только администратор")
    return user

# Список пользователей
@app.get("/admin", response_class=HTMLResponse)
async def admin_list(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    users = db.query(User).all()
    return templates.TemplateResponse("admin/list.html", {
        "request": request,
        "users": users
    })

# Форма редактирования
@app.get("/admin/edit/{user_id}", response_class=HTMLResponse)
async def admin_edit_form(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    require_admin(request, db)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return templates.TemplateResponse("admin/edit.html", {
        "request": request,
        "user": user,
        "solved_tasks": int(bin(user.solved_tasks)[2:][::-1])
    })

# Обработка редактирования
@app.post("/admin/edit/{user_id}", response_class=HTMLResponse)
async def admin_edit_submit(

    request: Request,
    user_id: int,
    username: str = Form(...),
    password: str = Form(...),
    participants_full_names: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    photo: UploadFile = File(None),
    start_time: str = Form(""),
    end_time: str = Form(""),
    solved_tasks: int = Form(0),
    active_task: int = Form(-1),
    db: Session = Depends(get_db)
):
    require_admin(request, db)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)

    # Обновляем фото (если загружено)
    if photo and photo.filename:
        ext = Path(photo.filename).suffix.lower()
        if ext in {".png", ".jpg", ".jpeg", ".gif"}:
            filename = f"team_{uuid.uuid4().hex}{ext}"
            filepath = UPLOADS_DIR / filename
            with open(filepath, "wb") as f:
                f.write(await photo.read())
            user.photo_path = f"uploads/{filename}"

    # Обновляем остальные поля
    user.username = username
    user.password = password
    user.participants_full_names = participants_full_names
    user.email = email
    user.phone = phone
    user.solved_tasks = solved_tasks
    user.active_task = active_task

    # Обработка времени
    user.start_time = datetime.fromisoformat(start_time) if start_time else None
    user.end_time = datetime.fromisoformat(end_time) if end_time else None

    db.commit()
    db.refresh(user)

    return RedirectResponse(url="/admin", status_code=303)



# Тестовая страница (можно удалить в продакшене)
@app.get("/test", response_class=HTMLResponse)
async def get_register_page(request: Request):
    """Отображение страницы регистрации"""
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
        }
    )