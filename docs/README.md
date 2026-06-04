# 文档目录

| 目录 / 文件 | 说明 |
|---|---|
| [design/](design/) | 设计文档：架构、数据模型、AI 功能、安全 |
| [api/](api/) | REST API 接口文档（按模块拆分） |
| [cpp_api.md](cpp_api.md) | Python ↔ C++ pybind11 接口说明 |
| [testing.md](testing.md) | 单元测试说明：覆盖范围、用例列表、运行方式 |

## 设计文档（[design/](design/)）

| 文档 | 说明 |
|---|---|
| [architecture.md](design/architecture.md) | 整体架构、技术选型、关键设计决策、部署 |
| [data_model.md](design/data_model.md) | 17 张表的字段说明、E-R 关系、设计意图 |
| [ai_design.md](design/ai_design.md) | RAG 检索、学习计划、智能问答、批改、查重的 AI 设计 |
| [security_design.md](design/security_design.md) | JWT、密码存储、权限模型、安全检查清单 |

## API 文档（[api/](api/)）

| 文档 | 说明 |
|---|---|
| [README.md](api/README.md) | API 总览：规范、鉴权、响应格式 |
| [auth.md](api/auth.md) | 注册、登录 |
| [courses.md](api/courses.md) | 课程管理 |
| [sections.md](api/sections.md) | 课程小节 |
| [assignments.md](api/assignments.md) | 作业（教师发布 + 学生提交） |
| [chat.md](api/chat.md) | 智能问答 |
| [learning_plans.md](api/learning_plans.md) | 学习计划 |
| [quizzes.md](api/quizzes.md) | 测验 |
| [summaries.md](api/summaries.md) | 知识总结 |
| [discussions.md](api/discussions.md) | 课程讨论 |
| [questions.md](api/questions.md) | 课程提问 |
| [announcements.md](api/announcements.md) | 课程公告 |
| [scores.md](api/scores.md) | 成绩概览 |
