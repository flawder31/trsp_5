# Task Management API

FastAPI приложение для управления задачами с WebSocket чатом и интеграционными тестами.

## Команды для запуска

### Локальный запуск
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или .venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
Запуск тестов
bash
pytest
Docker запуск
bash
docker compose up --build
API Endpoints
GET /health - проверка состояния

POST /tasks - создание задачи

GET /tasks - список задач

GET /tasks/{id} - получить задачу

PATCH /tasks/{id}/status - обновить статус

DELETE /tasks/{id} - удалить задачу

GET /users/me - текущий пользователь

GET /admin/stats - статистика (admin only)

WebSocket /ws/rooms/{room_id}?username={name} - WebSocket чат

Проверка после Docker запуска
bash
curl http://localhost:8000/tasks -H "X-User-Id: 10"