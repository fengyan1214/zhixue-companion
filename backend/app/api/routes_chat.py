"""智能问答路由（课程路径版）"""
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import chat_service as svc
from app.services.auth_service import require_student

router = APIRouter(tags=["智能问答"])


def _ok(data, message="ok"):
    return {"success": True, "data": data, "message": message}


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None
    section_id: str | None = None


@router.post("/student/courses/{course_id}/chat")
def send_message(
    course_id: str,
    req: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(require_student),
    db: Session = Depends(get_db),
):
    result = svc.send_message(
        course_id, current_user.id, req.question, req.session_id, req.section_id, db
    )
    # 取出写入上下文，调度后台任务，不阻塞响应
    save_ctx = result.pop("_save_ctx")
    background_tasks.add_task(svc.save_messages, result["session_id"], save_ctx)
    return _ok(result)


@router.post("/student/courses/{course_id}/chat/stream")
def stream_message(
    course_id: str,
    req: ChatRequest,
    current_user=Depends(require_student),
    db: Session = Depends(get_db),
):
    """
    流式问答接口（SSE）。
    响应为 text/event-stream，逐事件推送：
      - meta：首个事件，包含 session_id、rag_used、references
      - delta：文本片段，逐字推送
      - done：流结束标志
      - error：出错时推送（可选）
    消息在流结束后由服务层同步持久化，客户端无需额外请求。
    """
    return StreamingResponse(
        svc.stream_message(
            course_id, current_user.id, req.question, req.session_id, req.section_id, db
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # 禁止 Nginx 缓冲，确保逐行推送
        },
    )


@router.get("/student/courses/{course_id}/chat/sessions")
def list_sessions(course_id: str, section_id: str | None = None,
                   current_user=Depends(require_student), db: Session = Depends(get_db)):
    return _ok(svc.list_sessions(course_id, current_user.id, section_id, db))


@router.get("/student/courses/{course_id}/chat/sessions/{session_id}/messages")
def get_session_messages(course_id: str, session_id: str,
                          current_user=Depends(require_student), db: Session = Depends(get_db)):
    return _ok(svc.get_session_messages(course_id, session_id, current_user.id, db))
