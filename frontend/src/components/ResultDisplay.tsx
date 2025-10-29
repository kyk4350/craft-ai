import { useState } from 'react';
import { FullContentGenerationResponse, performanceApi, PerformanceMetrics } from '../utils/api';
import Toast from './Toast';
import PerformanceDisplay from './PerformanceDisplay';

interface ResultDisplayProps {
  result: FullContentGenerationResponse;
}

export default function ResultDisplay({ result }: ResultDisplayProps) {
  const [selectedStrategy, setSelectedStrategy] = useState<number>(result.data.selected_strategy_id);
  const [showToast, setShowToast] = useState(false);
  const [showPerformance, setShowPerformance] = useState(false);
  const [performanceData, setPerformanceData] = useState<PerformanceMetrics | null>(null);
  const [isLoadingPerformance, setIsLoadingPerformance] = useState(false);
  const [performanceError, setPerformanceError] = useState<string | null>(null);
  const [isAiPrediction, setIsAiPrediction] = useState(false);
  const [confidenceScore, setConfidenceScore] = useState<number | undefined>(undefined);
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  // 성과 예측 실행
  const handlePredictPerformance = async () => {
    if (!result.data.content_id) {
      setPerformanceError('콘텐츠 ID가 없습니다. 데이터베이스 저장이 필요합니다.');
      return;
    }

    setIsLoadingPerformance(true);
    setPerformanceError(null);

    try {
      const response = await performanceApi.predictPerformance(result.data.content_id);

      if (response.success && response.data.exists && response.data.metrics) {
        setPerformanceData(response.data.metrics);
        setIsAiPrediction(response.data.is_ai_prediction || false);
        setConfidenceScore(response.data.confidence_score);
        setShowPerformance(true);
      } else {
        setPerformanceError('성과 데이터를 불러올 수 없습니다.');
      }
    } catch (error) {
      console.error('성과 예측 오류:', error);
      setPerformanceError(error instanceof Error ? error.message : '성과 예측 중 오류가 발생했습니다.');
    } finally {
      setIsLoadingPerformance(false);
    }
  };

  if (!result) return null;

  const { strategies, selected_strategy, copy, image } = result.data;

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">생성 완료!</h2>
        <p className="text-gray-600">
          소요 시간: <span className="font-semibold">{result.generation_time}초</span>
        </p>
      </div>

      {/* 전략 선택 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">마케팅 전략</h3>
        <div className="space-y-3">
          {strategies.map((strategy) => (
            <div
              key={strategy.id}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                selectedStrategy === strategy.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedStrategy(strategy.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-800 mb-1">{strategy.name}</h4>
                  <p className="text-sm text-gray-600 mb-2">{strategy.core_message}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded">
                      {strategy.emotion}
                    </span>
                    {selectedStrategy === strategy.id && (
                      <span className="text-blue-600 font-medium">✓ 선택됨</span>
                    )}
                  </div>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                <span className="font-medium">예상 효과:</span> {strategy.expected_effect}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* 카피 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">광고 카피</h3>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-lg text-gray-800 leading-relaxed mb-3">{copy.text}</p>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
              {copy.tone}
            </span>
            <span className="text-gray-400">•</span>
            <span>{copy.length}자</span>
          </div>
          {copy.hashtags && copy.hashtags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {copy.hashtags.map((tag, idx) => (
                <span key={idx} className="text-blue-600 text-sm">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 이미지 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">생성된 이미지</h3>

        {/* 이미지 표시 */}
        <div className="relative aspect-square w-full max-w-2xl mx-auto bg-gray-100 rounded-lg overflow-hidden">
          {image.local_url ? (
            <img
              src={`${API_BASE_URL}${image.local_url}`}
              alt="Generated content"
              className="w-full h-full object-contain"
              onError={(e) => {
                // 로컬 이미지 로드 실패 시 원본 URL 사용
                const target = e.target as HTMLImageElement;
                target.src = image.original_url;
              }}
            />
          ) : (
            <img
              src={image.original_url}
              alt="Generated content"
              className="w-full h-full object-contain"
            />
          )}
        </div>

        {/* 이미지 프롬프트 */}
        <div className="mt-4 p-3 bg-gray-50 rounded text-sm text-gray-600">
          <p className="font-medium mb-1">이미지 프롬프트:</p>
          <p className="text-xs">{image.prompt}</p>
        </div>

        {/* 다운로드 버튼 */}
        <div className="mt-4 flex gap-3">
          <a
            href={image.local_url ? `${API_BASE_URL}${image.local_url}` : image.original_url}
            download
            className="flex-1 py-2 px-4 bg-blue-600 text-white text-center rounded-md hover:bg-blue-700 transition-colors"
          >
            이미지 다운로드
          </a>
          <button
            onClick={() => {
              const copyWithHashtags = copy.hashtags && copy.hashtags.length > 0
                ? `${copy.text}\n\n${copy.hashtags.join(' ')}`
                : copy.text;
              navigator.clipboard.writeText(copyWithHashtags);
              setShowToast(true);
            }}
            className="flex-1 py-2 px-4 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            카피 복사
          </button>
        </div>
      </div>

      {/* 성과 예측 섹션 */}
      {result.data.content_id && (
        <div className="bg-white rounded-lg shadow-md p-6">
          {!showPerformance ? (
            <div className="text-center">
              <h3 className="text-xl font-bold text-gray-800 mb-3">📊 성과 분석</h3>
              <p className="text-gray-600 mb-4">
                AI가 가상 사용자 페르소나를 생성하여 이 콘텐츠의 예상 성과를 분석합니다.
              </p>
              <button
                onClick={handlePredictPerformance}
                disabled={isLoadingPerformance}
                className={`py-3 px-6 rounded-lg font-medium transition-colors ${
                  isLoadingPerformance
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700'
                }`}
              >
                {isLoadingPerformance ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    성과 분석 중... (약 10-15초 소요)
                  </span>
                ) : (
                  '성과 예측 보기'
                )}
              </button>
              {performanceError && (
                <p className="mt-3 text-red-600 text-sm">{performanceError}</p>
              )}
            </div>
          ) : (
            performanceData && (
              <PerformanceDisplay
                metrics={performanceData}
                isAiPrediction={isAiPrediction}
                confidenceScore={confidenceScore}
              />
            )
          )}
        </div>
      )}

      {/* 다시 생성 버튼 */}
      <div className="flex justify-center">
        <button
          onClick={() => window.location.reload()}
          className="py-3 px-6 bg-white text-gray-700 border-2 border-gray-300 rounded-md hover:bg-gray-50 transition-colors font-medium"
        >
          새로운 콘텐츠 생성하기
        </button>
      </div>

      {/* 토스트 메시지 */}
      {showToast && (
        <Toast
          message="카피와 해시태그가 복사되었습니다!"
          onClose={() => setShowToast(false)}
        />
      )}
    </div>
  );
}
