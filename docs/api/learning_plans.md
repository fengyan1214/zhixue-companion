# 个性化学习计划 API

> 基础路径：`/api/student/courses/{course_id}/learning-plans`
>
> 权限：`role = student`，且已加入该课程。
>
> 所有接口均需携带 JWT 令牌。

---

## 数据信号说明

学习计划生成时，后端会**自动采集**该学生在本课程内的所有可用数据，无需前端传入。数据信号包括以下几类：

| 信号类型 | 采集内容 | 用途 |
| --- | --- | --- |
| 成绩数据 | 各作业得分、薄弱知识点 | 定位掌握程度薄弱环节 |
| 个人信息 | `interests`（兴趣）、`career_direction`（岗位方向） | 调整计划侧重和举例方向 |
| AI 问答记录 | 提问频率高的知识点、会话中暴露的困惑点 | 识别反复疑惑的概念 |
| 知识点总结记录 | 已生成总结的小节、总结频率 | 识别主动复习薄弱的区域 |
| 提问记录 | 向教师提问的问题标题和关联小节 | 定位学生认为难以理解的具体知识点 |
| 讨论参与记录 | 参与讨论的频率和所属小节 | 辅助判断学习投入度和感兴趣的方向 |
| 课程材料（RAG） | 与薄弱知识点相关的课件 / 资料片段 | 确保计划任务与课程实际内容对齐 |

**个人信息**可在 [认证 API](./auth.md) 的「更新个人信息」接口中填写。

响应中 `data_sources` 字段会列出本次实际参与生成的数据类型，让前端可以展示"计划基于哪些信息生成"。

---

## 1. 生成个性化学习计划

```http
POST /api/student/courses/{course_id}/learning-plans
```

**功能说明：** 后端自动采集上述全部可用数据，结合 RAG 检索课程材料，调用 MiniMax 生成定制化学习计划。

**请求体：**

```json
{
  "goal": "两周内提升进程调度相关知识点的掌握程度",
  "available_time_per_day": 60
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| goal | string | 否 | 学习目标描述，不填则由 AI 根据采集到的薄弱点自动制定 |
| available_time_per_day | integer | 否 | 每天可用学习时间（分钟），默认 60 |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "plan_001",
    "course_id": "course_001",
    "course_name": "操作系统",
    "career_direction": "backend",
    "data_sources": [
      "scores",
      "profile",
      "chat_sessions",
      "summaries",
      "questions",
      "discussions",
      "course_materials"
    ],
    "analysis": {
      "current_level": "基础概念掌握一般，进程调度和内存分页部分偏弱",
      "weak_points": ["进程状态转换", "调度算法对比", "页面置换算法"],
      "frequently_asked": ["阻塞态和挂起态的区别", "LRU 和 FIFO 的性能差异"],
      "career_relevance": "进程调度和并发模型是后端开发的重要基础，建议重点加强",
      "engagement_note": "你在进程管理相关讨论中参与积极，但内存管理章节问答较少，建议加强该部分主动学习",
      "priority": "先补齐进程状态转换，再横向对比调度算法，最后攻克页面置换"
    },
    "rag_references": [
      {
        "section_id": "section_001",
        "section_title": "第一章：进程管理",
        "file_name": "section_001_slides.pdf",
        "excerpt": "进程的五种状态及转换条件如下..."
      },
      {
        "section_id": "section_003",
        "section_title": "第三章：内存管理",
        "file_name": "section_003_notes.pdf",
        "excerpt": "页面置换算法的性能对比：LRU 命中率最高，但实现代价较大..."
      }
    ],
    "plan": [
      {
        "day": 1,
        "task": "精读课件第 12-18 页「进程状态转换图」，重点理解阻塞态与挂起态的区别（你之前提问过这个知识点）",
        "duration_minutes": 60,
        "section_id": "section_001",
        "section_title": "第一章：进程管理"
      },
      {
        "day": 2,
        "task": "整理 FCFS、SJF、时间片轮转三种算法差异，尝试用代码模拟实现（结合后端开发场景理解其在操作系统中的意义）",
        "duration_minutes": 60,
        "section_id": "section_001",
        "section_title": "第一章：进程管理"
      },
      {
        "day": 3,
        "task": "复习页面置换算法，重点对比 LRU 和 FIFO 的适用场景，完成课件配套练习题",
        "duration_minutes": 60,
        "section_id": "section_003",
        "section_title": "第三章：内存管理"
      }
    ],
    "created_at": "2026-06-04T20:00:00+08:00"
  },
  "message": "created"
}
```

> `data_sources` 中各值含义：
>
> | 值 | 说明 |
> | --- | --- |
> | scores | 作业成绩与薄弱知识点 |
> | profile | 个人兴趣与岗位方向 |
> | chat_sessions | AI 问答会话记录 |
> | summaries | 知识点总结记录 |
> | questions | 向教师提问的记录 |
> | discussions | 讨论参与记录 |
> | course_materials | 课程材料 RAG 检索结果 |

---

## 2. 获取学习计划列表

```http
GET /api/student/courses/{course_id}/learning-plans
```

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| status | string | 否 | active、completed 或 archived |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001",
    "items": [
      {
        "id": "plan_001",
        "course_name": "操作系统",
        "status": "active",
        "career_direction": "backend",
        "data_sources": ["scores", "profile", "chat_sessions", "questions", "course_materials"],
        "created_at": "2026-06-04T20:00:00+08:00"
      }
    ],
    "total": 1
  },
  "message": "ok"
}
```

---

## 3. 获取学习计划详情

```http
GET /api/student/courses/{course_id}/learning-plans/{plan_id}
```

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "plan_001",
    "course_id": "course_001",
    "course_name": "操作系统",
    "career_direction": "backend",
    "status": "active",
    "data_sources": ["scores", "profile", "chat_sessions", "questions", "course_materials"],
    "analysis": {
      "current_level": "基础概念掌握一般，进程调度和内存分页部分偏弱",
      "weak_points": ["进程状态转换", "调度算法对比", "页面置换算法"],
      "frequently_asked": ["阻塞态和挂起态的区别", "LRU 和 FIFO 的性能差异"],
      "career_relevance": "进程调度和并发模型是后端开发的重要基础",
      "engagement_note": "你在进程管理相关讨论中参与积极，但内存管理章节问答较少",
      "priority": "先补齐进程状态转换，再横向对比调度算法，最后攻克页面置换"
    },
    "rag_references": [
      {
        "section_id": "section_001",
        "section_title": "第一章：进程管理",
        "file_name": "section_001_slides.pdf",
        "excerpt": "进程的五种状态及转换条件如下..."
      }
    ],
    "plan": [
      {
        "day": 1,
        "task": "精读课件第 12-18 页「进程状态转换图」",
        "duration_minutes": 60,
        "section_id": "section_001",
        "section_title": "第一章：进程管理"
      }
    ],
    "created_at": "2026-06-04T20:00:00+08:00"
  },
  "message": "ok"
}
```

---

## 4. 更新学习计划状态

```http
PATCH /api/student/courses/{course_id}/learning-plans/{plan_id}
```

**请求体：**

```json
{
  "status": "completed"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| status | string | 是 | active、completed 或 archived |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "plan_001",
    "status": "completed",
    "updated_at": "2026-06-18T20:00:00+08:00"
  },
  "message": "updated"
}
```
