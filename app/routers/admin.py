from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import require_admin, get_storage_dep, User
from app.storage import TaskStorage
from collections import Counter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
async def get_stats(
    admin: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage_dep)
):
    all_tasks = storage.get_all_tasks()
    by_status = Counter(task.status.value for task in all_tasks)
    
    return {
        "total_tasks": len(all_tasks),
        "by_status": dict(by_status)
    }

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_task(
    task_id: int,
    admin: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage_dep)
):
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")