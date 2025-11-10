import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuthStore } from '../stores/authStore';
import { fetchSSE, SSEMessage } from '../utils/sse';

interface Message {
  role: 'assistant' | 'user';
  content: string;
  options?: string[];
  imageUrl?: string; // 업로드된 이미지 미리보기 URL
  imageName?: string; // 이미지 파일명
}

interface ConversationalChatbotProps {
  onContentGenerated: (content: any) => void;
  onGenerationStart: () => void;
  onProgress?: (step: number, total: number, message: string) => void;
  currentContent?: any; // 현재 생성된 콘텐츠 (수정 요청 시 사용)
}

interface CollectedInfo {
  product_name?: string;
  product_description?: string;
  category?: string;
  target_ages?: string[];
  target_genders?: string[];
  target_interests?: string[];
  copy_tone?: string;
  product_image_path?: string; // 업로드된 제품 이미지 경로
}

export default function ConversationalChatbot({
  onContentGenerated,
  onGenerationStart,
  onProgress,
  currentContent
}: ConversationalChatbotProps) {
  const { token } = useAuthStore();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: '안녕하세요! 어떤 제품이나 서비스의 마케팅 콘텐츠를 만들어드릴까요?\n\n아래에서 카테고리를 선택하거나 직접 입력해주세요.',
      options: ['뷰티/화장품', '패션/의류', '식품/음료', '건강/헬스', 'IT/전자제품', '라이프스타일', '직접 입력']
    }
  ]);
  const [userInput, setUserInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [collectedInfo, setCollectedInfo] = useState<CollectedInfo>({});
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [uploadedImageFile, setUploadedImageFile] = useState<File | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const conversationFlow = [
    {
      key: 'product_info',
      question: '어떤 제품이나 서비스의 마케팅 콘텐츠를 만들어드릴까요?\n\n아래에서 카테고리를 선택하거나 직접 입력해주세요.',
      options: ['뷰티/화장품', '패션/의류', '식품/음료', '건강/헬스', 'IT/전자제품', '라이프스타일', '직접 입력']
    },
    {
      key: 'product_detail',
      question: '제품명과 간단한 설명을 알려주세요.\n\n예: "프리미엄 핸드크림 - 자연 유래 성분으로 만든 고보습 핸드크림"'
    },
    {
      key: 'target_age',
      question: '타겟 연령대를 선택해주세요. (여러 개 선택 가능)',
      options: ['10대', '20대', '30대', '40대', '50대 이상', 'AI가 자동 분석'],
      multiple: true
    },
    {
      key: 'target_gender',
      question: '타겟 성별을 선택해주세요. (여러 개 선택 가능)',
      options: ['여성', '남성', '무관'],
      multiple: true
    },
    {
      key: 'target_interest',
      question: '타겟의 관심사를 선택해주세요. (여러 개 선택 가능)',
      options: ['뷰티', '패션', '건강', '운동', '자기관리', '트렌드', '품질', '가성비', 'AI가 자동 분석'],
      multiple: true
    },
    {
      key: 'copy_tone',
      question: '원하시는 카피 스타일을 선택해주세요.',
      options: ['프로페셔널', '캐주얼', '임팩트', 'AI가 자동 선택']
    }
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleOptionClick = (option: string) => {
    const step = conversationFlow[currentStep];

    if (step.multiple) {
      const currentValues = (collectedInfo[step.key as keyof CollectedInfo] as string[]) || [];
      const newValues = currentValues.includes(option)
        ? currentValues.filter(v => v !== option)
        : [...currentValues, option];

      setCollectedInfo({ ...collectedInfo, [step.key]: newValues });
    } else {
      handleUserMessage(option);
    }
  };

  const handleMultipleSelectionConfirm = () => {
    const step = conversationFlow[currentStep];
    const selectedValues = collectedInfo[step.key as keyof CollectedInfo] as string[];

    if (!selectedValues || selectedValues.length === 0) {
      alert('최소 1개 이상 선택해주세요.');
      return;
    }

    const userMessage = selectedValues.join(', ');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    // 타겟 연령대, 성별, 관심사 매핑
    let updatedInfo = { ...collectedInfo };

    if (step.key === 'target_age') {
      const ageMap: { [key: string]: string } = {
        '10대': '10-19',
        '20대': '20-29',
        '30대': '30-39',
        '40대': '40-49',
        '50대 이상': '50+'
      };

      if (selectedValues.includes('AI가 자동 분석')) {
        updatedInfo.target_ages = []; // 빈 배열로 AI가 판단하게
      } else {
        const mappedAges = selectedValues.map(age => ageMap[age] || age);
        updatedInfo.target_ages = mappedAges;
      }
      // target_age 중간 키 제거
      delete (updatedInfo as any).target_age;

    } else if (step.key === 'target_gender') {
      // 성별 처리: '무관' 선택 시 ['여성', '남성'] 전송
      if (selectedValues.includes('무관')) {
        updatedInfo.target_genders = ['여성', '남성'];
      } else {
        updatedInfo.target_genders = selectedValues;
      }
      // target_gender 중간 키 제거
      delete (updatedInfo as any).target_gender;

    } else if (step.key === 'target_interest') {
      if (selectedValues.includes('AI가 자동 분석')) {
        updatedInfo.target_interests = []; // 빈 배열로 AI가 판단하게
      } else {
        updatedInfo.target_interests = selectedValues;
      }
      // target_interest 중간 키 제거
      delete (updatedInfo as any).target_interest;
    }

    setCollectedInfo(updatedInfo);
    proceedToNextStep();
  };

  // 이미지 업로드 핸들러
  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // 파일 크기 체크 (10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('파일 크기는 10MB 이하여야 합니다.');
      return;
    }

    // 파일 형식 체크
    if (!['image/jpeg', 'image/jpg', 'image/png', 'image/webp'].includes(file.type)) {
      alert('JPG, PNG, WEBP 형식의 이미지만 업로드 가능합니다.');
      return;
    }

    setUploadedImageFile(file);
    setImagePreviewUrl(URL.createObjectURL(file));

    // 업로드 메시지만 표시하고 대화는 계속 진행 (제품명/설명 입력 대기)
    // 메시지는 추가하지 않음 - 사용자가 계속 입력할 수 있도록
  };

  // 이미지 제거 핸들러
  const handleRemoveImage = () => {
    setUploadedImageFile(null);
    setImagePreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUserMessage = async (message: string) => {
    if (!message.trim()) return;

    // 생성 완료 후 수정 요청 감지
    if (currentStep >= conversationFlow.length && currentContent) {
      handleModificationRequest(message);
      return;
    }

    const step = conversationFlow[currentStep];

    // product_detail 단계에서 이미지가 있으면 메시지에 포함
    const newMessage: Message = {
      role: 'user' as const,
      content: message
    };

    if (step.key === 'product_detail' && imagePreviewUrl && uploadedImageFile) {
      newMessage.imageUrl = imagePreviewUrl;
      newMessage.imageName = uploadedImageFile.name;
    }

    const newMessages: Message[] = [...messages, newMessage];
    setMessages(newMessages);
    setUserInput('');

    let updatedInfo = { ...collectedInfo };

    if (step.key === 'product_info') {
      // 카테고리 매핑
      const categoryMap: { [key: string]: string } = {
        '뷰티/화장품': 'beauty',
        '패션/의류': 'fashion',
        '식품/음료': 'food',
        '건강/헬스': 'health',
        'IT/전자제품': 'tech',
        '라이프스타일': 'lifestyle'
      };

      if (message === '직접 입력') {
        // 직접 입력일 경우 다음 단계로
        updatedInfo.category = 'other';
      } else {
        updatedInfo.category = categoryMap[message] || message.toLowerCase();
      }
      setCollectedInfo(updatedInfo);
    } else if (step.key === 'product_detail') {
      // 제품 상세 정보 파싱
      const parts = message.split('-');
      const productName = parts[0]?.trim() || message.split(' ')[0] || message;
      const productDesc = parts[1]?.trim() || message;

      updatedInfo = {
        ...updatedInfo,
        product_name: productName,
        product_description: productDesc
      };
      setCollectedInfo(updatedInfo);
    } else if (step.key === 'copy_tone') {
      // 톤 매핑
      const toneMap: { [key: string]: string } = {
        '프로페셔널': 'professional',
        '캐주얼': 'casual',
        '임팩트': 'impact',
        'AI가 자동 선택': 'auto'
      };
      updatedInfo.copy_tone = toneMap[message] || 'professional';
      setCollectedInfo(updatedInfo);

      // 마지막 스텝이므로 바로 생성 (상태 업데이트를 기다리지 않고 updatedInfo 사용)
      proceedToNextStep(updatedInfo);
      return;
    }

    proceedToNextStep();
  };

  const proceedToNextStep = (infoToUse?: CollectedInfo) => {
    const nextStep = currentStep + 1;

    if (nextStep < conversationFlow.length) {
      const nextQuestion = conversationFlow[nextStep];
      setCurrentStep(nextStep);

      setTimeout(() => {
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: nextQuestion.question,
            options: nextQuestion.options
          }
        ]);
      }, 500);
    } else {
      // 마지막 스텝: 콘텐츠 생성
      generateContent(infoToUse);
    }
  };

  const handleModificationRequest = async (message: string) => {
    console.log('🔥 handleModificationRequest 호출됨:', message);

    // 입력창 초기화
    setUserInput('');
    setIsLoading(true);

    try {
      if (message === '새 콘텐츠 생성') {
        // 페이지 새로고침으로 완전히 새로 시작
        window.location.reload();
        return;

      } else if (message === '전체 다시 생성') {
        // 전체 재생성
        setMessages(prev => [
          ...prev,
          { role: 'user', content: message },
          {
            role: 'assistant',
            content: '알겠습니다! 카피와 이미지를 포함한 전체 콘텐츠를 새롭게 생성하겠습니다. 잠시만 기다려주세요! ✨'
          }
        ]);

        // 기존 정보로 다시 생성
        await regenerateContent('all');

      } else if (message === '이미지만 다시 생성') {
        // 이미지만 재생성
        setMessages(prev => [
          ...prev,
          { role: 'user', content: message },
          {
            role: 'assistant',
            content: '네! 카피는 그대로 유지하고 이미지만 새롭게 생성하겠습니다. 🎨'
          }
        ]);

        await regenerateContent('image');

      } else if (message === '카피만 다시 생성') {
        // 카피만 재생성
        setMessages(prev => [
          ...prev,
          { role: 'user', content: message },
          {
            role: 'assistant',
            content: '알겠습니다! 이미지는 그대로 두고 카피 문구만 새롭게 작성하겠습니다. ✍️'
          }
        ]);

        await regenerateContent('copy');

      } else if (message === '카피 톤 변경') {
        // 톤 변경 옵션 보여주기
        setMessages(prev => [
          ...prev,
          { role: 'user', content: message },
          {
            role: 'assistant',
            content: '어떤 톤으로 카피를 변경하시겠어요? 원하시는 스타일을 선택해주세요!',
            options: ['프로페셔널', '캐주얼', '임팩트']
          }
        ]);
        setIsLoading(false);
        return;

      } else if (message === '직접 입력') {
        // 직접 입력 - 입력창 포커스
        setIsLoading(false);
        // 입력창에 포커스
        setTimeout(() => {
          inputRef.current?.focus();
        }, 100);
        return;

      } else if (['프로페셔널', '캐주얼', '임팩트'].includes(message)) {
        // 톤 변경
        const toneMap: { [key: string]: string } = {
          '프로페셔널': 'professional',
          '캐주얼': 'casual',
          '임팩트': 'impact'
        };

        const toneDescription: { [key: string]: string } = {
          '프로페셔널': '격식있고 전문적인',
          '캐주얼': '친근하고 편안한',
          '임팩트': '짧고 강렬한'
        };

        setMessages(prev => [
          ...prev,
          { role: 'user', content: message },
          {
            role: 'assistant',
            content: `좋습니다! ${toneDescription[message]} 톤으로 카피를 다시 작성하겠습니다. 📝`
          }
        ]);

        await regenerateContent('copy', { tone: toneMap[message] });

      } else {
        // 자유 입력 처리 - 의도 파악 후 적절한 재생성
        setMessages(prev => [
          ...prev,
          { role: 'user', content: message }
        ]);

        // 간단한 키워드 기반 의도 파악
        const lowerMessage = message.toLowerCase();
        let regenerateType = 'all';
        let responseMessage = '알겠습니다! 요청하신 내용대로 수정하겠습니다. 잠시만 기다려주세요!';

        // 이미지 관련 키워드 체크
        const imageKeywords = ['이미지', '사진', '그림', '비주얼', '디자인', '색상', '배경', '튜브형', '병', '용기', '패키지', '옷', '상의', '하의', '의상', '스타일', '모델', '사람', '포즈', '장소', '분위기', '조명', '느낌'];
        const copyKeywords = ['카피', '문구', '텍스트', '글', '메시지', '헤드라인', '슬로건'];

        const hasImageKeyword = imageKeywords.some(keyword => lowerMessage.includes(keyword));
        const hasCopyKeyword = copyKeywords.some(keyword => lowerMessage.includes(keyword));

        if (hasImageKeyword && !hasCopyKeyword) {
          // 이미지만 수정 요청
          regenerateType = 'image';
          responseMessage = '네! 이미지를 수정하겠습니다. 잠시만 기다려주세요! 🎨';
        } else if (hasCopyKeyword && !hasImageKeyword) {
          // 카피만 수정 요청
          regenerateType = 'copy';
          responseMessage = '네! 카피 문구를 수정하겠습니다. 잠시만 기다려주세요! ✍️';
        } else {
          // 전체 또는 애매한 경우 - 전체 재생성
          regenerateType = 'all';
          responseMessage = '알겠습니다! 요청하신 내용을 반영하여 콘텐츠를 다시 생성하겠습니다. 잠시만 기다려주세요! 💪';
        }

        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: responseMessage
          }
        ]);

        // 의도에 따라 재생성
        await regenerateContent(regenerateType, { request: message, customPrompt: message });
      }
    } catch (error) {
      console.error('수정 요청 처리 중 오류:', error);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: '죄송합니다. 요청 처리 중 오류가 발생했습니다.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const regenerateContent = async (type: string, params?: any) => {
    // 로딩 시작 알림 (오른쪽 패널에 표시)
    onGenerationStart();

    try {
      let response;

      if (type === 'image') {
        // 이미지만 재생성
        const requestData = {
          ...currentContent,  // 기존 데이터 전부 전달
          product_image_path: collectedInfo.product_image_path || undefined, // 제품 이미지 경로 포함
          copy_text: currentContent.copy.text,
          image_prompt: currentContent.image?.prompt,
          customPrompt: params?.customPrompt  // 커스텀 요청 전달
        };

        console.log('🔍 이미지 재생성 요청 데이터:', {
          customPrompt: requestData.customPrompt,
          copy_text: requestData.copy_text,
          product_image_path: requestData.product_image_path
        });

        response = await axios.post('http://localhost:8000/api/content/regenerate/image', requestData, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

      } else if (type === 'copy') {
        // 카피만 재생성
        const requestData = {
          ...currentContent,  // 기존 데이터 전부 전달
          product_name: collectedInfo.product_name || currentContent.product_name,
          product_description: collectedInfo.product_description || currentContent.product_description,
          category: collectedInfo.category || currentContent.category,
          target_ages: currentContent.target_ages || collectedInfo.target_ages || [],
          target_genders: currentContent.target_genders || collectedInfo.target_genders || ['여성', '남성'],
          target_interests: currentContent.target_interests || collectedInfo.target_interests || [],
          copy_tone: params?.tone || collectedInfo.copy_tone || 'professional',
          strategy_name: currentContent.selected_strategy?.name || '',
          core_message: currentContent.selected_strategy?.core_message || ''
        };

        response = await axios.post('http://localhost:8000/api/content/regenerate/copy', requestData, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

      } else {
        // 'all' 또는 'auto' - 전체 재생성 (SSE 사용)
        const formData = {
          product_name: collectedInfo.product_name || '',
          product_description: collectedInfo.product_description || '',
          category: collectedInfo.category || 'other',
          product_image_path: collectedInfo.product_image_path || undefined, // 제품 이미지 경로 포함
          target_ages: collectedInfo.target_ages || [],
          target_genders: collectedInfo.target_genders || ['여성', '남성'],
          target_interests: collectedInfo.target_interests || [],
          copy_tone: params?.tone || collectedInfo.copy_tone || 'professional',
          regenerate_type: type,
          custom_request: params?.request || ''
        };

        console.log('전체 재생성 요청 (SSE):', formData);

        // SSE로 전체 재생성
        await fetchSSE(
          'http://localhost:8000/api/content/generate-stream',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
          },
          (message: SSEMessage) => {
            console.log('SSE 메시지 (재생성):', message);

            if (message.type === 'progress') {
              if (onProgress && message.step !== undefined && message.total !== undefined && message.message) {
                onProgress(message.step, message.total, message.message);
              }
            } else if (message.type === 'complete') {
              onContentGenerated(message.data);
              response = { data: { success: true, data: message.data } };
            } else if (message.type === 'error') {
              throw new Error(message.message || '콘텐츠 재생성 중 오류 발생');
            }
          },
          (error) => { throw error; }
        );
      }

      if (response && response.data.success) {
        onContentGenerated(response.data.data);
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: '✨ 수정이 완료되었습니다! 오른쪽에서 확인해보세요.\n\n추가 수정이 필요하시면 아래 옵션을 선택해주세요.',
            options: ['새 콘텐츠 생성', '전체 다시 생성', '이미지만 다시 생성', '카피만 다시 생성', '카피 톤 변경']
          }
        ]);
      }
    } catch (error: any) {
      console.error('재생성 중 오류:', error);
      throw error;
    }
  };

  const generateContent = async (infoToUse?: CollectedInfo) => {
    setIsLoading(true);
    onGenerationStart();

    // infoToUse가 있으면 사용, 없으면 collectedInfo 사용
    const info = infoToUse || collectedInfo;

    setMessages(prev => [
      ...prev,
      {
        role: 'assistant',
        content: '알겠습니다! 제품 정보를 분석하고 최적의 타겟층을 자동으로 선정한 뒤, 트렌드에 맞는 마케팅 콘텐츠를 생성하고 있습니다...'
      }
    ]);

    try {
      console.log('=== 콘텐츠 생성 요청 ===');
      console.log('사용할 정보 (info):', info);

      // 제품 이미지 업로드 (있는 경우)
      let uploadedImagePath = '';
      if (uploadedImageFile) {
        console.log('제품 이미지 업로드 중...', uploadedImageFile.name);

        const imageFormData = new FormData();
        imageFormData.append('file', uploadedImageFile);

        try {
          const uploadResponse = await axios.post(
            'http://localhost:8000/api/upload/product-image',
            imageFormData,
            {
              headers: {
                'Content-Type': 'multipart/form-data',
                Authorization: `Bearer ${token}`
              }
            }
          );

          if (uploadResponse.data.success) {
            uploadedImagePath = uploadResponse.data.data.file_path;
            console.log('✓ 제품 이미지 업로드 완료:', uploadedImagePath);

            // collectedInfo에 이미지 경로 저장 (수정 요청 시 재사용)
            setCollectedInfo(prev => ({
              ...prev,
              product_image_path: uploadedImagePath
            }));
          }
        } catch (uploadError) {
          console.error('제품 이미지 업로드 실패:', uploadError);
          // 업로드 실패해도 콘텐츠 생성은 진행
        }
      }

      const formData = {
        product_name: info.product_name || '',
        product_description: info.product_description || '',
        category: info.category || 'other',
        product_image_path: uploadedImagePath || info.product_image_path || undefined, // 업로드된 이미지 경로 또는 저장된 경로
        // 연령: 빈 배열이면 백엔드에서 AI가 자동 분석
        target_ages: info.target_ages || [],
        // 성별: 사용자 선택값 (기본값: 여성, 남성)
        target_genders: info.target_genders || ['여성', '남성'],
        // 관심사: 빈 배열이면 백엔드에서 AI가 자동 분석
        target_interests: info.target_interests || [],
        copy_tone: info.copy_tone || 'professional'
      };

      console.log('전송할 formData:', formData);
      console.log('========================');

      // SSE로 실시간 진행 상태를 받으며 콘텐츠 생성
      await fetchSSE(
        'http://localhost:8000/api/content/generate-stream',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(formData)
        },
        (message: SSEMessage) => {
          console.log('SSE 메시지:', message);

          if (message.type === 'progress') {
            // 진행 상태 업데이트
            if (onProgress && message.step !== undefined && message.total !== undefined && message.message) {
              onProgress(message.step, message.total, message.message);
            }
          } else if (message.type === 'complete') {
            // 생성 완료
            console.log('Content Data:', message.data);
            onContentGenerated(message.data);

            // 생성 완료 - currentStep을 conversationFlow.length 이상으로 설정
            setCurrentStep(conversationFlow.length);

            setMessages(prev => [
              ...prev,
              {
                role: 'assistant',
                content: '✨ 콘텐츠 생성이 완료되었습니다!\n\n제품 분석을 바탕으로 최적의 타겟층을 선정하고, 현재 트렌드에 맞는 이미지와 카피를 생성했습니다. 오른쪽에서 확인해보세요!\n\n수정이 필요하시면 아래 옵션을 선택하거나 직접 입력해주세요.',
                options: ['새 콘텐츠 생성', '전체 다시 생성', '이미지만 다시 생성', '카피만 다시 생성', '카피 톤 변경']
              }
            ]);
          } else if (message.type === 'error') {
            // 에러 처리
            throw new Error(message.message || '콘텐츠 생성 중 오류 발생');
          }
        },
        (error) => {
          // 에러 처리
          console.error('SSE Error:', error);
          throw error;
        }
      );
    } catch (error: any) {
      console.error('Error generating content:', error);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: '죄송합니다. 콘텐츠 생성 중 오류가 발생했습니다. 다시 시도해주세요.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleUserMessage(userInput);
    }
  };

  const currentQuestion = conversationFlow[currentStep];
  const hasOptions = currentQuestion?.options;
  const isMultiple = currentQuestion?.multiple;
  const selectedOptions = (collectedInfo[currentQuestion?.key as keyof CollectedInfo] as string[]) || [];

  // 생성 완료 후에도 입력창 표시
  const showInput = !hasOptions || currentStep >= conversationFlow.length;

  return (
    <div className="h-full flex flex-col">
      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {/* 업로드된 이미지 표시 (사용자 메시지에만) */}
              {message.imageUrl && message.role === 'user' && (
                <div className="mb-3 pb-3 border-b border-blue-500">
                  <img
                    src={message.imageUrl}
                    alt={message.imageName || 'Uploaded product'}
                    className="w-full max-w-[200px] rounded-lg mb-2"
                  />
                  <p className="text-xs opacity-90">📎 {message.imageName}</p>
                </div>
              )}

              <p className="text-sm whitespace-pre-wrap">{message.content}</p>

              {/* 옵션 버튼들 */}
              {message.options && message.role === 'assistant' && index === messages.length - 1 && (
                <div className="mt-3 space-y-2">
                  {message.options.map((option, optIndex) => (
                    <button
                      key={optIndex}
                      onClick={() => {
                        console.log('버튼 클릭:', option, 'currentStep:', currentStep, 'conversationFlow.length:', conversationFlow.length);
                        // "직접 입력"은 특별 처리
                        if (option === '직접 입력') {
                          setTimeout(() => {
                            inputRef.current?.focus();
                          }, 100);
                        }
                        // 생성 완료 후 수정 옵션인 경우
                        else if (currentStep >= conversationFlow.length) {
                          console.log('👉 handleModificationRequest 호출 예정');
                          handleModificationRequest(option);
                        } else {
                          console.log('👉 handleOptionClick 호출 예정');
                          handleOptionClick(option);
                        }
                      }}
                      className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                        isMultiple && selectedOptions.includes(option)
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
                      }`}
                      disabled={isLoading}
                    >
                      {option}
                    </button>
                  ))}

                  {/* 다중 선택일 경우 확인 버튼 */}
                  {isMultiple && (
                    <button
                      onClick={handleMultipleSelectionConfirm}
                      className="w-full mt-2 px-3 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
                      disabled={isLoading}
                    >
                      선택 완료
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 - 항상 표시 */}
      <div className="border-t border-gray-200 p-4">
        {/* 제품 이미지 업로드 (product_detail 단계에서만 표시) */}
        {currentStep === 1 && (
          <div className="mb-4">
            <div className="text-sm text-gray-600 mb-2">
              제품 이미지를 업로드하면 더 나은 마케팅 이미지를 생성할 수 있습니다 (선택사항)
            </div>

            {!imagePreviewUrl ? (
              <div className="flex items-center space-x-2">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/jpg,image/png,image/webp"
                  onChange={handleImageUpload}
                  className="hidden"
                  id="product-image-upload"
                />
                <label
                  htmlFor="product-image-upload"
                  className="flex items-center px-4 py-2 bg-white border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                >
                  <svg className="w-5 h-5 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span className="text-sm text-gray-700">제품 이미지 업로드</span>
                </label>
              </div>
            ) : (
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <img
                  src={imagePreviewUrl}
                  alt="Product preview"
                  className="w-16 h-16 object-cover rounded"
                />
                <div className="flex-1">
                  <p className="text-sm text-gray-700 font-medium">
                    {uploadedImageFile?.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {uploadedImageFile ? `${(uploadedImageFile.size / 1024).toFixed(1)} KB` : ''}
                  </p>
                </div>
                <button
                  onClick={handleRemoveImage}
                  className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                  title="이미지 제거"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            )}
          </div>
        )}

        <div className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              currentStep < conversationFlow.length && hasOptions && !isMultiple
                ? "위 옵션을 선택하거나 직접 입력하세요..."
                : currentStep >= conversationFlow.length
                ? "수정 요청을 입력하거나 위 옵션을 선택하세요..."
                : "메시지를 입력하세요..."
            }
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={() => handleUserMessage(userInput)}
            disabled={isLoading || !userInput.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            전송
          </button>
        </div>
      </div>
    </div>
  );
}
