# 智学伴侣 · 安全设计

## 1. 安全目标

| 目标 | 说明 |
|------|------|
| 身份认证 | 只有合法注册用户才能访问受保护资源 |
| 权限隔离 | 学生无法操作教师接口，教师无法查看他人课程 |
| 数据隔离 | 学生只能看到已加入课程的数据 |
| 密码安全 | 密码不以明文或弱哈希形式存储 |
| API Key 保护 | MiniMax API Key 不出现在前端或日志 |
| 文件安全 | 上传文件类型和大小受限，防止恶意上传 |

---

## 2. 认证方案

### 2.1 JWT（JSON Web Token）

**签发**：`POST /api/auth/login` 验证密码成功后签发

**算法**：HS256（HMAC-SHA256）

**有效期**：24 小时（可通过 `access_token_expire_minutes` 配置）

**Payload 结构**：

```json
{
  "sub": "user_id",
  "role": "student",
  "exp": 1234567890
}
```

**密钥管理**：`secret_key` 通过环境变量注入，默认值 `change_this_to_a_long_random_string` 仅供开发使用，生产环境必须替换。

### 2.2 Token 传递

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**存储**：前端存储在 `localStorage`（不存 httpOnly cookie，不支持 SSR 的 SPA 折中方案）。  
**风险**：XSS 攻击可读取 localStorage。缓解措施：避免引入不可信三方脚本，启用 CSP。

### 2.3 Token 验证

```python
def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
```

验证失败（过期、签名错误）时 `JWTError` 被捕获，返回 401。

### 2.4 自动登出

前端响应拦截器：收到 401 时清除本地 token，用户需重新登录：

```typescript
if (error.response?.status === 401) {
  localStorage.removeItem('token')
}
```

---

## 3. 密码安全

### 3.1 哈希算法

使用 **bcrypt**（行业标准），自动生成随机 salt：

```python
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
```

**特性**：
- 内置 salt（不同密码不同哈希，相同密码每次结果不同）
- 计算成本可调（`gensalt()` 默认 cost factor 12）
- 抵抗彩虹表攻击

### 3.2 密码不出现在日志

`login` 接口只记录用户名，不记录密码；响应不返回 `password_hash` 字段。

---

## 4. 权限模型

### 4.1 三层权限检查

```
层级 1：是否登录（JWT 合法）
    ↓
层级 2：角色匹配（role == student 或 teacher）
    ↓
层级 3：资源归属（课程/作业/提交是否属于当前用户）
```

### 4.2 角色依赖注入

```python
# auth_service.py

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证信息")
    token = authorization[len("Bearer "):]
    payload = decode_token(token)          # 失败抛 401
    user = db.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def require_student(current_user = Depends(get_current_user)) -> User:
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅限学生访问")
    return current_user


def require_teacher(current_user = Depends(get_current_user)) -> User:
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅限教师访问")
    return current_user
```

### 4.3 资源归属校验

```python
# course_service.py

def _require_enrollment(course_id: str, student_id: str, db: Session):
    """学生必须已加入课程，否则 403"""
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == student_id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="未加入该课程")


def _require_teacher_course(course_id: str, teacher_id: str, db: Session):
    """课程必须属于该教师，否则 404（不暴露课程存在）"""
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == teacher_id,
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
```

**设计意图**：教师操作他人课程时返回 404（不告知存在），防止枚举攻击；学生未加入课程时返回 403。

---

## 5. API Key 保护

### 5.1 存储策略

```bash
# backend/.env（不提交到 git，.gitignore 已配置）
MINIMAX_API_KEY=sk-xxxxxxxxxx
MINIMAX_GROUP_ID=xxxxxxxxxx
SECRET_KEY=your-long-random-secret-key
```

### 5.2 调用链路

```
前端 → FastAPI 后端 → MiniMax API
```

前端**从不直接调用** MiniMax，所有大模型请求均经后端中转。  
`minimax_client.py` 从 `settings` 读取 Key，不在日志或响应中输出。

### 5.3 .gitignore 保护

```gitignore
backend/.env
backend/.env.local
backend/.env.*.local
backend/chroma_db/       # 向量库数据不提交
```

---

## 6. 文件上传安全

### 6.1 类型白名单

```python
allowed_extensions: list[str] = ["pdf", "txt", "doc", "docx"]
```

后端校验扩展名（不信任 Content-Type 头），不在白名单内拒绝。

### 6.2 大小限制

```python
max_upload_bytes: int = 10 * 1024 * 1024  # 10 MB
```

### 6.3 文件名处理

上传文件不使用原始文件名，改为 `section_material_{uuid}.{ext}` 格式，防止路径穿越攻击：

```python
fname = f"section_material_{uuid.uuid4()}.{ext}"
fpath = os.path.join(settings.upload_dir, fname)
```

---

## 7. 输入校验

### 7.1 Pydantic 自动校验

所有请求体通过 Pydantic 模型定义，字段类型、必填性、约束自动校验：

```python
class StudentRegisterRequest(BaseModel):
    username: str
    name: str
    class_name: str
    password: str
```

校验失败时 FastAPI 自动返回 422 Unprocessable Entity。

### 7.2 业务层防御

- 成绩数据只使用 `confirmed=True` 的批改结果（防止 AI 数据直接生效）
- 学习计划调整时验证 `plan_id` 属于当前学生
- 简答题 AI 打分不超过题目满分：`min(float(score), question.score)`

---

## 8. 异常处理与信息泄露

### 8.1 全局 500 处理

```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"code": "INTERNAL_ERROR", "message": str(exc)}},
    )
```

**注意**：`str(exc)` 可能泄露内部错误细节，生产环境建议改为固定 message：

```python
"message": "服务器内部错误，请稍后重试"
```

### 8.2 AI 服务失败降级

RAG 检索、向量化、C++ 扩展等外部依赖失败时，均 `try/except` 捕获后静默降级：

```python
except Exception:
    logger.warning("RAG 检索失败，降级为无上下文回答", exc_info=True)
    return []
```

不将内部错误暴露给前端，主流程不中断。

---

## 9. CORS 配置

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 开发阶段
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**生产环境**必须收窄 `allow_origins`：

```python
allow_origins=["https://your-domain.com"]
```

---

## 10. 安全检查清单

| 项目 | 状态 | 说明 |
|------|------|------|
| 密码 bcrypt 哈希 | ✅ | `bcrypt.gensalt()` 默认 cost 12 |
| JWT 鉴权 | ✅ | HS256，24h 有效期 |
| 角色权限隔离 | ✅ | `require_student` / `require_teacher` |
| 课程归属校验 | ✅ | `_require_enrollment` / `_require_teacher_course` |
| API Key 不出前端 | ✅ | 环境变量，`.gitignore` 保护 |
| 文件类型白名单 | ✅ | `allowed_extensions` |
| 文件大小限制 | ✅ | `max_upload_bytes = 10MB` |
| 文件名随机化 | ✅ | `uuid4()` 替代原始文件名 |
| 向量库数据不提交 | ✅ | `backend/chroma_db/` 在 `.gitignore` |
| CORS 开发/生产区分 | ⚠️ | 当前 `allow_origins=["*"]`，生产需收窄 |
| 全局 500 信息泄露 | ⚠️ | 生产需隐藏 `str(exc)` |
| Token 刷新机制 | ❌ | 无 refresh token，到期需重新登录 |
| 请求频率限制 | ❌ | 无 rate limiting，AI 接口高频调用有成本风险 |
| HTTPS 强制 | ❌ | 应在 Nginx/反代层配置 |
