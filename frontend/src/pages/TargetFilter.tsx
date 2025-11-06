import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { segmentationApi } from '../utils/api';

interface FilterState {
  age_groups: string[];
  genders: string[];
  interests: string[];
  income_levels: string[];
  category: string;
}

interface TargetProfile {
  id: number;
  age_group: string;
  gender: string;
  interests: string[];
  income_level: string;
  category: string;
  pain_points: string[];
  preferred_channels: string[];
  tone_preference: string;
}

interface Insights {
  pain_points: string[];
  preferred_channels: string[];
  tone_preferences: string[];
  message_strategies: string[];
}

const TargetFilter: React.FC = () => {
  const navigate = useNavigate();

  const [filters, setFilters] = useState<FilterState>({
    age_groups: [],
    genders: [],
    interests: [],
    income_levels: [],
    category: ''
  });

  const [profiles, setProfiles] = useState<TargetProfile[]>([]);
  const [insights, setInsights] = useState<Insights | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // 필터 옵션
  const ageOptions = ['10대', '20대', '30대', '40대', '50대', '60대 이상'];
  const genderOptions = ['남성', '여성', '무관'];
  const incomeOptions = ['저소득', '중소득', '중상소득', '고소득'];
  const categoryOptions = ['화장품', '식품', '패션', '전자제품', '서비스'];
  const interestOptions = [
    '뷰티', '자기관리', '건강', '운동', '여행', '맛집', '요리',
    '패션', '쇼핑', '독서', '영화', '음악', '게임', '반려동물',
    '재테크', '자기계발', '공부', '취미', '스포츠', '문화생활'
  ];

  const handleFilterChange = (key: keyof FilterState, value: string) => {
    if (key === 'category') {
      // 카테고리는 단일 선택
      setFilters(prev => ({ ...prev, category: value }));
    } else {
      // 나머지는 다중 선택
      setFilters(prev => {
        const current = prev[key] as string[];
        if (current.includes(value)) {
          return { ...prev, [key]: current.filter(v => v !== value) };
        } else {
          return { ...prev, [key]: [...current, value] };
        }
      });
    }
  };

  const handleSearch = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response: any = await segmentationApi.filterTargets(filters);
      setProfiles(response.data.profiles || []);
      setInsights(response.data.insights || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : '검색에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setFilters({
      age_groups: [],
      genders: [],
      interests: [],
      income_levels: [],
      category: ''
    });
    setProfiles([]);
    setInsights(null);
  };

  const handleUseForContent = () => {
    if (profiles.length === 0) {
      alert('먼저 타겟을 선택해주세요');
      return;
    }

    // 나이대 형식 변환: "20대" -> "20-29"
    const ageMapping: Record<string, string> = {
      '10대': '10-19',
      '20대': '20-29',
      '30대': '30-39',
      '40대': '40-49',
      '50대': '50-59',
      '60대 이상': '60+'
    };

    // 카테고리 형식 변환: "화장품" -> "beauty"
    const categoryMapping: Record<string, string> = {
      '화장품': 'beauty',
      '식품': 'food',
      '패션': 'fashion',
      '전자제품': 'electronics',
      '서비스': 'service'
    };

    // 선택된 모든 값들을 콘텐츠 생성 페이지로 전달
    const selectedAges = filters.age_groups.length > 0
      ? filters.age_groups.map(age => ageMapping[age] || age)
      : [ageMapping[profiles[0]?.age_group] || '20-29'];
    const selectedGenders = filters.genders.length > 0 ? filters.genders : [profiles[0]?.gender || '여성'];

    // 카테고리 전달 (단일 선택)
    const selectedCategory = filters.category
      ? categoryMapping[filters.category] || 'beauty'
      : 'beauty';

    // 관심사: 사용자 선택 + 프로필에서 추출 (중복 제거, 최대 5개)
    const userSelectedInterests = filters.interests;
    const profileInterests = [...new Set(profiles.flatMap(p => p.interests))];

    // 사용자 선택 관심사 우선, 그 다음 프로필 관심사 추가
    const combinedInterests = [
      ...userSelectedInterests,
      ...profileInterests.filter(i => !userSelectedInterests.includes(i))
    ].slice(0, 5); // 최대 5개로 제한

    const selectedInterests = combinedInterests.length > 0
      ? combinedInterests
      : profileInterests.slice(0, 3); // 프로필도 없으면 기본값

    // 쿼리 파라미터로 전달 (배열은 쉼표로 구분, 카테고리는 단일)
    const params = new URLSearchParams({
      ages: selectedAges.join(','),
      genders: selectedGenders.join(','),
      category: selectedCategory,
      interests: selectedInterests.join(',')
    });

    navigate(`/?${params.toString()}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">타겟 세분화</h1>
          <p className="mt-2 text-gray-600">
            필터를 선택하여 타겟 고객을 찾고 인사이트를 확인하세요
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Filters Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">필터</h2>

              {/* Age */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">나이대</h3>
                <div className="flex flex-wrap gap-2">
                  {ageOptions.map(age => (
                    <button
                      key={age}
                      onClick={() => handleFilterChange('age_groups', age)}
                      className={`px-3 py-1 rounded-full text-sm transition ${
                        filters.age_groups.includes(age)
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {age}
                    </button>
                  ))}
                </div>
              </div>

              {/* Gender */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">성별</h3>
                <div className="flex flex-wrap gap-2">
                  {genderOptions.map(gender => (
                    <button
                      key={gender}
                      onClick={() => handleFilterChange('genders', gender)}
                      className={`px-3 py-1 rounded-full text-sm transition ${
                        filters.genders.includes(gender)
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {gender}
                    </button>
                  ))}
                </div>
              </div>

              {/* Income */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">소득 수준</h3>
                <div className="flex flex-wrap gap-2">
                  {incomeOptions.map(income => (
                    <button
                      key={income}
                      onClick={() => handleFilterChange('income_levels', income)}
                      className={`px-3 py-1 rounded-full text-sm transition ${
                        filters.income_levels.includes(income)
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {income}
                    </button>
                  ))}
                </div>
              </div>

              {/* Category (단일 선택) */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">제품 카테고리 (단일 선택)</h3>
                <div className="flex flex-wrap gap-2">
                  {categoryOptions.map(category => (
                    <button
                      key={category}
                      onClick={() => handleFilterChange('category', category)}
                      className={`px-3 py-1 rounded-full text-sm transition ${
                        filters.category === category
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              </div>

              {/* Interests */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">관심사 (선택하면 해당 관심사가 콘텐츠 생성에 사용됩니다)</h3>
                <div className="flex flex-wrap gap-2">
                  {interestOptions.map(interest => (
                    <button
                      key={interest}
                      onClick={() => handleFilterChange('interests', interest)}
                      className={`px-3 py-1 rounded-full text-sm transition ${
                        filters.interests.includes(interest)
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {interest}
                    </button>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2">
                <button
                  onClick={handleSearch}
                  disabled={isLoading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition disabled:bg-gray-400"
                >
                  {isLoading ? '검색 중...' : '타겟 검색'}
                </button>
                <button
                  onClick={handleReset}
                  className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-3 rounded-lg transition"
                >
                  초기화
                </button>
              </div>
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2">
            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4">
                {error}
              </div>
            )}

            {/* Results Summary */}
            {profiles.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">
                      검색 결과: <span className="text-blue-600">{profiles.length}명</span>
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">
                      필터 조건에 맞는 타겟 프로필입니다
                    </p>
                  </div>
                  <button
                    onClick={handleUseForContent}
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition"
                  >
                    이 타겟으로 콘텐츠 생성
                  </button>
                </div>

                {/* Insights */}
                {insights && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
                    {/* Pain Points */}
                    {insights.pain_points && insights.pain_points.length > 0 && (
                      <div>
                        <h3 className="text-sm font-semibold text-gray-700 mb-2">주요 고충</h3>
                        <ul className="space-y-1">
                          {insights.pain_points.slice(0, 5).map((point, idx) => (
                            <li key={idx} className="text-sm text-gray-600">• {point}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Preferred Channels */}
                    {insights.preferred_channels && insights.preferred_channels.length > 0 && (
                      <div>
                        <h3 className="text-sm font-semibold text-gray-700 mb-2">선호 채널</h3>
                        <div className="flex flex-wrap gap-1">
                          {insights.preferred_channels.slice(0, 5).map((channel, idx) => (
                            <span key={idx} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                              {channel}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Tone Preferences */}
                    {insights.tone_preferences && insights.tone_preferences.length > 0 && (
                      <div>
                        <h3 className="text-sm font-semibold text-gray-700 mb-2">선호 톤</h3>
                        <div className="flex flex-wrap gap-1">
                          {insights.tone_preferences.slice(0, 3).map((tone, idx) => (
                            <span key={idx} className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                              {tone}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Message Strategies */}
                    {insights.message_strategies && insights.message_strategies.length > 0 && (
                      <div>
                        <h3 className="text-sm font-semibold text-gray-700 mb-2">메시지 전략</h3>
                        <ul className="space-y-1">
                          {insights.message_strategies.slice(0, 3).map((strategy, idx) => (
                            <li key={idx} className="text-sm text-gray-600">• {strategy}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Empty State */}
            {!isLoading && profiles.length === 0 && !error && (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <h3 className="mt-4 text-lg font-medium text-gray-900">타겟을 검색하세요</h3>
                <p className="mt-2 text-gray-500">
                  왼쪽 필터를 선택하고 '타겟 검색' 버튼을 클릭하세요
                </p>
              </div>
            )}

            {/* Loading */}
            {isLoading && (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <p className="mt-4 text-gray-600">검색 중...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TargetFilter;
