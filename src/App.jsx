import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, ChevronRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useMockStream } from './hooks/useMockStream';
import ReportView from './components/ReportView';

function App() {
  const [input, setInput] = useState('');
  const { messages, isStreaming, generateResponse, reportData } = useMockStream();
  const messagesEndRef = useRef(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    generateResponse(input);
    setInput('');
  };

  return (
    <div className="flex h-screen w-full bg-gray-50 text-gray-800 font-sans antialiased">
      {/* 左侧：聊天区域 */}
      <div className="flex-1 flex flex-col h-full max-w-3xl mx-auto bg-white shadow-lg rounded-tr-2xl rounded-br-2xl z-10 w-full sm:w-1/2 lg:w-3/5 transition-all duration-300 ease-in-out">
        
        {/* Header */}
        <div className="h-16 border-b border-gray-100 flex items-center px-6 bg-white shrink-0 rounded-tr-2xl">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center mr-4 shadow-md">
            <Sparkles className="text-white w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-gray-900">XSimple AI 报表助手</h1>
            <p className="text-xs text-gray-500">智能生成销售、用户增长和财务报表</p>
          </div>
        </div>

        {/* Messages List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50">
          {/* Welcome Message */}
          {messages.length === 0 && (
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 bg-gradient-to-br from-indigo-100 to-purple-100 text-indigo-600">
                <Bot size={20} />
              </div>
              <div className="max-w-[80%] rounded-2xl px-5 py-4 text-sm leading-relaxed bg-white text-gray-700 rounded-bl-none shadow-sm border border-gray-100">
                <p className="font-medium text-indigo-700 mb-2">你好！我是 XSimple 智能助手</p>
                <p className="text-gray-600">我可以帮你生成销售、用户增长或财务报表。请告诉我你的需求。</p>
              </div>
            </div>
          )}
          
          {/* Existing Messages */}
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              {/* Avatar */}
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                msg.role === 'assistant' ? 'bg-gradient-to-br from-indigo-100 to-purple-100 text-indigo-600' : 'bg-gradient-to-br from-gray-100 to-gray-200 text-gray-700'
              }`}>
                {msg.role === 'assistant' ? <Bot size={20} /> : <User size={20} />}
              </div>

              {/* Message Bubble */}
              <div className={`max-w-[80%] rounded-2xl px-5 py-4 text-sm leading-relaxed ${
                msg.role === 'user' 
                  ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-br-none shadow-md' 
                  : 'bg-white text-gray-700 rounded-bl-none shadow-sm border border-gray-100'
              }`}>
                {msg.role === 'assistant' ? (
                  /* 使用 ReactMarkdown 渲染 AI 的格式化文本 */
                  <ReactMarkdown 
                    components={{
                      p: ({node, ...props}) => <span {...props} />, // 防止多余换行
                      strong: ({node, ...props}) => <span className="font-bold text-indigo-700" {...props} />
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  msg.content
                )}
                
                {/* 正在生成的 Loading 动画 */}
                {msg.role === 'assistant' && isStreaming && idx === messages.length - 1 && (
                  <div className="inline-flex items-center ml-2 space-x-1">
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-white animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-white animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-white animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-100 bg-white rounded-br-2xl">
          <form onSubmit={handleSubmit} className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="输入 '销售' 生成报表，或询问其他问题..."
              className="w-full bg-gray-50 border border-gray-200 rounded-xl py-3 pl-4 pr-16 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all duration-300 ease-in-out shadow-sm"
            />
            <button
              type="submit"
              disabled={!input.trim() || isStreaming}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 disabled:opacity-50 disabled:hover:from-indigo-500 disabled:hover:to-purple-600 transition-all duration-300 ease-in-out shadow-md disabled:shadow-none"
            >
              {isStreaming ? <ChevronRight size={18} /> : <Send size={18} />}
            </button>
          </form>
          <p className="text-xs text-center text-gray-500 mt-3">
            AI 生成内容仅供参考。 Developed by XSimple.
          </p>
        </div>
      </div>

      {/* 右侧：报表预览区域 (在大屏幕上显示，移动端可隐藏) */}
      <div className="hidden lg:block w-2/5 h-full bg-white rounded-l-2xl shadow-lg transition-all duration-300 ease-in-out">
        <ReportView data={reportData} />
      </div>
    </div>
  );
}

export default App;