import React from 'react';
import { PerformanceMetrics } from '../utils/api';

interface PerformanceDisplayProps {
  metrics: PerformanceMetrics;
  isAiPrediction: boolean;
  confidenceScore?: number;
}

const PerformanceDisplay: React.FC<PerformanceDisplayProps> = ({
  metrics,
  isAiPrediction,
  confidenceScore
}) => {
  return (
    <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          📊 예상 성과
        </h3>
        {isAiPrediction && (
          <span className="text-xs px-3 py-1 bg-purple-100 text-purple-700 rounded-full">
            AI 예측 {confidenceScore ? `(신뢰도: ${(confidenceScore * 100).toFixed(0)}%)` : ''}
          </span>
        )}
      </div>

      {/* 주요 지표 그리드 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* CTR */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">클릭률 (CTR)</div>
          <div className="text-2xl font-bold text-blue-600">{metrics.ctr.toFixed(1)}%</div>
          <div className="text-xs text-gray-500 mt-1">
            {metrics.clicks.toLocaleString()} / {metrics.impressions.toLocaleString()}
          </div>
        </div>

        {/* 참여도 */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">참여도</div>
          <div className="text-2xl font-bold text-green-600">{metrics.engagement_rate.toFixed(1)}%</div>
          <div className="text-xs text-gray-500 mt-1">좋아요/댓글/공유</div>
        </div>

        {/* 전환율 */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">전환율</div>
          <div className="text-2xl font-bold text-orange-600">{metrics.conversion_rate.toFixed(1)}%</div>
          <div className="text-xs text-gray-500 mt-1">구매/신청</div>
        </div>

        {/* 브랜드 기억도 */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">브랜드 기억도</div>
          <div className="text-2xl font-bold text-purple-600">{metrics.brand_recall_score.toFixed(0)}</div>
          <div className="text-xs text-gray-500 mt-1">/ 100점</div>
        </div>
      </div>

      {/* AI 예측 안내 */}
      {isAiPrediction && (
        <div className="mt-4 p-3 bg-blue-100 rounded-lg text-sm text-blue-800">
          💡 이 성과는 AI가 가상의 사용자 페르소나를 생성하여 예측한 결과입니다.
          실제 캠페인 진행 후 추적 URL을 통해 실제 데이터로 업데이트할 수 있습니다.
        </div>
      )}
    </div>
  );
};

export default PerformanceDisplay;
