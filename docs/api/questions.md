# 提问 API

> 基础路径：`/api/courses/{course_id}/questions`
>
> 所有接口均需携带 JWT 令牌。

---

## 说明

提问功能允许学生在课程内向教师提问，支持**公开**和**私密**两种可见性：

- **公开（public）**：课程内所有师生均可查看该问题及回答，方便共同学习；
- **私密（private）**：仅提问学生本人和该课程教师可见，适合不希望暴露的问题。

学生可在提问时选择可见性，也可在提问后更改（改为私密始终允许；改为公开需仍未被回答，或由教师操作）。

**权限矩阵：**

| 操作 | 学生（本人） | 学生（他人） | 教师 |
| --- | :---: | :---: | :---: |
| 提问 | ✓ | — | ✗ |
| 查看公开问题 | ✓ | ✓ | ✓ |
| 查看私密问题 | ✓（仅自己） | ✗ | ✓ |
| 回答问题 | ✗ | ✗ | ✓ |
| 修改可见性 | ✓ | — | ✓ |
| 删除问题 | ✓（未回答时） | — | ✓ |

---

## 枚举说明

**可见性（visibility）：**

| 值 | 说明 |
| --- | --- |
| public | 公开，课程内所有人可见 |
| private | 私密，仅提问者和教师可见 |

**问题状态（question_status）：**

| 值 | 说明 |
| --- | --- |
| unanswered | 待回答 |
| answered | 已回答 |

---

## 1. 学生提问

```http
POST /api/courses/{course_id}/questions
```

**权限：** `role = student`，且已加入该课程。

**请求体：**

```json
{
  "title": "进程的阻塞态和挂起态有什么区别？",
  "content": "课件上提到了挂起状态，但没有详细说明它和阻塞态的区别，希望老师解答。",
  "visibility": "public",
  "section_id": "section_001"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| title | string | 是 | 问题标题（最大 100 字） |
| content | string | 否 | 问题详细描述 |
| visibility | string | 是 | public 或 private |
| section_id | string | 否 | 关联小节，不填则为课程级提问 |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "question_001",
    "course_id": "course_001",
    "section_id": "section_001",
    "section_title": "第一章：进程管理",
    "title": "进程的阻塞态和挂起态有什么区别？",
    "content": "课件上提到了挂起状态，但没有详细说明它和阻塞态的区别，希望老师解答。",
    "visibility": "public",
    "status": "unanswered",
    "asked_by": {
      "id": "user_001",
      "name": "张三"
    },
    "created_at": "2026-06-04T10:00:00+08:00"
  },
  "message": "created"
}
```

---

## 2. 获取问题列表

```http
GET /api/courses/{course_id}/questions
```

**权限：**
- `student`：只能看到公开问题 + 自己的私密问题；
- `teacher`：可看到所有问题（包括所有私密问题）。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| section_id | string | 否 | 按关联小节筛选 |
| status | string | 否 | unanswered 或 answered |
| visibility | string | 否 | public 或 private（仅教师可用） |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001",
    "items": [
      {
        "id": "question_001",
        "section_id": "section_001",
        "section_title": "第一章：进程管理",
        "title": "进程的阻塞态和挂起态有什么区别？",
        "visibility": "public",
        "status": "answered",
        "asked_by": {
          "id": "user_001",
          "name": "张三"
        },
        "created_at": "2026-06-04T10:00:00+08:00",
        "answered_at": "2026-06-04T14:00:00+08:00"
      }
    ],
    "total": 1
  },
  "message": "ok"
}
```

> 对学生端返回的私密问题条目，`asked_by` 只会是自己，后端在查询时已过滤。

---

## 3. 获取问题详情

```http
GET /api/courses/{course_id}/questions/{question_id}
```

**权限：**
- 公开问题：课程内所有人可访问；
- 私密问题：仅提问者本人和教师可访问，其他学生访问返回 `403`。

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "question_001",
    "course_id": "course_001",
    "section_id": "section_001",
    "section_title": "第一章：进程管理",
    "title": "进程的阻塞态和挂起态有什么区别？",
    "content": "课件上提到了挂起状态，但没有详细说明它和阻塞态的区别，希望老师解答。",
    "visibility": "public",
    "status": "answered",
    "asked_by": {
      "id": "user_001",
      "name": "张三"
    },
    "answer": {
      "content": "阻塞态是进程主动等待某个事件（如 I/O 完成），仍驻留在内存中；挂起态是进程被调出到外存，不再占用内存资源，通常由系统主动执行以缓解内存压力。",
      "answered_by": {
        "id": "user_002",
        "name": "李老师"
      },
      "answered_at": "2026-06-04T14:00:00+08:00"
    },
    "created_at": "2026-06-04T10:00:00+08:00"
  },
  "message": "ok"
}
```

---

## 4. 教师回答问题

```http
POST /api/courses/{course_id}/questions/{question_id}/answer
```

**功能说明：** 教师对学生提问进行回答。每个问题只有一条官方回答，重复调用视为更新。

**权限：** `role = teacher`

**请求体：**

```json
{
  "content": "阻塞态是进程主动等待某个事件（如 I/O 完成），仍驻留在内存中；挂起态是进程被调出到外存，不再占用内存资源，通常由系统主动执行以缓解内存压力。"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| content | string | 是 | 回答内容 |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "question_id": "question_001",
    "answer": {
      "content": "阻塞态是进程主动等待某个事件（如 I/O 完成）...",
      "answered_by": {
        "id": "user_002",
        "name": "李老师"
      },
      "answered_at": "2026-06-04T14:00:00+08:00"
    }
  },
  "message": "answered"
}
```

---

## 5. 修改问题可见性

```http
PATCH /api/courses/{course_id}/questions/{question_id}
```

**功能说明：** 学生可将自己的问题改为私密；教师可修改任意问题的可见性。

**权限：** 提问者本人（仅可改为 private）或 `role = teacher`。

**请求体：**

```json
{
  "visibility": "private"
}
```

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "question_001",
    "visibility": "private"
  },
  "message": "updated"
}
```

---

## 6. 删除问题

```http
DELETE /api/courses/{course_id}/questions/{question_id}
```

**功能说明：** 提问者本人在问题未被回答时可删除；教师可删除任意问题。删除问题时，对应回答也一并删除。

**权限：** 提问者本人（未回答状态）或 `role = teacher`。

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "question_001"
  },
  "message": "deleted"
}
```
