# main.py
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, Base
from auth_utils import get_password_hash, verify_password
from fastapi.staticfiles import StaticFiles
from datetime import datetime 


from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

tasks_keys = [7360, 5666, 2430, 2430, 1403, 2173, 2722, 3079, 4691, 4390]
finish_code = 12345

SYMBOLS = [
    {"image": "/static/images/phone.png", "message": "Сообщение 1"},
    {"image": "/static/images/phone.png", "message": "Сообщение 2"},
    {"image": "/static/images/phone.png", "message": "Сообщение 3"},
    {"image": "/static/images/phone.png", "message": "Сообщение 4"},
    {"image": "/static/images/phone.png", "message": "Сообщение 5"},
    {"image": "/static/images/phone.png", "message": "Сообщение 6"},
    {"image": "/static/images/phone.png", "message": "Сообщение 7"},
    {"image": "/static/images/phone.png", "message": "Сообщение 8"},
    {"image": "/static/images/phone.png", "message": "Сообщение 9"},
    {"image": "/static/images/phone.png", "message": "Сообщение 10"},
    {"image": "/static/images/phone.png", "message": "Сообщение 11"},
    {"image": "/static/images/phone.png", "message": "Сообщение 12"},
    {"image": "/static/images/phone.png", "message": "Сообщение 13"},
    {"image": "/static/images/phone.png", "message": "Сообщение 14"},
    {"image": "/static/images/phone.png", "message": "Сообщение 15"},
    {"image": "/static/images/phone.png", "message": "Сообщение 16"},
            ]

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    
    if not user_id or not user_id.isdigit():
        return RedirectResponse(url="/login")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login")
    
    if user.end_time is not None:
        return RedirectResponse(url="/finish")
    
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "username": user.username, "grade": user.grade, "task_id":0}
    )


@app.post("/")
async def start_session(request: Request, db: Session = Depends(get_db)):
    # Получаем user_id из cookie
    user_id = request.cookies.get("user_id")
    
    if not user_id or not user_id.isdigit():
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Сохраняем текущее время в start_time
    user.start_time = datetime.utcnow()  # или datetime.now() — см. примечание ниже
    db.commit()
    
    # Перенаправляем на первое задание
    return RedirectResponse(url="/tasks/1?pass_code="+str(tasks_keys[1]), status_code=303)


@app.get("/list", response_class=HTMLResponse)
async def show_list(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("list.html", {"request": request, "users": users})

# Страница входа (форма)
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, 
                                                     "username": "--------",
                                                     "task_id": 0})

# Обработка входа
@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    grade: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()

    if user:
        # Обновляем grade, если нужно
        user.grade = grade
        db.commit()
        db.refresh(user)  # чтобы убедиться, что id загружен
    else:
        # Создаём нового пользователя
        new_user = User(username=username, grade=grade, start_time=None, end_time=None)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # ← важно: получаем присвоенный id
        user = new_user

    # Сохраняем ID (целое число → строка для cookie)
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id), max_age=86400)  # 1 день
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("user_id")
    return response

@app.get("/finish", response_class=HTMLResponse)
async def finish_page(request: Request, db: Session = Depends(get_db), 
pass_code: int = None):
    if pass_code != finish_code:
        raise HTTPException(status_code=404)
    user_id = request.cookies.get("user_id")
    
    if not user_id or not user_id.isdigit():
        return RedirectResponse(url="/login")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login")
    
     # 🔹 Записываем время завершения, только если оно ещё не установлено
    if user.end_time is None:
        user.end_time = datetime.utcnow()  # или datetime.now() — зависит от твоего часового пояса
        db.add(user)
        db.commit()
        db.refresh(user)  # опционально — чтобы убедиться, что данные актуальны

    return templates.TemplateResponse(
        "finish.html",
        {"request": request, "username": user.username}
    )



