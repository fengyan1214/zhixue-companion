# 智学伴侣 API 文档

## 1. API 概述

本文档描述智学伴侣后端 API 设计。后端使用 Python FastAPI 实现，前端 React 通过 HTTP JSON 接口访问后端服务，后端再根据业务需要访问数据库、MiniMax 大模型 API 和 C++ 文件处理服务。

基础路径：

```text
/api
```

默认响应格式：

```json
{
  "success": true,
  "data": {},
  "message": "ok"
}
```

默认错误响应格式：

```json
{
  "success": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "请求参数不合法"
  }
}
```

## 2. 通用约定

### 2.1 HTTP 状态码

| 状态码 | 说明 |
| --- | --- |
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未登录或 Token 无效 |
| 403 | 无权限（角色不匹配） |
| 404 | 资源不存在 |
| 422 | 参数校验失败 |
| 500 | 服务内部错误 |
| 502 | 大模型服务调用失败 |

### 2.2 时间格式

所有时间字段统一使用 ISO 8601 格式。

```text
2026-06-01T20:00:00+08:00
```

### 2.3 认证方式

除注册和登录接口外，所有接口均需在请求头中携带 JWT 令牌：

```text
Authorization: Bearer <token>
```

### 2.4 角色枚举

```text
student   // 学生
teacher   // 教师
```

### 2.5 作业状态枚举

```text
open      // 进行中（学生可提交）
closed    // 已关闭（截止或教师手动关闭）
```

### 2.6 提交状态枚举

```text
submitted  // 已提交
```

## 3. 认证 API

### 3.1 学生注册

接口：

```http
POST /api/auth/register/student
```

功能说明：

学生注册账号，填写学号、姓名、班级和密码。

请求体：

```json
{
  "username": "20240101",
  "name": "张三",
  "class_name": "计算机 2401 班",
  "password": "your_password"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 学号，登录时使用 |
| name | string | 是 | 真实姓名 |
| class_name | string | 是 | 班级名称 |
| password | string | 是 | 登录密码（长度 6-32 位） |

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "user_001",
    "username": "20240101",
    "name": "张三",
    "role": "student"
  },
  "message": "registered"
}
```

### 3.2 教师注册

接口：

```http
POST /api/auth/register/teacher
```

功能说明：

教师注册账号，填写工号、姓名、所教课程和密码。

请求体：

```json
{
  "username": "T20240001",
  "name": "李老师",
  "courses": ["高等数学", "线性代数"],
  "password": "your_password"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 工号，登录时使用 |
| name | string | 是 | 真实姓名 |
| courses | array | 是 | 所教课程列表 |
| password | string | 是 | 登录密码（长度 6-32 位） |

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "user_002",
    "username": "T20240001",
    "name": "李老师",
    "role": "teacher"
  },
  "message": "registered"
}
```

### 3.3 登录

接口：

```http
POST /api/auth/login
```

功能说明：

学生和教师统一登录入口，输入用户名和密码，返回 JWT 令牌和用户角色。

请求体：

```json
{
  "username": "20240101",
  "password": "your_password"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 学号或工号 |
| password | string | 是 | 登录密码 |

响应示例：

```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400,
    "user": {
      "id": "user_001",
      "username": "20240101",
      "name": "张三",
      "role": "student"
    }
  },
  "message": "ok"
}
```

### 3.4 获取当前用户信息

接口：

```http
GET /api/auth/me
```

功能说明：

返回当前已登录用户的基本信息。需携带 JWT 令牌。

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "user_001",
    "username": "20240101",
    "name": "张三",
    "role": "student",
    "extra": {
      "class_name": "计算机 2401 班"
    }
  },
  "message": "ok"
}
```

## 4. 智能问答 API

> 权限：学生端（role = student）

### 4.1 发送问题

接口：

```http
POST /api/chat
```

功能说明：

向 AI 学习伴侣发送一个学习问题，由后端调用 MiniMax 生成回答。

请求体：

