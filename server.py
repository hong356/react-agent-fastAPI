import uuid
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, RedirectResponse, HTMLResponse

app = FastAPI(title="ReAct Agent 流式问答")

HTML_TPL = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>ReAct Agent 聊天</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            max-width: 900px;
            margin: 20px auto;
            padding: 0 15px;
            font-family: "Microsoft Yahei", sans-serif;
            background-color: #f5f7fa;
        }
        #chatBox {
            height: 560px;
            overflow-y: auto;
            background: white;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 16px;
            border: 1px solid #e5e7eb;
        }
        .msg-item {
            margin-bottom: 14px;
            display: flex;
            flex-direction: column;
        }
        .user-msg {
            align-items: flex-end;
        }
        .ai-msg {
            align-items: flex-start;
        }
        .msg-time {
            font-size: 12px;
            color: #888;
            margin-bottom: 4px;
            padding: 0 4px;
        }
        .msg-content {
            display: inline-block;
            padding: 10px 14px;
            border-radius: 8px;
            max-width: 75%;
            white-space: pre-wrap;
            word-break: break-word;
        }
        .user-msg .msg-content {
            background-color: #2563eb;
            color: white;
        }
        .ai-msg .msg-content {
            background-color: #eef2ff;
            color: #111;
        }
        #inputArea {
            display: flex;
            gap: 10px;
        }
        #userInput {
            flex: 1;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #ddd;
            font-size: 16px;
        }
        #sendBtn {
            padding: 0 22px;
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }
        #sendBtn:disabled {
            background: #94a3b8;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
<div id="chatBox"></div>
<div id="inputArea">
    <input id="userInput" placeholder="输入你的问题，例如：现在几点？" />
    <button id="sendBtn">发送</button>
</div>

<script>
const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

let currentAiContent = null;
let sessionId = localStorage.getItem("react_session_id");
if(!sessionId){
    sessionId = Date.now().toString();
    localStorage.setItem("react_session_id", sessionId);
}

function getLocalTime() {
    const now = new Date();
    return now.toLocaleTimeString();
}

function addUserMsg(text) {
    const wrapper = document.createElement('div');
    wrapper.className = "msg-item user-msg";
    const time = getLocalTime();
    wrapper.innerHTML = '<div class="msg-time">'+time+'</div><div class="msg-content"></div>';
    wrapper.querySelector('.msg-content').textContent = text;
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function createAiMsgBlock() {
    const wrapper = document.createElement('div');
    wrapper.className = "msg-item ai-msg";
    const time = getLocalTime();
    wrapper.innerHTML = '<div class="msg-time">'+time+'</div><div class="msg-content"></div>';
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
    return wrapper.querySelector('.msg-content');
}

async function sendMessage(){
    const question = userInput.value.trim();
    if (!question) return;
    addUserMsg(question);
    userInput.value = "";
    sendBtn.disabled = true;
    currentAiContent = null;

    currentAiContent = createAiMsgBlock();
    const source = new EventSource(`/chat/stream?q=${encodeURIComponent(question)}&session_id=${sessionId}`);

    source.onmessage = function (e) {
        if (e.data === "[DONE]") {
            source.close();
            currentAiContent = null;
            sendBtn.disabled = false;
            return;
        }
        if(currentAiContent){
            currentAiContent.textContent += e.data;
        }
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    source.onerror = function () {
        if (currentAiContent) {
            currentAiContent.textContent += "\\n【连接中断】";
        }
        source.close();
        currentAiContent = null;
        sendBtn.disabled = false;
    };
}

sendBtn.onclick = sendMessage;
userInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});
</script>
</body>
</html>
'''

@app.get("/")
async def index():
    return RedirectResponse("/chat")

@app.get("/chat")
async def chat_page():
    return HTMLResponse(HTML_TPL)

@app.get("/chat/stream")
async def chat_stream(q: str = Query(...), session_id: str = Query(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    from main import Agent
    agent = Agent(session_id=session_id)

    async def stream_generator():
        try:
            async for chunk in agent.run_stream(q):
                yield f"data: {chunk}\n\n"
            yield f"data: [DONE]\n\n"
        except Exception as e:
            yield f"data: 请求模型失败: {str(e)}\n\n"
            yield f"data: [DONE]\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)