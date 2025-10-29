export default function LoadingSpinner({ message = '생성 중...', progress = null }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-white rounded-lg shadow-md">
      {/* 스피너 */}
      <div className="relative w-16 h-16 mb-4">
        <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-200 rounded-full"></div>
        <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
      </div>

      {/* 메시지 */}
      <p className="text-lg font-semibold text-gray-800 mb-2">{message}</p>

      {/* 진행 상황 (옵션) */}
      {progress && (
        <div className="w-full max-w-md">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>{progress.current}</span>
            <span>{progress.total}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(progress.value / progress.max) * 100}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* 안내 문구 */}
      <p className="text-sm text-gray-500 mt-4">
        고품질 콘텐츠를 생성하는 중입니다. 최대 40초 정도 소요될 수 있습니다.
      </p>
    </div>
  );
}
