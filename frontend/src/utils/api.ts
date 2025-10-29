import axios, { AxiosInstance, AxiosError } from 'axios';

// API 기본 URL 설정
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// === 타입 정의 ===

// 전략 타입
export interface Strategy {
  id: number;
  name: string;
  core_message: string;
  emotion: string;
  expected_effect: string;
}

// 카피 타입
export interface Copy {
  text: string;
  tone: string;
  hashtags?: string[];
  length?: number;
}

// 이미지 타입
export interface ImageData {
  prompt: string;
  original_url: string;
  local_url?: string;
  file_path?: string;
}

// 통합 콘텐츠 생성 요청
export interface FullContentGenerationRequest {
  product_name: string;
  product_description: string;
  category: string;
  target_age: string;
  target_gender: string;
  target_interests: string[];
  copy_tone: string;
  target_income_level?: string;
  strategy_id?: number;
  project_id?: number;
  save_to_db?: boolean;
}

// 통합 콘텐츠 생성 응답
export interface FullContentGenerationResponse {
  success: boolean;
  data: {
    content_id: number | null;
    strategies: Strategy[];
    selected_strategy_id: number;
    selected_strategy: Strategy;
    copy: Copy;
    image: ImageData;
  };
  message: string;
  generation_time: number;
}

// 세그먼트 필터 요청
export interface SegmentFilterRequest {
  age_groups?: string[];
  genders?: string[];
  interests?: string[];
  income_levels?: string[];
  categories?: string[];
}

// === Axios 인스턴스 생성 ===
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 120초 (이미지 생성 대기 시간 포함)
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
apiClient.interceptors.request.use(
  (config) => {
    // 토큰이 있으면 헤더에 추가 (향후 인증 기능 추가 시)
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error: AxiosError) => {
    // 에러 처리
    if (error.response) {
      // 서버 응답 에러
      const errorData = error.response.data as { detail?: string; message?: string };
      const errorMessage = errorData?.detail || errorData?.message || '서버 오류가 발생했습니다.';
      console.error('API Error:', errorMessage);
      return Promise.reject(new Error(errorMessage));
    } else if (error.request) {
      // 요청은 전송되었으나 응답이 없음
      console.error('Network Error:', error.message);
      return Promise.reject(new Error('네트워크 오류가 발생했습니다.'));
    } else {
      // 기타 에러
      console.error('Error:', error.message);
      return Promise.reject(error);
    }
  }
);

// === API 함수들 ===
export const contentApi = {
  /**
   * 통합 콘텐츠 생성 (전략 + 카피 + 이미지)
   */
  generateFullContent: async (
    data: FullContentGenerationRequest
  ): Promise<FullContentGenerationResponse> => {
    return apiClient.post('/api/content/generate', data);
  },

  /**
   * 마케팅 전략 생성
   */
  generateStrategy: async (data: unknown): Promise<unknown> => {
    return apiClient.post('/api/content/strategy', data);
  },

  /**
   * 카피 생성
   */
  generateCopy: async (data: unknown): Promise<unknown> => {
    return apiClient.post('/api/content/copy', data);
  },

  /**
   * 이미지 프롬프트 변환
   */
  generateImagePrompt: async (data: unknown): Promise<unknown> => {
    return apiClient.post('/api/content/image-prompt', data);
  },

  /**
   * 이미지 생성
   */
  generateImage: async (data: unknown): Promise<unknown> => {
    return apiClient.post('/api/content/image', data);
  },
};

export const segmentationApi = {
  /**
   * 타겟 필터링
   */
  filterTargets: async (data: SegmentFilterRequest): Promise<unknown> => {
    return apiClient.post('/api/segmentation/filter', data);
  },

  /**
   * 타겟 검색
   */
  searchTargets: async (data: { keyword: string }): Promise<unknown> => {
    return apiClient.post('/api/segmentation/search', data);
  },

  /**
   * 전체 요약
   */
  getSummary: async (): Promise<unknown> => {
    return apiClient.get('/api/segmentation/summary');
  },

  /**
   * 인사이트 조회
   */
  getInsights: async (params: Record<string, string>): Promise<unknown> => {
    return apiClient.get('/api/segmentation/insights', { params });
  },
};

export default apiClient;
