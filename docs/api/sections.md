# 课程小节 API

> 基础路径：`/api/teacher/courses/{course_id}/sections`、`/api/student/courses/{course_id}/sections`
>
> 所有接口均需携带 JWT 令牌。

---

## 说明

课程由若干**小节（Section）**组成，每个小节代表一次课或一个知识模块。小节下可挂载作业，学生完成各小节作业后积累分数。

---

## 1. 教师创建小节

```http
POST /api/teacher/courses/{course_id}/sections
```

**权限：** `role = teacher`，且是该课程的创建者。

**请求体：**

```json
{
  "title": "第一章：进程管理",
  "description": "介绍进程的概念、状态转换和调度算法。",
  "order": 1,
  "material_url": "/files/materials/section_001.pdf"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| title | string | 是 | 小节标题 |
| description | string | 否 | 小节说明 |
| order | integer | 否 | 排序序号，不传则追加到末尾 |
| material_url | string | 否 | 课件/资料文件 URL |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "section_001",
    "course_id": "course_001",
    "title": "第一章：进程管理",
    "description": "介绍进程的概念、状态转换和调度算法。",
    "order": 1,
    "material_url": "/files/materials/section_001.pdf",
    "assignment_count": 0,
    "created_at": "2026-06-04T10:00:00+08:00"
  },
  "message": "created"
}
```

---

## 2. 教师获取课程小节列表

```http
GET /api/teacher/courses/{course_id}/sections
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
        "id": "section_001",
        "title": "第一章：进程管理",
        "order": 1,
        "assignment_count": 2,
        "created_at": "2026-06-04T10:00:00+08:00"
      },
      {
        "id": "section_002",
        "title": "第二章：内存管理",
        "order": 2,
        "assignment_count": 1,
        "created_at": "2026-06-05T10:00:00+08:00"
      }
    ],
    "total": 2
  },
  "message": "ok"
}
```

---

## 3. 教师更新小节

```http
PATCH /api/teacher/courses/{course_id}/sections/{section_id}
```

**权限：** `role = teacher`

**请求体：**

```json
{
  "title": "第一章：进程管理（修订版）",
  "description": "新增了进程通信内容。",
  "order": 1
}
```

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "section_001",
    "title": "第一章：进程管理（修订版）",
    "updated_at": "2026-06-04T12:00:00+08:00"
  },
  "message": "updated"
}
```

---

## 4. 教师删除小节

```http
DELETE /api/teacher/courses/{course_id}/sections/{section_id}
```

**功能说明：** 删除小节时，该小节下所有作业也将一并删除（级联删除），请谨慎操作。

**权限：** `role = teacher`

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "section_001"
  },
  "message": "deleted"
}
```

---

## 5. 教师为小节发布作业

```http
POST /api/teacher/courses/{course_id}/sections/{section_id}/assignments
```

**功能说明：** 在指定小节下发布一份作业，作业与小节绑定，学生在课程作业列表中可看到所属小节。支持上传附件（题目 PDF 等）。

**权限：** `role = teacher`

**请求体（Content-Type: multipart/form-data）：**

```text
title=进程管理练习
description=完成关于进程状态转换的分析题，不少于 500 字。
reference_answer=参考答案...（可选）
rubric=满分 100 分，概念 40 分，分析 40 分，表达 20 分。（可选）
due_at=2026-06-15T23:59:00+08:00
full_score=100
attachment=<二进制文件内容，可选>
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| title | string | 是 | 作业标题 |
| description | string | 是 | 作业要求说明 |
| reference_answer | string | 否 | 参考答案 |
| rubric | string | 否 | 评分标准 |
| due_at | string | 是 | 截止时间（ISO 8601） |
| full_score | integer | 否 | 满分，默认 100 |
| attachment | file | 否 | 作业题目附件（PDF/TXT，最大 10 MB） |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "assignment_001",
    "course_id": "course_001",
    "section_id": "section_001",
    "section_title": "第一章：进程管理",
    "title": "进程管理练习",
    "description": "完成关于进程状态转换的分析题，不少于 500 字。",
    "due_at": "2026-06-15T23:59:00+08:00",
    "full_score": 100,
    "status": "open",
    "attachment_url": "/files/assignment_001_topic.pdf",
    "created_at": "2026-06-04T10:00:00+08:00"
  },
  "message": "published"
}
```

---

## 6. 学生获取课程小节列表

```http
GET /api/student/courses/{course_id}/sections
```

**功能说明：** 学生获取课程的所有小节，包含每节的作业数和个人完成情况。

**权限：** `role = student`，且已加入该课程。

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001",
    "items": [
      {
        "id": "section_001",
        "title": "第一章：进程管理",
        "description": "介绍进程的概念、状态转换和调度算法。",
        "order": 1,
        "material_url": "/files/materials/section_001.pdf",
        "assignment_count": 2,
        "submitted_count": 1,
        "section_score": 88
      },
      {
        "id": "section_002",
        "title": "第二章：内存管理",
        "order": 2,
        "material_url": null,
        "assignment_count": 1,
        "submitted_count": 0,
        "section_score": null
      }
    ],
    "total": 2
  },
  "message": "ok"
}
```

> `section_score` 为该小节所有已批改作业的平均分，未提交或未批改时为 `null`。

---

## 7. 学生获取小节详情

```http
GET /api/student/courses/{course_id}/sections/{section_id}
```

**权限：** `role = student`

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "section_001",
    "course_id": "course_001",
    "title": "第一章：进程管理",
    "description": "介绍进程的概念、状态转换和调度算法。",
    "order": 1,
    "material_url": "/files/materials/section_001.pdf",
    "assignments": [
      {
        "id": "assignment_001",
        "title": "进程管理练习",
        "due_at": "2026-06-15T23:59:00+08:00",
        "status": "open",
        "submitted": true,
        "score": 88
      }
    ]
  },
  "message": "ok"
}
```
