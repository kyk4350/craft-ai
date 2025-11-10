/**
 * SSE (Server-Sent Events) 유틸리티
 * POST 요청으로 SSE 스트림을 받을 수 있도록 fetch API 사용
 */

export interface SSEMessage {
  type: 'progress' | 'complete' | 'error';
  step?: number;
  total?: number;
  message?: string;
  data?: any;
  generation_time?: number;
}

export async function fetchSSE(
  url: string,
  options: RequestInit,
  onMessage: (message: SSEMessage) => void,
  onError?: (error: Error) => void,
  onComplete?: () => void
): Promise<void> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Accept': 'text/event-stream',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is null');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        console.log('SSE stream closed');
        if (onComplete) onComplete();
        break;
      }

      // 새로운 데이터를 버퍼에 추가
      buffer += decoder.decode(value, { stream: true });

      // SSE 메시지는 "\n\n"로 구분됨
      const messages = buffer.split('\n\n');

      // 마지막 조각은 불완전할 수 있으므로 버퍼에 유지
      buffer = messages.pop() || '';

      // 각 메시지 처리
      for (const message of messages) {
        if (message.trim() === '') continue;

        // "data: " 접두사 제거
        const dataMatch = message.match(/^data: (.+)$/m);
        if (dataMatch) {
          try {
            const parsedData: SSEMessage = JSON.parse(dataMatch[1]);
            onMessage(parsedData);
          } catch (e) {
            console.error('Failed to parse SSE message:', e, dataMatch[1]);
          }
        }
      }
    }
  } catch (error) {
    console.error('SSE fetch error:', error);
    if (onError) {
      onError(error as Error);
    }
  }
}
