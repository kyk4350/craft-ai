import { useState } from 'react';
import InputForm from '../components/InputForm';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import ResultDisplay from '../components/ResultDisplay';
import { contentApi } from '../utils/api';

export default function GeneratePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleSubmit = async (formData) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // API 호출
      const response = await contentApi.generateFullContent({
        product_name: formData.product_name,
        product_description: formData.product_description,
        category: formData.category,
        target_age: formData.target_age,
        target_gender: formData.target_gender,
        target_interests: formData.target_interests,
        copy_tone: formData.copy_tone,
        save_to_db: false, // 3주차에는 DB 저장 안함 (히스토리 기능은 5주차)
      });

      setResult(response);
    } catch (err) {
      setError(err.message || '콘텐츠 생성에 실패했습니다.');
      console.error('Content generation error:', err);
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

        {error && (
          <ErrorMessage message={error} onRetry={handleRetry} />
        )}

        {result && !isLoading && (
          <ResultDisplay result={result} />
        )}
      </div>
    </div>
  );
}
