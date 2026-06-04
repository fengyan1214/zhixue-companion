# 智能问答 API

> 基础路径：`/api/student/courses/{course_id}/chat`
>
> 权限：`role = student`，且已加入该课程。
>
> 所有接口均需携带 JWT 令牌。

---

## RAG 说明

问答基于 **RAG（检索增强生成）** 实现，回答质量与课程内已上传的材料直接挂钩：

- **检索范围**：教师在课程小节中上传的课件/资料文件（PDF、TXT 等），由 C++ 文件处理服务在上传时完成文本提取和向量化索引；
- **检索时机**：学生每次提问时，后端先对问题做向量检索，找到最相关的文本片段，再将原始问题 + 检索片段一起传给 MiniMax 生成回答；
- **降级策略**：若课程内尚无索引材料，退化为通用知识问答，响应中 `rag_used` 字段为 `false`。

---

## 1. 发送问题

```http
POST /api/student/courses/{course_id}/chat
```

**功能说明：** 向 AI 学习伴侣发送一个学习问题，后端先从课程材料中检索相关片段（RAG），再调用 MiniMax 生成回答。

**请求体：**

```json
{
  "question": "请帮我解释一下进程和线程有什么区别？",
  "session_id": "session_001",
  "section_id": "section_001"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| question | string | 是 | 用户问题 |
| session_id | string | 否 | 会话 ID，不传则后端创建新会话 |
| section_id | string | 否 | 限定在指定小节的材料范围内检索，不传则检索整门课程 |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "session_id": "session_001",
    "answer": "进程是资源分配的基本单位，线程是 CPU 调度的基本单位...",
    "rag_used": true,
    "references": [
      {
        "section_id": "section_001",
        "section_title": "第一章：进程管理",
        "file_name": "section_001_slides.pdf",
        "excerpt": "进程（Process）是操作系统进行资源分配和调度的基本单位..."
      }
    ],
    "suggestions": [
      "可以结合进程地址空间理解二者区别",
      "建议复习线程共享资源与独立栈空间"
    ]
  },
  "message": "ok"
}
```

> `references` 为本次回答实际引用的课程材料片段，供学生追溯原文；`rag_used = false` 时 `references` 为空数组。

---

## 2. 获取会话历史

```http
GET /api/student/courses/{course_id}/chat/sessions/{session_id}/messages
```

**路径参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| course_id | string | 是 | 课程 ID |
| session_id | string | 是 | 会话 ID |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "session_id": "session_001",
    "course_id": "course_001",
    "messages": [
      {
        "id": "msg_001",
        "role": "user",
        "content": "什么是进程？",
        "created_at": "2026-06-04T20:00:00+08:00"
      },
      {
        "id": "msg_002",
        "role": "assistant",
        "content": "进程是程序的一次执行过程...",
        "rag_used": true,
        "references": [
          {
            "section_title": "第一章：进程管理",
            "file_name": "section_001_slides.pdf",
            "excerpt": "进程是操作系统进行资源分配的基本单位..."
          }
        ],
        "created_at": "2026-06-04T20:00:02+08:00"
      }
    ]
  },
  "message": "ok"
}
```

---

## 3. 获取会话列表

```http
GET /api/student/courses/{course_id}/chat/sessions
```

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| section_id | string | 否 | 按小节筛选 |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001",
    "items": [
      {
        "id": "session_001",
        "section_id": "section_001",
        "section_title": "第一章：进程管理",
        "last_question": "什么是进程？",
        "message_count": 4,
        "created_at": "2026-06-04T20:00:00+08:00",
        "updated_at": "2026-06-04T20:05:00+08:00"
      }
    ],
    "total": 1
  },
  "message": "ok"
}
```
