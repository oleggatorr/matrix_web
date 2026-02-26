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
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import FileResponse


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


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.png")


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
    next_task_id = user.active_task
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

    # Устанавливаем время начала
    user.start_time = datetime.utcnow()
    db.commit()

    # Переходим на первое задание
    first_pass_code = TASKS.get(1, {}).get("key")
    if not first_pass_code:
        raise HTTPException(status_code=404)
    
    return RedirectResponse(
        url = f"/tasks/1?pass_code={TASKS.get(1).get('key')}",
        status_code=303
    )


@app.get("/list", response_class=HTMLResponse)
async def show_list(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.username != "admin").order_by(User.id.asc()).all()
    
    users_data = []
    for user in users:
        task_tracker = TaskStemps(user.solved_tasks or 0)
        tasks_status = {i: task_tracker.get_task(i) for i in range(1, 19)}
        solved_count = sum(1 for i in range(1, 19) if task_tracker.get_task(i))
        
        # Явно извлекаем значения через getattr() — безопасно, если колонки ещё не в БД
        users_data.append({
            'id': user.id,
            'username': user.username,
            'participants_full_names': user.participants_full_names,
            'email': user.email,
            'phone': user.phone,
            'photo_path': user.photo_path,
            'start_time': user.start_time,
            'end_time': user.end_time,
            'solved_tasks': user.solved_tasks,
            'school': getattr(user, 'school', None),   # ← безопасно
            'city': getattr(user, 'city', None),        # ← безопасно
            'tasks': tasks_status,
            'solved_count': solved_count,
        })
    
    return templates.TemplateResponse("list.html", {
        "request": request, 
        "users": users_data
    })


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# В main.py, в роуте @app.post("/login")
@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == username,
        User.password == password
    ).first()

    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный логин или пароль"
        })

    response = RedirectResponse(url="/", status_code=303)
    
    # 🔸 Если админ — перенаправляем в админку
    if user.username == "admin":
        response = RedirectResponse(url="/admin", status_code=303)
    
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
    pass_code: int,
    db: Session = Depends(get_db)
):
   
    user_id = request.cookies.get("user_id")
    if not user_id or not user_id.isdigit():
        return RedirectResponse(url="/login")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login")

    if pass_code != FINISH_CODE:
        raise HTTPException(status_code=404)

    if user.end_time == None:
        user.end_time = datetime.utcnow()
        db.commit()
        

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
    filename =f"tasks/{TASKS.get(task_id).get('file')}"
    
    if task_id: 
        if task_id == 1:
            
            return templates.TemplateResponse(filename, context)
        elif task_id == 2:
            
            return templates.TemplateResponse(filename, context)
        elif task_id == 3:
            
            
            return templates.TemplateResponse(filename, context)
        elif task_id == 4:

            
            return templates.TemplateResponse(filename, context)
        elif task_id == 5:

            
            return templates.TemplateResponse(filename, context)
        elif task_id == 6:

            
            return templates.TemplateResponse(filename, context)
        elif task_id == 7:

            
            return templates.TemplateResponse(filename, context)
        elif task_id == 8:

            
            return templates.TemplateResponse(filename, context)
        elif task_id == 9:

            
            return templates.TemplateResponse(filename, context)
        elif task_id == 10:

            
            return templates.TemplateResponse(filename, context)
        elif task_id == 11:

            
            return templates.TemplateResponse(filename, context)
        elif task_id == 12:
            
            return templates.TemplateResponse(filename, context)
        elif task_id == 13:
            
            return templates.TemplateResponse(filename, context)
        elif task_id == 14:
            
            return templates.TemplateResponse(filename, context)
        elif task_id == 15:
           
            return templates.TemplateResponse(filename, context)
        elif task_id == 16:

            return templates.TemplateResponse(filename, context)
        elif task_id == 17:

            return templates.TemplateResponse(filename, context)
        elif task_id == 18:

            return templates.TemplateResponse(filename, context)
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

        
        return templates.TemplateResponse(
            f"/tasks/{TASKS.get(task_id).get('file')}",
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
    school: str = Form(...),        # ← ОБЯЗАТЕЛЬНОЕ поле
    city: str = Form(...),          # ← ОБЯЗАТЕЛЬНОЕ поле
    db: Session = Depends(get_db)
):
    errors = {}
    
    # 0. Валидация обязательных полей (дополнительная проверка на уровне Python)
    if not school or not school.strip():
        errors["school"] = "Поле 'Школа' обязательно для заполнения"
    if not city or not city.strip():
        errors["city"] = "Поле 'Город' обязательно для заполнения"
    
    # 1. Проверка уникальности названия команды
    if db.query(User).filter(User.username == username).first():
        errors["username"] = "Команда с таким названием уже существует"
    
    # Если есть ошибки — возвращаем форму с данными
    if errors:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "errors": errors,
            "form_data": {
                "username": username,
                "participants_full_names": participants_full_names,
                "email": email,
                "phone": phone,
                "school": school,      # ← сохранить в form_data
                "city": city           # ← сохранить в form_data
            }
        })

    # 2. Обработка фото
    photo_path = None
    if photo and photo.filename:
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
        school=school,                # ← добавить в БД
        city=city,                    # ← добавить в БД
        photo_path=photo_path,
        start_time=None,
        end_time=None,
        solved_tasks=0,
        active_task=-1,
        password=password
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

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Страница не найдена"},
            status_code=404
        )
    elif exc.status_code == 403:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": exc.detail or "Доступ запрещён"},
            status_code=403
        )
    # Для других ошибок можно вернуть JSON или шаблон
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)  # ваша функция проверки
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