```json
{
  "question": "请帮我解释一下操作系统中的进程和线程有什么区别？",
  "course": "操作系统",
  "session_id": "session_001"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| question | string | 是 | 用户问题 |
| course | string | 否 | 课程名称或知识领域 |
| session_id | string | 否 | 会话 ID，不传则后端创建新会话 |

响应示例：

```json
{
  "success": true,
  "data": {
    "session_id": "session_001",
    "answer": "进程是资源分配的基本单位，线程是 CPU 调度的基本单位...",
    "suggestions": [
      "可以结合进程地址空间理解二者区别",
      "建议复习线程共享资源与独立栈空间"
    ]
  },
  "message": "ok"
}
```

### 4.2 获取会话历史

接口：

```http
GET /api/chat/sessions/{session_id}/messages
```

功能说明：

获取指定会话的历史消息。

路径参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| session_id | string | 是 | 会话 ID |

响应示例：

```json
{
  "success": true,
  "data": {
    "session_id": "session_001",
    "messages": [
      {
        "id": "msg_001",
        "role": "user",
        "content": "什么是进程？",
        "created_at": "2026-06-01T20:00:00+08:00"
      },
      {
        "id": "msg_002",
        "role": "assistant",
        "content": "进程是程序的一次执行过程...",
        "created_at": "2026-06-01T20:00:02+08:00"
      }
    ]
  },
  "message": "ok"
}
```

## 5. 学生端作业 API

> 权限：学生端（role = student）

### 5.1 获取作业列表

接口：

```http
GET /api/student/assignments
```

功能说明：

获取教师发布的作业列表，可按课程和状态筛选。

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| course | string | 否 | 按课程筛选 |
| status | string | 否 | open 或 closed |

请求示例：

```http
GET /api/student/assignments?status=open
```

响应示例：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "assignment_001",
        "title": "操作系统进程管理作业",
        "course": "操作系统",
        "due_at": "2026-06-10T23:59:00+08:00",
        "status": "open",
        "submitted": false
      }
    ],
    "total": 1
  },
  "message": "ok"
}
```

> `submitted` 表示当前登录学生是否已提交该作业。

### 5.2 获取作业详情

接口：

```http
GET /api/student/assignments/{assignment_id}
```

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "assignment_001",
    "title": "操作系统进程管理作业",
    "course": "操作系统",
    "description": "请结合课堂内容，分析进程与线程的区别及调度机制，不少于 800 字。",
    "due_at": "2026-06-10T23:59:00+08:00",
    "status": "open",
    "attachment_url": "/files/assignment_001_topic.pdf",
    "submitted": false
  },
  "message": "ok"
}
```

### 5.3 提交作业

接口：

```http
POST /api/student/assignments/{assignment_id}/submit
```

功能说明：

学生提交作业内容，支持纯文本提交或文件上传（二选一）。文件提交时由 C++ 文件处理服务提取文本。

请求体（文本提交，Content-Type: application/json）：

```json
{
  "content": "进程是程序执行的实体，包含程序计数器、寄存器和变量等资源...",
  "submit_type": "text"
}
```

请求体（文件提交，Content-Type: multipart/form-data）：

```text
submit_type=file
file=<二进制文件内容，支持 PDF、TXT、DOC，最大 10 MB>
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| submit_type | string | 是 | text（文本） 或 file（文件） |
| content | string | text 时必填 | 作业正文 |
| file | file | file 时必填 | 作业文件 |

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "submission_001",
    "assignment_id": "assignment_001",
    "student_id": "user_001",
    "submit_type": "file",
    "submitted_at": "2026-06-08T14:30:00+08:00",
    "status": "submitted"
  },
  "message": "submitted"
}
```

### 5.4 查看本人提交详情

接口：

```http
GET /api/student/assignments/{assignment_id}/my-submission
```

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "submission_001",
    "assignment_id": "assignment_001",
    "submit_type": "file",
    "file_url": "/files/submission_001.pdf",
    "submitted_at": "2026-06-08T14:30:00+08:00",
    "status": "submitted"
  },
  "message": "ok"
}
```

## 6. 知识点总结 API

> 权限：学生端（role = student）

### 6.1 创建知识点总结

接口：

```http
POST /api/summaries
```

功能说明：

提交笔记、课堂内容或知识主题，由后端调用 MiniMax 生成结构化总结。

