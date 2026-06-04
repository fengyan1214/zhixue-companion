# 认证 API

> 基础路径：`/api/auth`
>
> 注册和登录接口无需携带 JWT 令牌，其余接口均需在请求头中携带：
> ```
> Authorization: Bearer <token>
> ```

---

## 1. 学生注册

```http
POST /api/auth/register/student
```

**功能说明：** 学生注册账号，填写学号、姓名、班级和密码。

**请求体：**

```json
{
  "username": "20240101",
  "name": "张三",
  "class_name": "计算机 2401 班",
  "password": "your_password"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 学号，登录时使用 |
| name | string | 是 | 真实姓名 |
| class_name | string | 是 | 班级名称 |
| password | string | 是 | 登录密码（长度 6-32 位） |

**响应示例：**

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

---

## 2. 教师注册

```http
POST /api/auth/register/teacher
```

**功能说明：** 教师注册账号，填写工号、姓名和密码。

**请求体：**

```json
{
  "username": "T20240001",
  "name": "李老师",
  "password": "your_password"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 工号，登录时使用 |
| name | string | 是 | 真实姓名 |
| password | string | 是 | 登录密码（长度 6-32 位） |

**响应示例：**

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

---

## 3. 登录

```http
POST /api/auth/login
```

**功能说明：** 学生和教师统一登录入口，输入用户名和密码，返回 JWT 令牌和用户角色。

**请求体：**

```json
{
  "username": "20240101",
  "password": "your_password"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 学号或工号 |
| password | string | 是 | 登录密码 |

**响应示例：**

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

---

## 4. 获取当前用户信息

```http
GET /api/auth/me
```

**功能说明：** 返回当前已登录用户的基本信息，需携带 JWT 令牌。

**响应示例（学生）：**

```json
{
  "success": true,
  "data": {
    "id": "user_001",
    "username": "20240101",
    "name": "张三",
    "role": "student",
    "class_name": "计算机 2401 班",
    "profile": {
      "interests": ["后端开发", "算法"],
      "career_direction": "backend",
      "bio": "喜欢研究系统底层原理"
    }
  },
  "message": "ok"
}
```

---

## 5. 更新个人信息

```http
PATCH /api/auth/me
```

**功能说明：** 更新当前用户的个人资料，学生可填写兴趣爱好和岗位方向，供个性化学习计划生成使用。

**请求体（学生示例）：**

```json
{
  "bio": "喜欢研究系统底层原理",
  "interests": ["后端开发", "算法", "操作系统"],
  "career_direction": "backend"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| bio | string | 否 | 个人简介 |
| interests | array | 否 | 兴趣爱好列表，如 ["后端开发", "算法"] |
| career_direction | string | 否 | 岗位方向枚举：backend / frontend / product / algorithm / data / devops / other |
| class_name | string | 否 | 班级名称（仅学生可更新） |

> `career_direction` 枚举值说明：
>
> | 值 | 中文 |
> | --- | --- |
> | backend | 后端开发 |
> | frontend | 前端开发 |
> | product | 产品经理 |
> | algorithm | 算法工程师 |
> | data | 数据分析 |
> | devops | 运维/DevOps |
> | other | 其他 |

**响应示例：**

```json
{
  "success": true,
  "data": {
    "id": "user_001",
    "bio": "喜欢研究系统底层原理",
    "interests": ["后端开发", "算法", "操作系统"],
    "career_direction": "backend",
    "updated_at": "2026-06-04T10:00:00+08:00"
  },
  "message": "updated"
}
```

---

## 6. 修改密码

```http
POST /api/auth/change-password
```

**请求体：**

```json
{
  "old_password": "old_pass",
  "new_password": "new_pass"
}
```

**响应示例：**

```json
{
  "success": true,
  "data": {},
  "message": "password changed"
}
```