@app.get("/admin/tasks", response_class=HTMLResponse)
async def admin_tasks_list(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    
    from tasks_config import TASKS
    
    tasks = []
    for tid, config in sorted(TASKS.items()):
        tasks.append({
            "id": tid,
            "title": config.get("title", f"Задание {tid}"),
            "key": config.get("key", "???"),
            "expected": config.get("expected", {})
        })
    
    return templates.TemplateResponse("admin/tasks.html", {
        "request": request,
        "tasks": tasks
    })

# Список пользователей
@app.get("/admin/users", response_class=HTMLResponse)
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
    solved_tasks_bin: str = Form(""),
    active_task: int = Form(-1),
    school: str = Form(...),        # ← ОБЯЗАТЕЛЬНОЕ поле
    city: str = Form(...),          # ← ОБЯЗАТЕЛЬНОЕ поле
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

    # Обработка битовой маски задач
    if solved_tasks_bin.strip():
        bin_str = ''.join(c for c in solved_tasks_bin if c in '01')
        if bin_str:
            try:
                user.solved_tasks = int(bin_str, 2)
            except ValueError:
                pass
        else:
            user.solved_tasks = 0
    else:
        user.solved_tasks = solved_tasks

    # Обновляем остальные поля
    user.username = username
    user.password = password
    user.participants_full_names = participants_full_names
    user.email = email
    user.phone = phone
    user.school = school          # ← добавить
    user.city = city              # ← добавить
    user.active_task = active_task

    # Обработка времени
    user.start_time = datetime.fromisoformat(start_time) if start_time else None
    user.end_time = datetime.fromisoformat(end_time) if end_time else None

    db.commit()
    db.refresh(user)

    return RedirectResponse(url="/admin/users", status_code=303)

@app.post("/admin/delete/{user_id}")
async def admin_delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    require_admin(request, db)
    
    if str(user_id) == request.cookies.get("user_id"):
        raise HTTPException(status_code=400, detail="Нельзя удалить самого себя")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)

    # 🔸 Удаляем файл фото, если он есть
    if user.photo_path:
        photo_full_path = Path("static") / user.photo_path
        if photo_full_path.exists():
            photo_full_path.unlink()  # удаляет файл

    db.delete(user)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)

# Тестовая страница (можно удалить в продакшене)
@app.get("/test", response_class=HTMLResponse)
async def get_register_page(request: Request):
    """Отображение страницы регистрации"""
    return templates.TemplateResponse(
        "tasks/task0.html",
        {
            "request": request,
        }
    )