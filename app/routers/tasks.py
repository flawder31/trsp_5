from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from app.schemas import TaskCreate, Task, TaskStatusUpdate, TaskStatus
from app.dependencies import get_current_user, get_storage_dep, User
from app.storage import TaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage_dep)
):
    return storage.create(task_data.model_dump(), current_user.id)

@router.get("/", response_model=List[Task])
async def get_tasks(
    status: Optional[str] = None,
    min_priority: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage_dep)
):
    return storage.get_user_tasks(current_user.id, status, min_priority)

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage_dep)
):
    task = storage.get_task(task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}/status", response_model=Task)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage_dep)
):
    task = storage.get_task(task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated = storage.update_status(task_id, status_update.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage_dep)
):
    task = storage.get_task(task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")