@app.get("/tasks/{task}", response_class=HTMLResponse)
async def task_page(
    request: Request,
    task: int,               # ← path-параметр из URL
    pass_code: int = None,              # ← query-параметр ?pass_code=123
    db: Session = Depends(get_db)): 
    try:
        print(task, tasks_keys[task], pass_code, pass_code == tasks_keys[task])
        if  pass_code != tasks_keys[task]:
            raise HTTPException(status_code=404)
    except:
        raise HTTPException(status_code=404)
    

    user_id = request.cookies.get("user_id")
    
    if not user_id or not user_id.isdigit():
        return RedirectResponse(url="/login")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login")
    
    if user.end_time is not None:
        return RedirectResponse(url="/finish")


    match task:
        case 1: 
            return templates.TemplateResponse(
                "tasks/task1.html",
                {
                    "username":user.username,
                    "request": request,
                    "task_id": task,
                    "pass_code": pass_code,
                    "error" : None
                    
                }
            )
        case 2:
            return templates.TemplateResponse(
                "tasks/task2.html",
                {
                    "username":user.username,
                    "request": request,
                    "task_id": task,
                    "pass_code": pass_code,
                    "error" : None,
                    "symbols" : SYMBOLS
                }
            )
        case 3:
            return templates.TemplateResponse(
                "tasks/task2.html",
                {
                    "username":user.username,
                    "request": request,
                    "task_id": task,
                    "pass_code": pass_code,
                    "error" : None,
                    "symbols" : SYMBOLS
                }
            )
        case 4:
            return templates.TemplateResponse(
                "tasks/task2.html",
                {
                    "username":user.username,
                    "request": request,
                    "task_id": task,
                    "pass_code": pass_code,
                    "error" : None,
                    "symbols" : SYMBOLS
                }
            )
        case 5:
            return templates.TemplateResponse(
                "tasks/task2.html",
                {
                    "username":user.username,
                    "request": request,
                    "task_id": task,
                    "pass_code": pass_code,
                    "error" : None,
                    "symbols" : SYMBOLS
                }
            )
    return RedirectResponse(url="/invalid-path", status_code=200)


@app.post("/tasks/1", response_class=HTMLResponse)
async def task1_submit(request: Request, code: str = Form(...)):
    clean_code = code.strip().upper()
    
    if clean_code == "12345":
        # Успех → редирект на следующее задание
        return RedirectResponse(url="/tasks/2?pass_code="+str(tasks_keys[2]), status_code=303)
    else:
        # Ошибка → рендер той же страницы с ошибкой
        return templates.TemplateResponse("tasks/task1.html", {
            "request": request,
            "username": "guest",
            "task_id": 1,
            "symbols": SYMBOLS,
            "error": "Неверный код. Попробуй другой символ.",
            "code": code  # сохраняем введённое значение
        }, status_code=400)


@app.post("/tasks/2", response_class=HTMLResponse)
async def task2_submit(request: Request, code: str = Form(...)):
    clean_code = code.strip().upper()
    
    if clean_code == "12345":
        # Успех → редирект на следующее задание
        return RedirectResponse(url="/tasks/3?pass_code="+str(tasks_keys[3]), status_code=303)
    else:
        # Ошибка → рендер той же страницы с ошибкой
        return templates.TemplateResponse("tasks/task2.html", {
            "request": request,
            "username": "guest",
            "task_id": 1,
            "symbols": SYMBOLS,
            "error": "Неверный код. Попробуй другой символ.",
            "code": code  # сохраняем введённое значение
        }, status_code=400)


@app.post("/tasks/3", response_class=HTMLResponse)
async def task3_submit(request: Request, code: str = Form(...)):
    clean_code = code.strip().upper()
    
    if clean_code == "12345":
        # Успех → редирект на следующее задание
        return RedirectResponse(url="/tasks/4?pass_code="+str(tasks_keys[4]), status_code=303)
    else:
        # Ошибка → рендер той же страницы с ошибкой
        return templates.TemplateResponse("tasks/task3.html", {
            "request": request,
            "username": "guest",
            "task_id": 1,
            "symbols": SYMBOLS,
            "error": "Неверный код. Попробуй другой символ.",
            "code": code  # сохраняем введённое значение
        }, status_code=400)


@app.post("/tasks/4", response_class=HTMLResponse)
async def task4_submit(request: Request, code: str = Form(...)):
    clean_code = code.strip().upper()
    
    if clean_code == "12345":
        # Успех → редирект на следующее задание
        return RedirectResponse(url="/finish?pass_code="+str(finish_code), status_code=303)
    else:
        # Ошибка → рендер той же страницы с ошибкой
        return templates.TemplateResponse("tasks/task4.html", {
            "request": request,
            "username": "guest",
            "task_id": 5,
            "symbols": SYMBOLS,
            "error": "Неверный код. Попробуй другой символ.",
            "code": code  # сохраняем введённое значение
        }, status_code=400)


@app.post("/tasks/5", response_class=HTMLResponse)
async def task5_submit(request: Request, code: str = Form(...)):
    clean_code = code.strip().upper()
    
    if clean_code == "12345":
        # Успех → редирект на следующее задание
        return RedirectResponse(url="/tasks/7?pass_code="+str(tasks_keys[6]), status_code=303)
    else:
        # Ошибка → рендер той же страницы с ошибкой
        return templates.TemplateResponse("tasks/task5.html", {
            "request": request,
            "username": "guest",
            "task_id": 1,
            "symbols": SYMBOLS,
            "error": "Неверный код. Попробуй другой символ.",
            "code": code  # сохраняем введённое значение
        }, status_code=400)





@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "username": "???",      # или из сессии
                "task_id": "???"          # неизвестно — ставим ???
            },
            status_code=404
        )
    # Для других ошибок (403, 500 и т.д.) можно сделать аналогично
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)