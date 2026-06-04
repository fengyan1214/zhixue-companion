# 分数与成绩 API

> 所有接口均需携带 JWT 令牌。

---

## 说明

分数体系以**课程**为单位，每门课程下每份作业批改后产生一条成绩记录。课程总分为所有已批改作业分数的加权汇总。

---

## 一、学生端成绩 API

### 1.1 查看课程成绩明细

```http
GET /api/student/courses/{course_id}/scores
```

**功能说明：** 学生查看自己在该课程内各作业的得分明细和课程总分。

**权限：** `role = student`，且已加入该课程。

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001",
    "course_name": "操作系统",
    "total_score": 87.5,
    "rank": 8,
    "total_students": 35,
    "records": [
      {
        "assignment_id": "assignment_001",
        "assignment_title": "进程管理练习",
        "section_title": "第一章：进程管理",
        "full_score": 100,
        "score": 88,
        "ai_score": 86,
        "teacher_comment": "补充了一些关键点，酌情加分。",
        "graded_at": "2026-06-09T10:00:00+08:00"
      },
      {
        "assignment_id": "assignment_002",
        "assignment_title": "内存管理分析",
        "section_title": "第二章：内存管理",
        "full_score": 100,
        "score": 87,
        "ai_score": 87,
        "teacher_comment": null,
        "graded_at": "2026-06-10T10:00:00+08:00"
      }
    ]
  },
  "message": "ok"
}
```

---

### 1.2 查看所有课程的成绩汇总

```http
GET /api/student/scores
```

**功能说明：** 学生查看自己所有已加入课程的成绩汇总，方便跨课程横向对比，也用于个性化学习计划生成时的参考数据源。

**权限：** `role = student`

**响应示例：**

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "course_id": "course_001",
        "course_name": "操作系统",
        "total_score": 87.5,
        "rank": 8,
        "total_students": 35,
        "graded_assignments": 2,
        "total_assignments": 5
      },
      {
        "course_id": "course_002",
        "course_name": "高等数学",
        "total_score": 72.0,
        "rank": 20,
        "total_students": 42,
        "graded_assignments": 1,
        "total_assignments": 3
      }
    ]
  },
  "message": "ok"
}
```

> 此接口为便捷聚合接口，不属于某门课程，故不含 `course_id` 路径段。

---

## 二、教师端成绩 API

### 2.1 查看课程成绩分布

```http
GET /api/teacher/courses/{course_id}/scores
```

**功能说明：** 教师查看该课程所有学生的成绩分布，了解整体学情。

**权限：** `role = teacher`

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| sort_by | string | 否 | 排序字段：total_score（默认）、name |
| order | string | 否 | asc 或 desc（默认 desc） |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "course_id": "course_001",
    "course_name": "操作系统",
    "statistics": {
      "average_score": 82.3,
      "max_score": 98.0,
      "min_score": 45.0,
      "pass_rate": 0.91,
      "excellent_rate": 0.34
    },
    "score_distribution": {
      "90_100": 8,
      "80_89": 12,
      "70_79": 9,
      "60_69": 4,
      "below_60": 2
    },
    "items": [
      {
        "student_id": "user_001",
        "student_name": "张三",
        "class_name": "计算机 2401 班",
        "total_score": 87.5,
        "graded_assignments": 2,
        "rank": 8
      }
    ],
    "total": 35
  },
  "message": "ok"
}
```

---

### 2.2 查看某学生在课程内的详细成绩

```http
GET /api/teacher/courses/{course_id}/scores/{student_id}
```

**权限：** `role = teacher`

**响应示例：**

```json
{
  "success": true,
  "data": {
    "student_id": "user_001",
    "student_name": "张三",
    "course_id": "course_001",
    "total_score": 87.5,
    "rank": 8,
    "records": [
      {
        "assignment_id": "assignment_001",
        "assignment_title": "进程管理练习",
        "section_title": "第一章：进程管理",
        "full_score": 100,
        "score": 88,
        "ai_score": 86,
        "deductions": [
          {
            "point": "进程状态转换条件说明不完整",
            "minus": 6
          }
        ],
        "suggestions": ["补充阻塞态与就绪态的转换条件"],
        "teacher_comment": "补充了一些关键点，酌情加分。",
        "graded_at": "2026-06-09T10:00:00+08:00"
      }
    ]
  },
  "message": "ok"
}
```
