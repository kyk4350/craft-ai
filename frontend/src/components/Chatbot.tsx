import { useState, useRef, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  formUpdates?: Record<string, any>;
}

interface ChatbotProps {
  onFormUpdate: (updates: Record<string, any>) => void;
  onHighlightField: (field: string | null) => void;
}

export default function Chatbot({ onFormUpdate, onHighlightField }: ChatbotProps) {
  // Zustand store에서 토큰 가져오기
  const token = useAuthStore((state) => state.token);

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: '안녕하세요! 🎨 ContentCraft AI 어시스턴트입니다.\n\n어떤 제품의 마케팅 콘텐츠를 만들고 싶으신가요?\n제품명이나 간단한 설명을 알려주세요!',
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // 자동 스크롤 - 메시지 컨테이너의 scrollTop을 직접 조작
  useEffect(() => {
    // 새 메시지가 추가될 때만 (초기 마운트는 제외)
    if (messages.length > 1) {
      const container = messagesContainerRef.current;
      if (container) {
        // 컨테이너 내부에서만 스크롤 (페이지 전체 스크롤 안 됨)
        container.scrollTop = container.scrollHeight;
      }
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // input을 미리 저장 (setInput으로 비우기 전에)
    const currentInput = input.trim();

    const userMessage: ChatMessage = {
      role: 'user',
      content: currentInput,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      console.log('🚀 챗봇 API 호출 시작:', currentInput);
      console.log('🔑 토큰 확인:', token ? '존재함' : '없음');

      if (!token) {
        throw new Error('로그인이 필요합니다. 다시 로그인해주세요.');
      }

      console.log('📤 요청 데이터:', {
        message: currentInput,
        conversation_history_count: messages.slice(-5).length,
      });

      const response = await fetch('http://localhost:8000/api/chat/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: currentInput,
          conversation_history: messages.slice(-5), // 최근 5개 메시지만 컨텍스트로 전송
        }),
      });

      console.log('📥 응답 상태:', response.status, response.statusText);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'API 호출 실패');
      }

      const data = await response.json();
      console.log('✅ 응답 데이터:', data);

      // 폼 업데이트
      if (data.form_updates && Object.keys(data.form_updates).length > 0) {
        console.log('📝 폼 업데이트:', data.form_updates);
        onFormUpdate(data.form_updates);

        // 업데이트된 필드들을 순차적으로 하이라이트
        const fields = Object.keys(data.form_updates);
        for (let i = 0; i < fields.length; i++) {
          setTimeout(() => {
            onHighlightField(fields[i]);
            setTimeout(() => onHighlightField(null), 1500);
          }, i * 500);
        }
      }

      // 어시스턴트 응답 추가
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        formUpdates: data.form_updates,
      };

      setMessages(prev => [...prev, assistantMessage]);
      console.log('✅ 챗봇 처리 완료');
    } catch (error) {
      console.error('❌ 챗봇 에러:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `죄송합니다. 처리 중 오류가 발생했습니다.\n${error instanceof Error ? error.message : '다시 시도해주세요.'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      console.log('🏁 챗봇 API 호출 종료');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 빠른 액션 버튼들
  const quickActions = [
    { icon: '💡', label: '트렌드 키워드', action: () => setInput('요즘 트렌드 키워드를 알려주세요') },
    { icon: '🎯', label: '인기 타겟 추천', action: () => setInput('인기있는 타겟 고객층을 추천해주세요') },
    { icon: '✨', label: '성공 사례', action: () => setInput('비슷한 제품의 성공 사례를 알려주세요') },
    { icon: '🔄', label: '다시 시작', action: () => {
      setMessages([{
        role: 'assistant',
        content: '새로 시작하겠습니다! 어떤 제품의 콘텐츠를 만들고 싶으신가요?',
        timestamp: new Date(),
      }]);
    }},
  ];

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-blue-50 to-white min-h-0">
      {/* 헤더 */}
      <div className="bg-blue-600 text-white p-4 shadow-md flex-shrink-0">
        <div className="flex items-center space-x-2">
          <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-2xl">
            🤖
          </div>
          <div>
            <h3 className="font-bold text-lg">AI 어시스턴트</h3>
            <p className="text-xs text-blue-100">대화로 빠르게 생성하기</p>
          </div>
        </div>
      </div>

      {/* 메시지 영역 */}
      <div ref={messagesContainerRef} className="flex-1 min-h-0 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white shadow-md border border-gray-200'
              }`}
            >
              <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
              {msg.formUpdates && Object.keys(msg.formUpdates).length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-500 mb-1">📝 폼 업데이트:</p>
                  <div className="text-xs bg-green-50 p-2 rounded">
                    {Object.entries(msg.formUpdates).map(([key, value]) => (
                      <div key={key} className="text-green-700">
                        • {key}: {JSON.stringify(value)}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <p className="text-xs opacity-60 mt-1">
                {msg.timestamp.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white shadow-md border border-gray-200 rounded-lg p-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 빠른 액션 버튼 */}
      <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 flex-shrink-0">
        <div className="flex space-x-2 overflow-x-auto pb-2">
          {quickActions.map((action, idx) => (
            <button
              key={idx}
              onClick={action.action}
              disabled={isLoading}
              className="flex items-center space-x-1 px-3 py-1 bg-white border border-gray-300 rounded-full text-xs hover:bg-gray-100 transition whitespace-nowrap disabled:opacity-50"
            >
              <span>{action.icon}</span>
              <span>{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 입력 영역 */}
      <div className="p-4 bg-white border-t border-gray-200 flex-shrink-0">
        <div className="flex space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="메시지를 입력하세요... (Shift+Enter: 줄바꿈)"
            disabled={isLoading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none disabled:bg-gray-100"
            rows={2}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <span className="text-xl">➤</span>
            )}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          💬 자연스럽게 대화하듯 입력해주세요. AI가 자동으로 폼을 채워드립니다!
        </p>
      </div>
    </div>
  );
}
