import { useState } from 'react';
import ConversationalChatbot from '../components/ConversationalChatbot';
import ContentResult from '../components/ContentResult';

export default function GeneratePageNew() {
  const [generatedContent, setGeneratedContent] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  const handleContentGenerated = (content: any) => {
    setGeneratedContent(content);
    setIsGenerating(false);
  };

  const handleGenerationStart = () => {
    setIsGenerating(true);
  };

  return (
    <div className="h-full flex bg-gray-50">
      {/* 왼쪽: AI 챗봇 (40%) */}
      <div className="w-2/5 h-full bg-white border-r border-gray-200 flex flex-col">
        <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
          <h2 className="text-lg font-bold text-gray-800">AI 어시스턴트</h2>
          <p className="text-sm text-gray-600 mt-1">
            질문에 답변하면 자동으로 콘텐츠가 생성됩니다
          </p>
        </div>

        <div className="flex-1 overflow-hidden">
          <ConversationalChatbot
            onContentGenerated={handleContentGenerated}
            onGenerationStart={handleGenerationStart}
            currentContent={generatedContent}
          />
        </div>
      </div>

      {/* 오른쪽: 생성된 콘텐츠 결과 (60%) */}
      <div className="w-3/5 h-full flex flex-col">
        <div className="px-6 py-4 border-b border-gray-200 bg-white">
          <h2 className="text-lg font-bold text-gray-800">생성된 콘텐츠</h2>
          <p className="text-sm text-gray-600 mt-1">
            AI가 생성한 마케팅 콘텐츠를 확인하고 수정 요청할 수 있습니다
          </p>
        </div>

        <div className="flex-1 overflow-auto p-6">
          {isGenerating ? (
            <div className="flex flex-col items-center justify-center h-full">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600 font-medium">콘텐츠 생성 중...</p>
              <p className="mt-2 text-sm text-gray-500">AI가 최적의 콘텐츠를 만들고 있습니다</p>
            </div>
          ) : generatedContent ? (
            <ContentResult content={generatedContent} />
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <svg className="w-24 h-24 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <p className="text-lg font-medium">아직 생성된 콘텐츠가 없습니다</p>
              <p className="text-sm mt-2">왼쪽 AI 어시스턴트와 대화를 시작해보세요</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
