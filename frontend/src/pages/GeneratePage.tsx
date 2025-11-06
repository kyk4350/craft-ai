import { useState } from "react";
import InputForm from "../components/InputForm";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import ResultDisplay from "../components/ResultDisplay";
import {
  contentApi,
  FullContentGenerationRequest,
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

export default function GeneratePage() {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FullContentGenerationResponse | null>(
    null
  );

  const handleSubmit = async (formData: FormData) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // API 호출
      const response = await contentApi.generateFullContent({
        product_name: formData.product_name,
        product_description: formData.product_description,
        category: formData.category,
        target_ages: formData.target_ages,
        target_genders: formData.target_genders,
        target_interests: formData.target_interests,
        copy_tone: formData.copy_tone,
        save_to_db: true, // DB 저장 (성과 예측 기능을 위해 필요)
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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            ContentCraft AI
          </h1>
          <p className="text-gray-600">
            AI 기반 마케팅 콘텐츠 자동 생성 플랫폼
          </p>
        </div>

        {/* 메인 콘텐츠 */}
        {!isLoading && !result && (
          <InputForm onSubmit={handleSubmit} isLoading={isLoading} />
        )}

        {isLoading && (
          <LoadingSpinner message="AI가 맞춤형 콘텐츠를 생성하고 있습니다..." />
        )}

        {error && <ErrorMessage message={error} onRetry={handleRetry} />}

        {result && !isLoading && <ResultDisplay result={result} />}
      </div>
    </div>
  );
}
