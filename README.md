# ReAct智能体 Web服务项目
基于Python + FastAPI 实现的原生ReAct Agent，对接阿里云百炼大模型
不依赖LangChain，原生实现工具调用、流式对话、会话持久化

## 技术栈
Python 3.8、FastAPI、httpx异步请求、Pydantic、uvicorn
功能：SSE流式输出、对话历史截断、异步重试、异常分级处理、本地JSON会话存储

## 项目功能
1. ReAct 思维链路 + Tool Calling 工具调用
2. Web接口SSE逐字流式返回
3. Ctrl+C优雅退出、分层异常捕获
4. 对话自动截断，防止上下文过长400报错
5. 会话持久化，对话历史本地JSON保存
6. 请求失败自动重试机制

## 环境安装
```bash
pip install -r requirements.txt