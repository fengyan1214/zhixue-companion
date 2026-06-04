# 课程管理 API

> 基础路径：`/api/courses`、`/api/teacher/courses`、`/api/student/courses`
>
> 所有接口均需携带 JWT 令牌。

---

## 枚举说明

**课程状态（course_status）：**

| 值 | 说明 |
| --- | --- |
| active | 进行中 |
| archived | 已归档（只读，不可再加入） |

---

## 1. 教师创建课程

```http
POST /api/teacher/courses
```

**功能说明：** 教师创建一门课程，系统自动生成唯一的 6 位课程码，学生凭课程码加入。

**权限：** `role = teacher`

**请求体：**

```json
{
  "name": "操作系统",
  "description": "本课程介绍操作系统的核心原理，包括进程管理、内存管理和文件系统。",
  "cover_image_url": "/files/covers/os.png",
  "semester": "2026春季"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| name | string | 是 | 课程名称 |
| description | string | 否 | 课程简介 |
| cover_image_url | string | 否 | 课程封面图 URL |
| semester | string | 否 | 学期标识，如 "2026春季" |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "course_001",
    "name": "操作系统",
    "description": "本课程介绍操作系统的核心原理...",
    "code": "OS8X2K",
    "semester": "2026春季",
    "status": "active",
    "teacher_id": "user_002",
    "teacher_name": "李老师",
    "student_count": 0,
    "created_at": "2026-06-04T10:00:00+08:00"
  },
  "message": "created"
}
```

> `code` 为系统自动生成的 6 位课程码（大写字母+数字），学生凭此码加入课程。

---

## 2. 教师获取自己的课程列表

```http
GET /api/teacher/courses
```

**权限：** `role = teacher`

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| status | string | 否 | active 或 archived |
| keyword | string | 否 | 按课程名称模糊搜索 |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "course_001",
        "name": "操作系统",
        "code": "OS8X2K",
        "semester": "2026春季",
        "status": "active",
        "student_count": 35,
        "section_count": 12,
        "created_at": "2026-06-04T10:00:00+08:00"
      }
    ],
    "total": 1
  },
  "message": "ok"
}
```

---

## 3. 教师获取课程详情

```http
GET /api/teacher/courses/{course_id}
```

**权限：** `role = teacher`，且必须是该课程的创建教师。

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "course_001",
    "name": "操作系统",
    "description": "本课程介绍操作系统的核心原理...",
    "code": "OS8X2K",
    "semester": "2026春季",
    "status": "active",
    "teacher_id": "user_002",
    "teacher_name": "李老师",
    "student_count": 35,
    "section_count": 12,
    "created_at": "2026-06-04T10:00:00+08:00",
    "updated_at": "2026-06-04T10:00:00+08:00"
  },
  "message": "ok"
}
```

---

## 4. 教师更新课程信息

```http
PATCH /api/teacher/courses/{course_id}
```

**权限：** `role = teacher`

**请求体：**

```json
{
  "name": "操作系统（2026版）",
  "description": "更新后的课程简介",
  "semester": "2026秋季"
}
```

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "course_001",
    "name": "操作系统（2026版）",
    "updated_at": "2026-06-04T12:00:00+08:00"
  },
  "message": "updated"
}
```

---

## 5. 归档课程

```http
POST /api/teacher/courses/{course_id}/archive
```

**功能说明：** 将课程标记为已归档，归档后学生不能再加入，但已加入学生仍可查看历史内容。

**权限：** `role = teacher`

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "course_001",
    "status": "archived"
  },
  "message": "archived"
}
```

---

## 6. 重新生成课程码

```http
POST /api/teacher/courses/{course_id}/regenerate-code
```

**功能说明：** 当课程码泄露时，教师可重新生成新的课程码，旧码立即失效。

