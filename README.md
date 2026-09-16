# ReAct Agent 智能体项目
## 项目简介
基于Python + FastAPI实现ReAct推理智能体，对接阿里云DashScope大模型，SSE流式输出，支持会话持久化。
技术栈：Python3.8、FastAPI、httpx异步请求、Redis（可选）、本地JSON会话存储。

## 功能
1. ReAct 思考+工具调用智能体
2. SSE流式问答接口
3. 对话历史自动截断
4. 会话持久化存储（本地JSON / Redis可选）
5. 敏感密钥使用.env隔离，gitignore保护密钥不提交

## 启动步骤
1. 创建虚拟环境