请求体：

```json
{
  "title": "操作系统进程管理",
  "course": "操作系统",
  "source_text": "进程是程序的一次执行过程，包含程序段、数据段和进程控制块...",
  "summary_type": "structured"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| title | string | 是 | 总结标题 |
| course | string | 否 | 所属课程 |
| source_text | string | 是 | 待总结内容 |
| summary_type | string | 否 | structured、brief、review |

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "summary_001",
    "title": "操作系统进程管理",
    "course": "操作系统",
    "summary": {
      "overview": "本部分主要介绍进程的定义、状态转换和调度机制。",
      "key_points": [
        "进程是资源分配的基本单位",
        "进程状态通常包括就绪、运行和阻塞",
        "调度算法影响系统响应时间和吞吐量"
      ],
      "difficult_points": [
        "进程与线程的区别",
        "阻塞和就绪状态的转换条件"
      ],
      "review_tips": [
        "结合状态转换图记忆进程生命周期",
        "对比 FCFS、SJF、时间片轮转等调度算法"
      ]
    },
    "created_at": "2026-06-01T20:00:00+08:00"
  },
  "message": "created"
}
```

### 6.2 获取总结列表

接口：

```http
GET /api/summaries
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| course | string | 否 | 按课程筛选 |
| keyword | string | 否 | 按标题或内容关键词搜索 |

响应示例：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "summary_001",
        "title": "操作系统进程管理",
        "course": "操作系统",
        "created_at": "2026-06-01T20:00:00+08:00"
      }
    ],
    "total": 1
  },
  "message": "ok"
}
```

### 6.3 获取总结详情

接口：

```http
GET /api/summaries/{summary_id}
```

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "summary_001",
    "title": "操作系统进程管理",
    "course": "操作系统",
    "source_text": "进程是程序的一次执行过程...",
    "summary": {
      "overview": "本部分主要介绍进程的定义、状态转换和调度机制。",
      "key_points": ["进程是资源分配的基本单位"],
      "difficult_points": ["进程与线程的区别"],
      "review_tips": ["结合状态转换图记忆进程生命周期"]
    },
    "created_at": "2026-06-01T20:00:00+08:00"
  },
  "message": "ok"
}
```

### 6.4 删除总结

接口：

```http
DELETE /api/summaries/{summary_id}
```

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "summary_001"
  },
  "message": "deleted"
}
```

## 7. 学生端个性化学习计划 API

> 权限：学生端（role = student）

### 7.1 生成个性化学习计划

接口：

```http
POST /api/student/learning-plans
```

功能说明：

根据学生成绩、作业完成情况、薄弱知识点和学习目标，调用 MiniMax 生成定制化学习计划。

请求体：

```json
{
  "course": "高等数学",
  "goal": "两周内提升导数应用题正确率",
  "grade_records": [
    {
      "exam_name": "期中考试",
      "score": 72,
      "full_score": 100
    }
  ],
  "homework_records": [
    {
      "title": "第 3 章导数作业",
      "score": 68,
      "full_score": 100,
      "weak_points": ["复合函数求导", "极值应用题"]
    }
  ],
  "available_time_per_day": 60
}
```

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "plan_001",
    "course": "高等数学",
    "analysis": {
      "current_level": "基础概念掌握一般，应用题偏弱",
      "weak_points": ["复合函数求导", "极值应用题"],
      "priority": "先补齐求导规则，再训练应用题建模"
    },
    "plan": [
      {
        "day": 1,
        "task": "复习复合函数求导规则并完成 10 道基础题",
        "duration_minutes": 60
      },
      {
        "day": 2,
        "task": "整理极值应用题常见模型并完成 5 道例题",
        "duration_minutes": 60
      }
    ],
    "created_at": "2026-06-01T20:00:00+08:00"
  },
  "message": "created"
}
```

### 7.2 获取学习计划列表

接口：

```http
GET /api/student/learning-plans
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| course | string | 否 | 课程名称 |
| status | string | 否 | active、completed 或 archived |

