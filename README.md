# ТРСП Контрольная работа №5 Болотских Р.И. ЭФБО-03-24

## Команды для запуска

### Локальный запуск
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

Запуск тестов
python -m pytest

Docker запуск
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
