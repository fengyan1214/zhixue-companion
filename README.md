# 智学伴侣 AI Campus Companion

智学伴侣是一个以 AI 为核心的校园学习辅助系统，分为学生端和教师端。学生端提供智能问答、作业管理、知识点总结和个性化学习计划；教师端提供 AI 批改、查重与作业比对能力。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 19、TypeScript、Vite、Tailwind CSS |
| 后端 | Python、FastAPI、SQLAlchemy 2.0、uv |
| 大模型 | MiniMax（abab6.5s-chat + embo-01 Embedding） |
| 向量库 | ChromaDB（默认）/ pgvector（生产可选） |
| 数据库 | SQLite（默认）/ PostgreSQL（生产可选） |
| 文件处理 | C++ pybind11 扩展 |

## 快速开始

```bash
# 后端
cp backend/.env.example backend/.env  # 填写 MINIMAX_API_KEY
./server.sh start                     # 后台启动，日志写入 logs/backend.log
./server.sh status                    # 查看运行状态

# 前端
cd frontend && pnpm install && pnpm dev
```

## 文档

详细文档见 [docs/](docs/) 目录。

## 核心功能

**学生端**
- 智能问答：基于课程材料 RAG 检索 + MiniMax 回答，支持多轮会话
- 作业管理：查看、提交作业，支持文本和文件两种方式
- 知识点总结：对课堂内容生成结构化摘要、重难点、复习建议
- 个性化学习计划：综合成绩、问答、测验、讨论等 8 类信号生成按天学习安排，支持进度跟踪和多轮调整

**教师端**
- AI 批改：根据参考答案和评分标准批量生成评分、评语、扣分点
- 查重与作业比对：C++ 指纹粗筛 + MiniMax 语义分析，输出可疑对和多维比对报告