响应示例：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "plan_001",
        "course": "高等数学",
        "status": "active",
        "created_at": "2026-06-01T20:00:00+08:00"
      }
    ],
    "total": 1
  },
  "message": "ok"
}
```

## 8. 教师端作业管理 API

> 权限：教师端（role = teacher）

### 8.1 发布作业

接口：

```http
POST /api/teacher/assignments
```

功能说明：

教师发布一份作业，填写标题、课程、要求、参考答案、评分标准和截止时间。可上传作业附件（题目 PDF 等），由 C++ 文件处理服务自动解析。

请求体（Content-Type: multipart/form-data）：

```text
title=操作系统进程管理作业
course=操作系统
description=请结合课堂内容，分析进程与线程的区别及调度机制，不少于 800 字。
reference_answer=参考答案内容...（可选）
rubric=满分 100 分，概念解释 30 分，过程分析 40 分，结论 30 分。（可选）
due_at=2026-06-10T23:59:00+08:00
attachment=<二进制文件内容，可选，支持 PDF、TXT，最大 10 MB>
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| title | string | 是 | 作业标题 |
| course | string | 是 | 所属课程 |
| description | string | 是 | 作业要求说明 |
| reference_answer | string | 否 | 参考答案 |
| rubric | string | 否 | 评分标准 |
| due_at | string | 是 | 截止时间（ISO 8601） |
| attachment | file | 否 | 作业题目附件 |

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "assignment_001",
    "title": "操作系统进程管理作业",
    "course": "操作系统",
    "description": "请结合课堂内容，分析进程与线程的区别及调度机制，不少于 800 字。",
    "due_at": "2026-06-10T23:59:00+08:00",
    "status": "open",
    "attachment_url": "/files/assignment_001_topic.pdf",
    "created_at": "2026-06-01T20:00:00+08:00"
  },
  "message": "published"
}
```

### 8.2 获取已发布作业列表

接口：

```http
GET /api/teacher/assignments
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| course | string | 否 | 按课程筛选 |
| status | string | 否 | open 或 closed |

响应示例：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "assignment_001",
        "title": "操作系统进程管理作业",
        "course": "操作系统",
        "due_at": "2026-06-10T23:59:00+08:00",
        "status": "open",
        "submission_count": 25,
        "total_students": 40
      }
    ],
    "total": 1
  },
  "message": "ok"
}
```

### 8.3 获取作业详情

接口：

```http
GET /api/teacher/assignments/{assignment_id}
```

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "assignment_001",
    "title": "操作系统进程管理作业",
    "course": "操作系统",
    "description": "请结合课堂内容，分析进程与线程的区别及调度机制，不少于 800 字。",
    "reference_answer": "参考答案内容...",
    "rubric": "满分 100 分，概念解释 30 分，过程分析 40 分，结论 30 分。",
    "due_at": "2026-06-10T23:59:00+08:00",
    "status": "open",
    "attachment_url": "/files/assignment_001_topic.pdf",
    "submission_count": 25,
    "created_at": "2026-06-01T20:00:00+08:00",
    "updated_at": "2026-06-01T20:00:00+08:00"
  },
  "message": "ok"
}
```

### 8.4 更新作业

接口：

```http
PATCH /api/teacher/assignments/{assignment_id}
```

请求体：