**权限：** `role = teacher`

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "course_001",
    "code": "KR7PQ1"
  },
  "message": "code regenerated"
}
```

---

## 7. 教师获取课程学生列表

```http
GET /api/teacher/courses/{course_id}/students
```

**权限：** `role = teacher`

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001",
    "items": [
      {
        "id": "user_001",
        "username": "20240101",
        "name": "张三",
        "class_name": "计算机 2401 班",
        "joined_at": "2026-06-04T10:30:00+08:00",
        "total_score": 87.5
      }
    ],
    "total": 35
  },
  "message": "ok"
}
```

---

## 8. 教师按学号添加学生

```http
POST /api/teacher/courses/{course_id}/students
```

**功能说明：** 教师主动将学生添加到课程中，无需学生自行输入课程码。支持单个或批量添加，按学号（`username`）查找学生账号。

**权限：** `role = teacher`

**请求体：**

```json
{
  "usernames": ["20240101", "20240102", "20240103"]
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| usernames | array | 是 | 学号列表，至少 1 个，最多 100 个 |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001",
    "added": [
      { "username": "20240101", "name": "张三", "student_id": "user_001" },
      { "username": "20240102", "name": "李四", "student_id": "user_002" }
    ],
    "failed": [
      { "username": "20240103", "reason": "用户不存在" },
      { "username": "20240104", "reason": "已在课程中" }
    ]
  },
  "message": "ok"
}
```

> `added` 为成功添加的学生，`failed` 为未能添加的条目及原因，两者均可能同时存在（部分成功）。

---

## 9. 教师移除学生

```http
DELETE /api/teacher/courses/{course_id}/students/{student_id}
```

**功能说明：** 将指定学生从课程中移除。

**权限：** `role = teacher`

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001",
    "student_id": "user_001"
  },
  "message": "removed"
}
```

---

## 10. 学生通过课程码加入课程

```http
POST /api/student/courses/join
```

**功能说明：** 学生输入课程码加入对应课程。每门课程每个学生只能加入一次。

**权限：** `role = student`

**请求体：**

```json
{
  "code": "OS8X2K"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| code | string | 是 | 课程码，6 位大写字母+数字 |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001",
    "course_name": "操作系统",
    "teacher_name": "李老师",
    "semester": "2026春季",
    "joined_at": "2026-06-04T10:30:00+08:00"
  },
  "message": "joined"
}
```

**错误示例（课程码不存在）：**

```json
{
  "success": false,
  "error": {
    "code": "COURSE_NOT_FOUND",
    "message": "课程码无效或课程不存在"
  }
}
```

**错误示例（已加入）：**

```json
{
  "success": false,
  "error": {
    "code": "ALREADY_JOINED",
    "message": "你已加入该课程"
  }
}
```

---

## 11. 学生获取已加入的课程列表

```http
GET /api/student/courses
```

**权限：** `role = student`

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| status | string | 否 | active 或 archived |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "course_001",
        "name": "操作系统",
        "teacher_name": "李老师",
        "semester": "2026春季",
        "status": "active",
        "section_count": 12,
        "completed_sections": 5,
        "total_score": 87.5,
        "joined_at": "2026-06-04T10:30:00+08:00"
      }
    ],
    "total": 3
  },
  "message": "ok"
}
```

---

## 12. 学生获取课程详情

```http
GET /api/student/courses/{course_id}
```

**权限：** `role = student`，且必须已加入该课程。

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "course_001",
    "name": "操作系统",
    "description": "本课程介绍操作系统的核心原理...",
    "teacher_name": "李老师",
    "semester": "2026春季",
    "status": "active",
    "section_count": 12,
    "completed_sections": 5,
    "total_score": 87.5,
    "joined_at": "2026-06-04T10:30:00+08:00"
  },
  "message": "ok"
}
```

---

## 13. 学生退出课程

```http
POST /api/student/courses/{course_id}/quit
```

**功能说明：** 学生主动退出课程，退出后将无法查看课程内容。

**权限：** `role = student`

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001"
  },
  "message": "quit"
}
```
