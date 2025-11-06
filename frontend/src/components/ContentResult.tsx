interface ContentResultProps {
  content: any;
}

export default function ContentResult({ content }: ContentResultProps) {
  console.log('ContentResult received:', content); // 디버깅용

  if (!content) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-400">
        <p className="text-lg font-medium">콘텐츠가 없습니다</p>
      </div>
    );
  }

  // API 응답 구조 파싱 - copy와 image는 최상위에 있음!
  const selectedStrategy = content.selected_strategy || content.selectedStrategy || {};
  const copyData = content.copy || {};
  const imageData = content.image || {};

  // copy_text 파싱 (객체에서 text 속성 추출)
  let copy_text = '';
  let hashtags = [];
  let tone = '';
  if (typeof copyData === 'object' && copyData !== null) {
    copy_text = copyData.text || '';
    hashtags = copyData.hashtags || [];
    tone = copyData.tone || '';
  } else {
    copy_text = copyData || '';
  }

  // image_url 파싱 (객체에서 URL 추출)
  let image_url = '';
  if (typeof imageData === 'object' && imageData !== null) {
    image_url = imageData.original_url || imageData.url || imageData.path || imageData.src || '';
  } else {
    image_url = imageData || '';
  }

  // 백엔드 URL 추가 (상대 경로인 경우, data: URL은 제외)
  if (image_url && !image_url.startsWith('http') && !image_url.startsWith('data:')) {
    image_url = `http://localhost:8000${image_url.startsWith('/') ? '' : '/'}${image_url}`;
  }

  // 타겟 세그먼트 파싱 - API 응답에서 직접 가져오기
  const targetInsights = content.target_insights || content.targetInsights || {};
  const target_segment = {
    // API 응답의 target_age_group, target_gender, target_interests 사용
    ages: content.target_age_group ? [content.target_age_group] : (content.target_ages || []),
    genders: content.target_gender ? [content.target_gender] : (content.target_genders || []),
    interests: content.target_interests || []
  };

  // 성과 예측 - 백엔드 응답에서 직접 가져오기
  let performance_prediction = {
    reach: null,
    engagement: null,
    conversions: null,
    confidence: null,
    ctr: null,
    conversion_rate: null
  };

  // 백엔드가 performance_prediction을 응답에 포함시킴
  const performanceData = content.performance_prediction;
  const selectedStrategyData = content.selected_strategy || content.selectedStrategy || {};
  const performancePred = selectedStrategyData.performance_prediction || selectedStrategyData.performancePrediction || {};

  if (performanceData) {
    // 실제 AI 시뮬레이션 성과 데이터 사용
    performance_prediction = {
      reach: performanceData.impressions || null,
      engagement: performanceData.engagement_rate || null,
      conversions: performanceData.conversions || null,
      confidence: performanceData.confidence_score || null,
      ctr: performanceData.ctr || null,
      conversion_rate: performanceData.conversion_rate || null
    };
  } else {
    // fallback: strategy의 예상 성과 사용 (만약 성과 예측이 실패했을 때)
    performance_prediction = {
      reach: performancePred.estimated_reach || performancePred.reach || null,
      engagement: performancePred.estimated_engagement_rate || performancePred.engagement || null,
      conversions: performancePred.estimated_conversions || performancePred.conversions || null,
      confidence: performancePred.confidence_score || performancePred.confidence || null,
      ctr: null,
      conversion_rate: null
    };
  }

  console.log('=== ContentResult Parsed Values ===');
  console.log('RAW content:', content);
  console.log('copyData:', copyData);
  console.log('imageData:', imageData);
  console.log('copy_text:', copy_text);
  console.log('hashtags:', hashtags);
  console.log('image_url type:', typeof image_url);
  console.log('image_url length:', image_url?.length);
  console.log('image_url starts with data:', image_url?.startsWith('data:'));
  console.log('image_url preview (first 100 chars):', image_url?.substring(0, 100));
  console.log('---');
  console.log('content.target_age_group:', content.target_age_group);
  console.log('content.target_gender:', content.target_gender);
  console.log('content.target_ages:', content.target_ages);
  console.log('content.target_genders:', content.target_genders);
  console.log('content.target_interests:', content.target_interests);
  console.log('targetInsights:', targetInsights);
  console.log('targetInsights keys:', Object.keys(targetInsights));
  console.log('target_segment:', target_segment);
  console.log('---');
  console.log('selectedStrategyData:', selectedStrategyData);
  console.log('performancePred:', performancePred);
  console.log('performance_prediction:', performance_prediction);
  console.log('==================================='); // 디버깅용

  // 이미지 다운로드 핸들러
  const handleDownloadImage = () => {
    if (!image_url) return;

    const link = document.createElement('a');
    link.href = image_url;
    link.download = `contentcraft-image-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 카피 복사 핸들러
  const handleCopyCopy = async () => {
    if (!copy_text) return;

    try {
      const fullText = hashtags.length > 0
        ? `${copy_text}\n\n${hashtags.join(' ')}`
        : copy_text;
      await navigator.clipboard.writeText(fullText);
      alert('카피가 클립보드에 복사되었습니다!');
    } catch (err) {
      console.error('복사 실패:', err);
      alert('복사에 실패했습니다.');
    }
  };

  return (
    <div className="space-y-6">
      {/* 생성된 이미지 */}
      {image_url && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
            <h3 className="font-semibold text-gray-800">생성된 이미지</h3>
            <button
              onClick={handleDownloadImage}
              className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
            >
              다운로드
            </button>
          </div>
          <div className="p-4">
            <img
              src={image_url}
              alt="Generated content"
              className="w-full h-auto rounded-lg"
            />
          </div>
        </div>
      )}

      {/* 카피 텍스트 */}
      {copy_text && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
            <h3 className="font-semibold text-gray-800">마케팅 카피</h3>
            <button
              onClick={handleCopyCopy}
              className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
            >
              복사하기
            </button>
          </div>
          <div className="p-4 space-y-4">
            <p className="text-lg text-gray-800 leading-relaxed">{copy_text}</p>

            {hashtags && hashtags.length > 0 && (
              <div className="pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-600 mb-2">해시태그</p>
                <div className="flex flex-wrap gap-2">
                  {hashtags.map((tag, index) => (
                    <span key={index} className="px-3 py-1 bg-blue-50 text-blue-600 rounded-full text-sm font-medium">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {tone && (
              <div className="pt-2">
                <p className="text-sm text-gray-500">톤: {tone}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 타겟 세그먼트 */}
      {targetInsights && Object.keys(targetInsights).length > 0 && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
            <h3 className="font-semibold text-gray-800">타겟 세그먼트</h3>
          </div>
          <div className="p-4 space-y-3">
            {target_segment.ages.length > 0 && (
              <div>
                <p className="text-sm text-gray-600 mb-1">나이대</p>
                <div className="flex flex-wrap gap-2">
                  {target_segment.ages.map((age: string, index: number) => (
                    <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                      {age}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {target_segment.genders.length > 0 && (
              <div>
                <p className="text-sm text-gray-600 mb-1">성별</p>
                <div className="flex flex-wrap gap-2">
                  {target_segment.genders.map((gender: string, index: number) => (
                    <span key={index} className="px-3 py-1 bg-pink-100 text-pink-800 rounded-full text-sm">
                      {gender}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {target_segment.interests.length > 0 && (
              <div>
                <p className="text-sm text-gray-600 mb-1">관심사</p>
                <div className="flex flex-wrap gap-2">
                  {target_segment.interests.map((interest: string, index: number) => (
                    <span key={index} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                      {interest}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 성과 예측 */}
      {(performance_prediction.reach || performance_prediction.engagement || performance_prediction.conversions || performance_prediction.confidence || performance_prediction.ctr || performance_prediction.conversion_rate) && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-4 py-3 bg-gradient-to-r from-purple-50 to-blue-50 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-gray-800">AI 성과 예측</h3>
                <p className="text-xs text-gray-500 mt-1">
                  {performanceData
                    ? 'AI 시뮬레이션 기반 실제 성과 예측'
                    : '마케팅 전략에 따른 예상 성과'}
                </p>
              </div>
            </div>
          </div>
          <div className="p-4 space-y-4">
            {performance_prediction.reach && (
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <span className="text-sm font-medium text-gray-700">콘텐츠 노출 수</span>
                  </div>
                  <p className="text-xs text-gray-500 ml-6">이 콘텐츠를 볼 것으로 예상되는 사람 수</p>
                </div>
                <span className="text-lg font-bold text-blue-600 ml-4">
                  {typeof performance_prediction.reach === 'number'
                    ? performance_prediction.reach.toLocaleString() + '명'
                    : performance_prediction.reach}
                </span>
              </div>
            )}
            {performance_prediction.engagement && (
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                    </svg>
                    <span className="text-sm font-medium text-gray-700">사용자 반응률</span>
                  </div>
                  <p className="text-xs text-gray-500 ml-6">좋아요, 댓글, 공유 등 반응을 보일 비율</p>
                </div>
                <span className="text-lg font-bold text-green-600 ml-4">
                  {typeof performance_prediction.engagement === 'number'
                    ? `${performance_prediction.engagement.toFixed(1)}%`
                    : performance_prediction.engagement}
                </span>
              </div>
            )}
            {performance_prediction.ctr && (
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                    </svg>
                    <span className="text-sm font-medium text-gray-700">클릭률 (CTR)</span>
                  </div>
                  <p className="text-xs text-gray-500 ml-6">콘텐츠를 본 사람 중 클릭하는 비율</p>
                </div>
                <span className="text-lg font-bold text-indigo-600 ml-4">
                  {typeof performance_prediction.ctr === 'number'
                    ? `${performance_prediction.ctr.toFixed(2)}%`
                    : performance_prediction.ctr}
                </span>
              </div>
            )}
            {performance_prediction.conversions && (
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <svg className="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    <span className="text-sm font-medium text-gray-700">예상 구매/전환 수</span>
                  </div>
                  <p className="text-xs text-gray-500 ml-6">실제로 행동(구매, 클릭 등)을 취할 것으로 예상되는 수</p>
                </div>
                <span className="text-lg font-bold text-purple-600 ml-4">
                  {typeof performance_prediction.conversions === 'number'
                    ? performance_prediction.conversions.toLocaleString() + '명'
                    : performance_prediction.conversions}
                </span>
              </div>
            )}
            {performance_prediction.conversion_rate && (
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <svg className="w-4 h-4 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <span className="text-sm font-medium text-gray-700">전환율</span>
                  </div>
                  <p className="text-xs text-gray-500 ml-6">클릭한 사람 중 실제 구매/전환하는 비율</p>
                </div>
                <span className="text-lg font-bold text-pink-600 ml-4">
                  {typeof performance_prediction.conversion_rate === 'number'
                    ? `${performance_prediction.conversion_rate.toFixed(2)}%`
                    : performance_prediction.conversion_rate}
                </span>
              </div>
            )}
            {performance_prediction.confidence && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm font-medium text-gray-700">예측 신뢰도</span>
                  </div>
                  <span className="text-base font-semibold text-orange-600">
                    {typeof performance_prediction.confidence === 'number'
                      ? `${(performance_prediction.confidence * 100).toFixed(0)}%`
                      : performance_prediction.confidence}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">이 예측의 정확도에 대한 AI의 확신 정도</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
