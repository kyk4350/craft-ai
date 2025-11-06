import { useState, useEffect } from "react";
import InputForm from "../components/InputForm";
import Chatbot from "../components/Chatbot";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import ResultDisplay from "../components/ResultDisplay";
import {
  contentApi,
  FullContentGenerationResponse,
} from "../utils/api";

interface FormData {
  product_name: string;
  product_description: string;
  category: string;
  target_ages: string[];
  target_genders: string[];
  target_interests: string[];
  copy_tone: string;
}

export default function GeneratePageWithChat() {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FullContentGenerationResponse | null>(null);
  const [highlightedField, setHighlightedField] = useState<string | null>(null);

  const [formData, setFormData] = useState<FormData>({
    product_name: '',
    product_description: '',
    category: 'beauty',
    target_ages: ['20-29'],
    target_genders: ['여성'],
    target_interests: [] as string[],
    copy_tone: 'professional',
  });

  const handleFormUpdate = (updates: Record<string, any>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  };

  const handleHighlight = (field: string | null) => {
    setHighlightedField(field);
  };

  const handleSubmit = async (submittedFormData: FormData) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // API 호출
      const response = await contentApi.generateFullContent({
        product_name: submittedFormData.product_name,
        product_description: submittedFormData.product_description,
        category: submittedFormData.category,
        target_ages: submittedFormData.target_ages,
        target_genders: submittedFormData.target_genders,
        target_interests: submittedFormData.target_interests,
        copy_tone: submittedFormData.copy_tone,
        save_to_db: true,
      });

      setResult(response);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "콘텐츠 생성에 실패했습니다.";
      setError(errorMessage);
      console.error("Content generation error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    setResult(null);
  };

  // 결과 화면에서는 챗봇 숨김
  if (result && !isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              ContentCraft AI
            </h1>
            <p className="text-gray-600">
              AI 기반 마케팅 콘텐츠 자동 생성 플랫폼
            </p>
          </div>
          <ResultDisplay result={result} />
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-50 overflow-hidden">
      {/* 헤더 */}
      <div className="bg-white shadow-sm border-b px-6 py-4 flex-shrink-0">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900">
            ContentCraft AI
          </h1>
          <p className="text-sm text-gray-600">
            AI 기반 마케팅 콘텐츠 자동 생성 플랫폼
          </p>
        </div>
      </div>

      {/* 메인 컨텐츠: 2열 레이아웃 */}
      <div className="flex-1 min-h-0 overflow-hidden">
        <div className="h-full max-w-7xl mx-auto flex">
          {/* 왼쪽: 입력 폼 */}
          <div className="w-1/2 h-full overflow-y-auto overflow-x-hidden p-6 border-r border-gray-200 bg-gray-50">
            {isLoading ? (
              <LoadingSpinner message="AI가 맞춤형 콘텐츠를 생성하고 있습니다..." />
            ) : error ? (
              <ErrorMessage message={error} onRetry={handleRetry} />
            ) : (
              <InputForm
                onSubmit={handleSubmit}
                isLoading={isLoading}
                formData={formData}
                setFormData={setFormData}
                highlightedField={highlightedField}
              />
            )}
          </div>

          {/* 오른쪽: AI 챗봇 */}
          <div className="w-1/2 h-full bg-white overflow-hidden">
            <Chatbot
              onFormUpdate={handleFormUpdate}
              onHighlightField={handleHighlight}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