```json
{
  "description": "请结合课堂内容，分析进程与线程的区别及调度机制，不少于 1000 字。",
  "due_at": "2026-06-12T23:59:00+08:00"
}
```

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "assignment_001",
    "description": "请结合课堂内容，分析进程与线程的区别及调度机制，不少于 1000 字。",
    "due_at": "2026-06-12T23:59:00+08:00",
    "updated_at": "2026-06-02T10:00:00+08:00"
  },
  "message": "updated"
}
```

### 8.5 关闭作业

接口：

```http
POST /api/teacher/assignments/{assignment_id}/close
```

响应示例：

```json
{
  "success": true,
  "data": {
    "id": "assignment_001",
    "status": "closed"
  },
  "message": "closed"
}
```

### 8.6 获取作业提交列表

接口：

```http
GET /api/teacher/assignments/{assignment_id}/submissions
```

功能说明：

获取指定作业的所有学生提交记录。

响应示例：

```json
{
  "success": true,
  "data": {
    "assignment_id": "assignment_001",
    "items": [
      {
        "id": "submission_001",
        "student_id": "user_001",
        "student_name": "张三",
        "submit_type": "file",
        "submitted_at": "2026-06-08T14:30:00+08:00",
        "status": "submitted"
      }
    ],
    "total": 25
  },
  "message": "ok"
}
```

## 9. 教师端 AI 批改 API

> 权限：教师端（role = teacher）

### 9.1 AI 批改作业

接口：

```http
POST /api/teacher/assignments/{assignment_id}/grade
```

功能说明：

教师指定提交 ID 列表，系统调用 MiniMax 对学生提交进行 AI 批改，生成分数、评语、扣分点和修改建议。若学生以文件提交，系统使用 C++ 服务预先提取的文本参与批改。

请求体：

```json
{
  "submission_ids": ["submission_001", "submission_002"],
  "need_teacher_confirm": true
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| submission_ids | array | 是 | 待批改的提交 ID 列表 |
| need_teacher_confirm | boolean | 否 | 是否需要教师二次确认（默认 true） |

响应示例：

```json
{
  "success": true,
  "data": {
    "assignment_id": "assignment_001",
    "results": [
      {
        "submission_id": "submission_001",
        "student_id": "user_001",
        "student_name": "张三",
        "ai_score": 86,
        "comments": "整体思路正确，但关键概念解释不够完整。",
        "deductions": [
          {
            "point": "进程状态转换条件说明不完整",
            "minus": 6
          }
        ],
        "suggestions": ["补充阻塞态与就绪态的转换条件", "增加调度算法对比"],
        "confirmed": false
      }
    ]
  },
  "message": "graded"
}
```

### 9.2 教师确认或调整批改结果

接口：

```http
PATCH /api/teacher/submissions/{submission_id}/grade
```

功能说明：

教师对 AI 批改结果进行确认或手动调整最终分数。

请求体：

```json
{
  "final_score": 88,
  "confirmed": true,
  "teacher_comment": "补充了一些关键点，酌情加分。"
}
```

响应示例：

```json
{
  "success": true,
  "data": {
    "submission_id": "submission_001",
    "final_score": 88,
    "confirmed": true
  },
  "message": "updated"
}
```

### 9.3 获取批改报告

接口：

```http
GET /api/teacher/assignments/{assignment_id}/grading-report
```

响应示例：

```json
{
  "success": true,
  "data": {
    "assignment_id": "assignment_001",
    "average_score": 82.5,
    "graded_count": 25,
    "common_mistakes": ["概念解释不完整", "缺少案例分析"],
    "weak_points": ["进程状态转换", "线程共享资源"],
    "teaching_suggestions": ["建议下一节课用流程图讲解状态转换", "安排一次概念对比小测"]
  },
  "message": "ok"
}
```

## 10. 教师端 AI 查重与作业比对 API（合并）

> 权限：教师端（role = teacher）

### 10.1 触发查重与比对分析

接口：

```http
POST /api/teacher/assignments/{assignment_id}/analyze
```

功能说明：

对指定作业的一批提交同时执行查重和多维度比对。系统先调用 C++ 文件处理服务对提交文本进行预处理和指纹提取，再调用 MiniMax 进行语义相似度分析和比对，最终输出统一的分析报告。

请求体：

```json
{
  "submission_ids": ["submission_001", "submission_002", "submission_003"],
  "similarity_threshold": 0.8,
  "compare_dimensions": ["structure", "concept", "expression", "conclusion"]
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| submission_ids | array | 是 | 参与分析的提交 ID 列表 |
| similarity_threshold | number | 否 | 相似度告警阈值，默认 0.8（0.0~1.0） |
| compare_dimensions | array | 否 | 比对维度，默认全部（结构、概念、表达、结论） |

响应示例：

```json
{
  "success": true,
  "data": {
    "report_id": "report_001",
    "assignment_id": "assignment_001",
    "suspicious_pairs": [
      {
        "submission_a": "submission_001",
        "student_a": "张三",
        "submission_b": "submission_002",
        "student_b": "李四",
        "similarity": 0.87,
        "risk_level": "high",
        "similar_segments": [
          "对进程定义的表述高度一致",
          "结论段落结构相同"
        ],
        "ai_reason": "两份作业在观点顺序、关键句表达和例子选择上高度相似，存在参考同一来源的可能。"
      }
    ],
    "comparison_details": [
      {
        "submission_id": "submission_001",
        "student_name": "张三",
        "strengths": ["对线程区别解释较完整", "结合了具体场景举例"],
        "weaknesses": ["缺少调度算法对比"],
        "dimension_scores": {
          "structure": "完整",
          "concept": "准确",
          "expression": "流畅",
          "conclusion": "一般"
        }
      }
    ],
    "common_issues": ["都没有结合具体场景举例"],
    "teaching_suggestions": ["课堂上补充进程状态转换案例", "强调概念解释和例子结合"],
    "created_at": "2026-06-09T10:00:00+08:00"
  },
  "message": "analyzed"
}
```

### 10.2 获取分析报告

接口：

```http
GET /api/teacher/assignments/{assignment_id}/analyze-report
```

功能说明：

获取指定作业最近一次查重与比对分析的报告。

响应示例：

```json
{
  "success": true,
  "data": {
    "report_id": "report_001",
    "assignment_id": "assignment_001",
    "suspicious_pairs": [...],
    "comparison_details": [...],
    "common_issues": ["都没有结合具体场景举例"],
    "created_at": "2026-06-09T10:00:00+08:00"
  },
  "message": "ok"
}
```

## 11. 健康检查 API

接口：

```http
GET /api/health
```

功能说明：

用于检查后端服务是否正常运行。

响应示例：

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "service": "zhixue-companion-api"
  },
  "message": "ok"
}
```

## 12. 后端路由规划

| 模块 | 路由前缀 | 文件建议 |
| --- | --- | --- |
| 健康检查 | /api/health | app/main.py |
| 认证（注册 / 登录） | /api/auth | app/api/routes_auth.py |
| 智能问答 | /api/chat | app/api/routes_chat.py |
| 学生端作业管理 | /api/student/assignments | app/api/routes_student_assignments.py |
| 知识总结 | /api/summaries | app/api/routes_summary.py |
| 学生端个性化学习计划 | /api/student/learning-plans | app/api/routes_learning_plans.py |
| 教师端作业管理与发布 | /api/teacher/assignments | app/api/routes_teacher_assignments.py |
| 教师端 AI 批改 | /api/teacher/assignments/{id}/grade | （同上文件） |
| 教师端查重与比对 | /api/teacher/assignments/{id}/analyze | （同上文件） |

## 13. 前端接口封装建议

前端建议将 API 调用集中放在 `src/api` 目录中，并统一在请求拦截器中注入 JWT 令牌。

```ts
// src/api/client.ts
import axios from 'axios';

const client = axios.create({ baseURL: '/api' });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default client;
```

```ts
// src/api/auth.ts
export async function loginUser(username: string, password: string) {
  const res = await client.post('/auth/login', { username, password });
  return res.data;
}

export async function registerStudent(payload: {
  username: string;
  name: string;
  class_name: string;
  password: string;
}) {
  const res = await client.post('/auth/register/student', payload);
  return res.data;
}
```

```ts
// src/api/studentAssignments.ts
export async function getAssignments(params?: { course?: string; status?: string }) {
  const res = await client.get('/student/assignments', { params });
  return res.data;
}

export async function submitAssignment(assignmentId: string, payload: FormData | { content: string; submit_type: 'text' }) {
  const res = await client.post(`/student/assignments/${assignmentId}/submit`, payload);
  return res.data;
}
```

```ts
// src/api/teacherAssignments.ts
export async function publishAssignment(formData: FormData) {
  const res = await client.post('/teacher/assignments', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function analyzeAssignment(assignmentId: string, payload: {
  submission_ids: string[];
  similarity_threshold?: number;
  compare_dimensions?: string[];
}) {
  const res = await client.post(`/teacher/assignments/${assignmentId}/analyze`, payload);
  return res.data;
}
```
