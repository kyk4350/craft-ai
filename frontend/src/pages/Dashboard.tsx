import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { analyticsApi } from '../utils/api';

interface Summary {
  total_contents: number;
  total_with_performance: number;
  avg_ctr: number;
  avg_engagement_rate: number;
  avg_conversion_rate: number;
  avg_brand_recall: number;
  max_ctr: number;
  best_content: {
    content_id: number;
    copy_text: string;
    ctr: number;
    product_name: string;
  } | null;
}

interface StrategyPerformance {
  strategy_name: string;
  avg_ctr: number;
  avg_engagement_rate: number;
  avg_conversion_rate: number;
  avg_brand_recall: number;
  count: number;
}

interface TargetPerformance {
  target_label: string;
  target_age_group: string;
  target_gender: string;
  avg_ctr: number;
  avg_engagement_rate: number;
  avg_conversion_rate: number;
  avg_brand_recall: number;
  count: number;
}

interface TopContent {
  content_id: number;
  copy_text: string;
  product_name: string;
  target: string;
  ctr: number;
  engagement_rate: number;
  conversion_rate: number;
  created_at: string;
}

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [summary, setSummary] = useState<Summary | null>(null);
  const [strategyData, setStrategyData] = useState<StrategyPerformance[]>([]);
  const [targetData, setTargetData] = useState<TargetPerformance[]>([]);
  const [topContents, setTopContents] = useState<TopContent[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError('');

    try {
      const [summaryRes, strategyRes, targetRes, topRes] = await Promise.all([
        analyticsApi.getSummary(),
        analyticsApi.getPerformanceByStrategy(),
        analyticsApi.getPerformanceByTarget(),
        analyticsApi.getTopContents(5)
      ]);

      setSummary(summaryRes.data);
      setStrategyData(strategyRes.data);
      setTargetData(targetRes.data);
      setTopContents(topRes.data);
    } catch (err: any) {
      setError(err.message || '데이터 로딩 중 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">데이터 로딩 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <p className="text-red-800">{error}</p>
          <button
            onClick={loadDashboardData}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">마케팅 성과 대시보드</h1>
          <p className="mt-2 text-gray-600">전체 콘텐츠 통계 및 분석</p>
        </div>

        {/* 핵심 지표 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* 총 콘텐츠 수 */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">총 콘텐츠</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{summary?.total_contents || 0}</p>
                <p className="text-xs text-gray-500 mt-1">성과 데이터: {summary?.total_with_performance || 0}개</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>

          {/* 평균 CTR */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">평균 CTR</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{summary?.avg_ctr || 0}%</p>
                <p className="text-xs text-gray-500 mt-1">클릭률</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                </svg>
              </div>
            </div>
          </div>

          {/* 평균 참여율 */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">평균 참여율</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{summary?.avg_engagement_rate || 0}%</p>
                <p className="text-xs text-gray-500 mt-1">좋아요/댓글/공유</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                </svg>
              </div>
            </div>
          </div>

          {/* 최고 CTR */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">최고 CTR</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{summary?.max_ctr || 0}%</p>
                {summary?.best_content && (
                  <p className="text-xs text-gray-500 mt-1">{summary.best_content.product_name}</p>
                )}
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* 차트 영역 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* 전략별 성과 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">전략별 평균 성과</h3>
            {strategyData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={strategyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="strategy_name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="avg_ctr" fill="#3B82F6" name="CTR (%)" />
                  <Bar dataKey="avg_engagement_rate" fill="#8B5CF6" name="참여율 (%)" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-8">데이터가 없습니다</p>
            )}
          </div>

          {/* 타겟별 성과 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">타겟별 평균 CTR</h3>
            {targetData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={targetData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="target_label" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="avg_ctr" stroke="#10B981" strokeWidth={2} name="CTR (%)" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-8">데이터가 없습니다</p>
            )}
          </div>
        </div>

        {/* 최고 성과 콘텐츠 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top 5 성과 콘텐츠</h3>
          {topContents.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">순위</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">카피</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">제품</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">타겟</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CTR</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">참여율</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {topContents.map((content, index) => (
                    <tr key={content.content_id} className={index === 0 ? 'bg-yellow-50' : ''}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-lg font-bold ${index === 0 ? 'text-yellow-600' : 'text-gray-600'}`}>
                          {index === 0 ? '🏆' : `${index + 1}`}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 max-w-md">{content.copy_text}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{content.product_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{content.target}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          {content.ctr}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">{content.engagement_rate}%</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">데이터가 없습니다</p>
          )}
        </div>

        {/* AI 인사이트 */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 AI 인사이트</h3>
          <div className="space-y-3">
            {strategyData.length > 0 && (
              <p className="text-gray-700">
                <strong className="text-blue-600">
                  {strategyData.reduce((prev, current) => prev.avg_ctr > current.avg_ctr ? prev : current).strategy_name}
                </strong>{' '}
                전략이 평균 CTR{' '}
                <strong>{strategyData.reduce((prev, current) => prev.avg_ctr > current.avg_ctr ? prev : current).avg_ctr}%</strong>
                로 가장 효과적입니다.
              </p>
            )}
            {targetData.length > 0 && (
              <p className="text-gray-700">
                <strong className="text-purple-600">
                  {targetData.reduce((prev, current) => prev.avg_ctr > current.avg_ctr ? prev : current).target_label}
                </strong>{' '}
                타겟이 평균 CTR{' '}
                <strong>{targetData.reduce((prev, current) => prev.avg_ctr > current.avg_ctr ? prev : current).avg_ctr}%</strong>
                로 가장 높은 성과를 보입니다.
              </p>
            )}
            {summary && summary.total_with_performance > 0 && (
              <p className="text-gray-700">
                총 <strong>{summary.total_contents}개</strong> 콘텐츠 중{' '}
                <strong>{summary.total_with_performance}개</strong>의 성과 데이터가 수집되었습니다.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
