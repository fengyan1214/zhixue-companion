# 知识点总结 API

> 基础路径：`/api/student/courses/{course_id}/summaries`
>
> 权限：`role = student`，且已加入该课程。
>
> 所有接口均需携带 JWT 令牌。

---

## RAG 说明

知识点总结支持两种模式：

- **自由输入模式**：学生手动提供 `source_text`，后端直接基于该文本调用 MiniMax 生成总结；
- **课程材料模式**：学生不提供 `source_text`，指定 `section_id`，后端从该小节的已索引课程材料（教师上传的课件/资料文件）中检索相关内容，以此为基础生成总结（RAG）。

响应中 `rag_used` 字段标识当次总结是否基于课程材料检索生成。

---

## 1. 创建知识点总结

```http
POST /api/student/courses/{course_id}/summaries
```

**请求体（自由输入模式）：**

```json
{
  "title": "进程管理自学笔记总结",
  "source_text": "进程是程序的一次执行过程，包含程序段、数据段和进程控制块...",
  "summary_type": "structured"
}
```

**请求体（课程材料模式，不传 source_text）：**

```json
{
  "title": "第一章：进程管理 课件总结",
  "section_id": "section_001",
  "summary_type": "review"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| title | string | 是 | 总结标题 |
| section_id | string | 否 | 关联小节 ID；不传 `source_text` 时必填，用于从课程材料中检索内容 |
| source_text | string | 否 | 待总结的原文；与 `section_id` 二选一，同时传入时优先使用 `source_text` |
| summary_type | string | 否 | structured（结构化，默认）、brief（简要摘要）、review（复习提纲） |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "summary_001",
    "course_id": "course_001",
    "section_id": "section_001",
    "section_title": "第一章：进程管理",
    "title": "第一章：进程管理 课件总结",
    "rag_used": true,
    "references": [
      {
        "file_name": "section_001_slides.pdf",
        "excerpt": "进程是操作系统进行资源分配和调度的基本单位..."
      }
    ],
    "summary": {
      "overview": "本章主要介绍进程的定义、状态转换和调度机制。",
      "key_points": [
        "进程是资源分配的基本单位",
        "进程状态包括就绪、运行和阻塞",
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
    "created_at": "2026-06-04T20:00:00+08:00"
  },
  "message": "created"
}
```

---

## 2. 获取总结列表

```http
GET /api/student/courses/{course_id}/summaries
```

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| section_id | string | 否 | 按小节 ID 筛选 |
| keyword | string | 否 | 按标题或内容关键词搜索 |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001",
    "items": [
      {
        "id": "summary_001",
        "section_id": "section_001",
        "section_title": "第一章：进程管理",
        "title": "第一章：进程管理 课件总结",
        "rag_used": true,
        "created_at": "2026-06-04T20:00:00+08:00"
      }
    ],
    "total": 1
  },
  "message": "ok"
}
```

---

## 3. 获取总结详情

```http
GET /api/student/courses/{course_id}/summaries/{summary_id}
```

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "summary_001",
    "course_id": "course_001",
    "section_id": "section_001",
    "section_title": "第一章：进程管理",
    "title": "第一章：进程管理 课件总结",
    "rag_used": true,
    "references": [
      {
        "file_name": "section_001_slides.pdf",
        "excerpt": "进程是操作系统进行资源分配和调度的基本单位..."
      }
    ],
    "summary": {
      "overview": "本章主要介绍进程的定义、状态转换和调度机制。",
      "key_points": ["进程是资源分配的基本单位"],
      "difficult_points": ["进程与线程的区别"],
      "review_tips": ["结合状态转换图记忆进程生命周期"]
    },
    "created_at": "2026-06-04T20:00:00+08:00"
  },
  "message": "ok"
}
```

---

## 4. 删除总结

```http
DELETE /api/student/courses/{course_id}/summaries/{summary_id}
```

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "summary_001"
  },
  "message": "deleted"
}
```
