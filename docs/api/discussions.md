# 讨论 API

> 基础路径：`/api/courses/{course_id}/discussions`
>
> 所有接口均需携带 JWT 令牌。

---

## 说明

讨论是教师在课程内发起的话题，师生均可参与回复，支持多级评论（帖子 → 回复）。教师发起讨论，学生和教师都可以回复，教师回复时身份标识会高亮显示。

**权限矩阵：**

| 操作 | 学生 | 教师 |
| --- | :---: | :---: |
| 创建讨论 | ✗ | ✓ |
| 查看讨论列表 / 详情 | ✓ | ✓ |
| 发表回复 | ✓ | ✓ |
| 删除自己的回复 | ✓ | ✓ |
| 删除任意回复 | ✗ | ✓ |
| 关闭 / 重开讨论 | ✗ | ✓ |
| 删除讨论 | ✗ | ✓ |

---

## 枚举说明

**讨论状态（discussion_status）：**

| 值 | 说明 |
| --- | --- |
| open | 进行中，学生可回复 |
| closed | 已关闭，仅可查看 |

---

## 1. 教师创建讨论

```http
POST /api/courses/{course_id}/discussions
```

**权限：** `role = teacher`

**请求体：**

```json
{
  "title": "关于进程调度算法，你觉得哪种最适合交互式系统？",
  "content": "本周课上介绍了 FCFS、SJF 和时间片轮转三种调度算法，请结合你的理解展开讨论。",
  "section_id": "section_001"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| title | string | 是 | 讨论标题 |
| content | string | 是 | 讨论正文，可提供背景或引导性问题 |
| section_id | string | 否 | 关联小节，不填则为课程级讨论 |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "discussion_001",
    "course_id": "course_001",
    "section_id": "section_001",
    "section_title": "第一章：进程管理",
    "title": "关于进程调度算法，你觉得哪种最适合交互式系统？",
    "content": "本周课上介绍了 FCFS、SJF 和时间片轮转三种调度算法，请结合你的理解展开讨论。",
    "status": "open",
    "reply_count": 0,
    "created_by": {
      "id": "user_002",
      "name": "李老师",
      "role": "teacher"
    },
    "created_at": "2026-06-04T10:00:00+08:00"
  },
  "message": "created"
}
```

---

## 2. 获取讨论列表

```http
GET /api/courses/{course_id}/discussions
```

**权限：** 已加入该课程的 `student` 或该课程的 `teacher`。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| section_id | string | 否 | 按关联小节筛选 |
| status | string | 否 | open 或 closed |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001",
    "items": [
      {
        "id": "discussion_001",
        "section_id": "section_001",
        "section_title": "第一章：进程管理",
        "title": "关于进程调度算法，你觉得哪种最适合交互式系统？",
        "status": "open",
        "reply_count": 12,
        "created_by": {
          "id": "user_002",
          "name": "李老师",
          "role": "teacher"
        },
        "last_reply_at": "2026-06-04T15:30:00+08:00",
        "created_at": "2026-06-04T10:00:00+08:00"
      }
    ],
    "total": 1
  },
  "message": "ok"
}
```

---

## 3. 获取讨论详情（含回复列表）

```http
GET /api/courses/{course_id}/discussions/{discussion_id}
```

**权限：** 已加入该课程的 `student` 或该课程的 `teacher`。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| page | integer | 否 | 回复页码，默认 1 |
| page_size | integer | 否 | 每页回复数，默认 20 |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "discussion_001",
    "course_id": "course_001",
    "section_id": "section_001",
    "section_title": "第一章：进程管理",
    "title": "关于进程调度算法，你觉得哪种最适合交互式系统？",
    "content": "本周课上介绍了 FCFS、SJF 和时间片轮转三种调度算法，请结合你的理解展开讨论。",
    "status": "open",
    "reply_count": 12,
    "created_by": {
      "id": "user_002",
      "name": "李老师",
      "role": "teacher"
    },
    "created_at": "2026-06-04T10:00:00+08:00",
    "replies": {
      "items": [
        {
          "id": "reply_001",
          "content": "我觉得时间片轮转最适合，因为它能保证所有进程都能被及时响应。",
          "author": {
            "id": "user_001",
            "name": "张三",
            "role": "student"
          },
          "is_teacher": false,
          "created_at": "2026-06-04T10:30:00+08:00"
        },
        {
          "id": "reply_002",
          "content": "补充一下：时间片的长短会直接影响响应时间和上下文切换开销，需要权衡。",
          "author": {
            "id": "user_002",
            "name": "李老师",
            "role": "teacher"
          },
          "is_teacher": true,
          "created_at": "2026-06-04T11:00:00+08:00"
        }
      ],
      "total": 12,
      "page": 1,
      "page_size": 20
    }
  },
  "message": "ok"
}
```

> `is_teacher` 为 `true` 时，前端应对该回复做教师身份高亮（如标注「教师」徽章）。

---

## 4. 发表回复

```http
POST /api/courses/{course_id}/discussions/{discussion_id}/replies
```

**权限：** 已加入该课程的 `student` 或该课程的 `teacher`；讨论状态须为 `open`。

**请求体：**

```json
{
  "content": "我认为时间片轮转更适合，因为它能保证交互式进程的响应时间上限。"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| content | string | 是 | 回复内容（最大 2000 字） |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "reply_003",
    "discussion_id": "discussion_001",
    "content": "我认为时间片轮转更适合，因为它能保证交互式进程的响应时间上限。",
    "author": {
      "id": "user_001",
      "name": "张三",
      "role": "student"
    },
    "is_teacher": false,
    "created_at": "2026-06-04T12:00:00+08:00"
  },
  "message": "replied"
}
```

---

## 5. 删除回复

```http
DELETE /api/courses/{course_id}/discussions/{discussion_id}/replies/{reply_id}
```

**权限：** 回复的作者可删除自己的回复；教师可删除该讨论下的任意回复。

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "reply_001"
  },
  "message": "deleted"
}
```

---

## 6. 关闭 / 重开讨论

```http
PATCH /api/courses/{course_id}/discussions/{discussion_id}
```

**权限：** `role = teacher`

**请求体：**

```json
{
  "status": "closed"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| status | string | 是 | open 或 closed |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "discussion_001",
    "status": "closed"
  },
  "message": "updated"
}
```

---

## 7. 删除讨论

```http
DELETE /api/courses/{course_id}/discussions/{discussion_id}
```

**功能说明：** 删除讨论时，该讨论下所有回复也将一并删除。

**权限：** `role = teacher`

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "discussion_001"
  },
  "message": "deleted"
}
```
