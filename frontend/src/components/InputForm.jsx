import { useState } from 'react';

const CATEGORIES = [
  { value: 'beauty', label: '화장품/뷰티' },
  { value: 'food', label: '식품' },
  { value: 'fashion', label: '패션' },
  { value: 'electronics', label: '전자제품' },
  { value: 'service', label: '서비스' },
];

const AGE_GROUPS = [
  { value: '10-19', label: '10대' },
  { value: '20-29', label: '20대' },
  { value: '30-39', label: '30대' },
  { value: '40-49', label: '40대' },
  { value: '50-59', label: '50대' },
  { value: '60+', label: '60대 이상' },
];

const GENDERS = [
  { value: '남성', label: '남성' },
  { value: '여성', label: '여성' },
  { value: '무관', label: '무관' },
];

const TONES = [
  { value: 'professional', label: '프로페셔널 (40-50자)' },
  { value: 'casual', label: '캐주얼 (30-40자)' },
  { value: 'impact', label: '임팩트 (15-25자)' },
];

const COMMON_INTERESTS = [
  '뷰티', '자기관리', '건강', '운동', '여행', '맛집', '요리',
  '패션', '쇼핑', '독서', '영화', '음악', '게임', '반려동물',
  '재테크', '자기계발', '공부', '취미', '스포츠', '문화생활'
];

export default function InputForm({ onSubmit, isLoading }) {
  const [formData, setFormData] = useState({
    product_name: '',
    product_description: '',
    category: 'beauty',
    target_age: '20-29',
    target_gender: '여성',
    target_interests: [],
    copy_tone: 'professional',
  });

  const [customInterest, setCustomInterest] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleInterestToggle = (interest) => {
    setFormData(prev => ({
      ...prev,
      target_interests: prev.target_interests.includes(interest)
        ? prev.target_interests.filter(i => i !== interest)
        : [...prev.target_interests, interest]
    }));
  };

  const handleAddCustomInterest = () => {
    if (customInterest.trim() && !formData.target_interests.includes(customInterest.trim())) {
      setFormData(prev => ({
        ...prev,
        target_interests: [...prev.target_interests, customInterest.trim()]
      }));
      setCustomInterest('');
    }
  };

  const handleRemoveInterest = (interest) => {
    setFormData(prev => ({
      ...prev,
      target_interests: prev.target_interests.filter(i => i !== interest)
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // 유효성 검사
    if (!formData.product_name.trim()) {
      alert('제품명을 입력해주세요.');
      return;
    }
    if (!formData.product_description.trim()) {
      alert('제품 설명을 입력해주세요.');
      return;
    }
    if (formData.target_interests.length === 0) {
      alert('타겟 관심사를 최소 1개 이상 선택해주세요.');
      return;
    }

    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">콘텐츠 생성 정보 입력</h2>

      {/* 제품 정보 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-700">제품 정보</h3>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            제품명 *
          </label>
          <input
            type="text"
            name="product_name"
            value={formData.product_name}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="예: 프리미엄 핸드크림"
            disabled={isLoading}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            제품 설명 *
          </label>
          <textarea
            name="product_description"
            value={formData.product_description}
            onChange={handleChange}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="예: 자연 유래 성분으로 만든 고보습 핸드크림"
            disabled={isLoading}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            카테고리 *
          </label>
          <select
            name="category"
            value={formData.category}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          >
            {CATEGORIES.map(cat => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* 타겟 정보 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-700">타겟 고객 정보</h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              나이대 *
            </label>
            <select
              name="target_age"
              value={formData.target_age}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            >
              {AGE_GROUPS.map(age => (
                <option key={age.value} value={age.value}>{age.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              성별 *
            </label>
            <select
              name="target_gender"
              value={formData.target_gender}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            >
              {GENDERS.map(gender => (
                <option key={gender.value} value={gender.value}>{gender.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            관심사 * (최소 1개)
          </label>

          {/* 선택된 관심사 */}
          {formData.target_interests.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {formData.target_interests.map(interest => (
                <span
                  key={interest}
                  className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {interest}
                  <button
                    type="button"
                    onClick={() => handleRemoveInterest(interest)}
                    className="ml-2 text-blue-600 hover:text-blue-800"
                    disabled={isLoading}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}

          {/* 일반 관심사 선택 */}
          <div className="flex flex-wrap gap-2 mb-3">
            {COMMON_INTERESTS.map(interest => (
              <button
                key={interest}
                type="button"
                onClick={() => handleInterestToggle(interest)}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${
                  formData.target_interests.includes(interest)
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
                disabled={isLoading}
              >
                {interest}
              </button>
            ))}
          </div>

          {/* 커스텀 관심사 추가 */}
          <div className="flex gap-2">
            <input
              type="text"
              value={customInterest}
              onChange={(e) => setCustomInterest(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomInterest())}
              placeholder="직접 입력..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={handleAddCustomInterest}
              className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
              disabled={isLoading}
            >
              추가
            </button>
          </div>
        </div>
      </div>

      {/* 카피 톤 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          카피 톤 *
        </label>
        <div className="grid grid-cols-3 gap-3">
          {TONES.map(tone => (
            <label
              key={tone.value}
              className={`flex items-center justify-center px-4 py-3 border-2 rounded-lg cursor-pointer transition-colors ${
                formData.copy_tone === tone.value
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <input
                type="radio"
                name="copy_tone"
                value={tone.value}
                checked={formData.copy_tone === tone.value}
                onChange={handleChange}
                className="sr-only"
                disabled={isLoading}
              />
              <span className="text-sm text-center">{tone.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* 제출 버튼 */}
      <button
        type="submit"
        disabled={isLoading}
        className={`w-full py-3 px-4 rounded-md font-semibold text-white transition-colors ${
          isLoading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700'
        }`}
      >
        {isLoading ? '생성 중...' : '콘텐츠 생성하기'}
      </button>
    </form>
  );
}
