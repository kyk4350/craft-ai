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

// 성과 지표 타입
export interface PerformanceMetrics {
  impressions: number;
  clicks: number;
  ctr: number;
  engagement_rate: number;
  conversion_rate: number;
  brand_recall_score: number;
}

// 성과 예측 응답
export interface PerformanceResponse {
  success: boolean;
  message?: string;
  data: {
    exists: boolean;
    data_source?: string;
    metrics?: PerformanceMetrics;
    confidence_score?: number;
    is_ai_prediction?: boolean;
  };
  is_new_prediction?: boolean;
}

// 통합 콘텐츠 생성 요청
export interface FullContentGenerationRequest {
  product_name: string;
  product_description: string;
  category: string;
  target_ages: string[];
  target_genders: string[];
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
  category?: string;
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
    // Zustand 스토어에서 토큰 가져오기
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      try {
        const { state } = JSON.parse(authStorage);
        const token = state?.token;
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (e) {
        console.error('Failed to parse auth storage:', e);
      }
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

// 타겟 세분화 API 제거됨 - AI 실시간 분석으로 대체

export const performanceApi = {
  /**
   * 콘텐츠 성과 예측
   */
  predictPerformance: async (contentId: number): Promise<PerformanceResponse> => {
    return apiClient.post(`/api/performance/predict/${contentId}`);
  },

  /**
   * 성과 데이터 조회
   */
  getPerformance: async (contentId: number): Promise<PerformanceResponse> => {
    return apiClient.get(`/api/performance/${contentId}`);
  },
};

export const analyticsApi = {
  /**
   * 대시보드 핵심 지표 요약
   */
  getSummary: async (): Promise<unknown> => {
    return apiClient.get('/api/analytics/summary');
  },

  /**
   * 전략별 평균 성과
   */
  getPerformanceByStrategy: async (): Promise<unknown> => {
    return apiClient.get('/api/analytics/by-strategy');
  },

  /**
   * 타겟별 평균 성과
   */
  getPerformanceByTarget: async (): Promise<unknown> => {
    return apiClient.get('/api/analytics/by-target');
  },

  /**
   * 최고 성과 콘텐츠 목록
   */
  getTopContents: async (limit: number = 5): Promise<unknown> => {
    return apiClient.get(`/api/analytics/top-contents?limit=${limit}`);
  },
};

// Auth API 타입 정의
export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface LoginRequest {
  username: string; // FastAPI OAuth2PasswordRequestForm uses 'username'
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    name: string;
    created_at: string;
  };
}

export interface RegisterResponse {
  success: boolean;
  message: string;
  user: {
    id: number;
    email: string;
    name: string;
    created_at: string;
  };
}

export const authApi = {
  /**
   * 회원가입
   */
  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    return apiClient.post('/api/auth/register', data);
  },

  /**
   * 로그인
   */
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    // OAuth2PasswordRequestForm 형식으로 전송 (form data)
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);

    return axios.post(`${API_BASE_URL}/api/auth/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }).then(res => res.data);
  },

  /**
   * Google 로그인
   */
  googleLogin: async (token: string): Promise<AuthResponse> => {
    return apiClient.post('/api/auth/google', { token });
  },
};

// Contents API 타입 정의
export interface ContentItem {
  id: number;
  project_id: number | null;
  product_name: string;
  category: string;
  target_age_group: string;
  target_gender: string;
  target_interests: string[];
  strategy: Record<string, unknown>;
  copy_text: string;
  copy_tone: string;
  hashtags: string[];
  image_url: string;
  image_provider?: string;
  status: string;
  created_at: string;
  generation_time?: number;
  performance?: {
    ctr: number;
    engagement_rate: number;
    conversion_rate: number;
    brand_recall_score: number;
    is_prediction: boolean;
  };
}

export interface ContentsListResponse {
  success: boolean;
  data: {
    contents: ContentItem[];
    total: number;
    page: number;
    limit: number;
  };
  message: string;
}

export const contentsApi = {
  /**
   * 콘텐츠 목록 조회
   */
  getContents: async (params?: {
    project_id?: number;
    limit?: number;
    offset?: number;
  }): Promise<ContentsListResponse> => {
    const queryParams = new URLSearchParams();
    if (params?.project_id) queryParams.append('project_id', params.project_id.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const queryString = queryParams.toString();
    return apiClient.get(`/api/contents${queryString ? '?' + queryString : ''}`);
  },

  /**
   * 콘텐츠 상세 조회
   */
  getContent: async (contentId: number): Promise<{ success: boolean; data: ContentItem; message: string }> => {
    return apiClient.get(`/api/contents/${contentId}`);
  },

  /**
   * 콘텐츠 삭제
   */
  deleteContent: async (contentId: number): Promise<{ success: boolean; message: string }> => {
    return apiClient.delete(`/api/contents/${contentId}`);
  },
};

export default apiClient;
