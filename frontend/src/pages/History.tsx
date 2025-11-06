import React, { useEffect, useState } from 'react';
import { contentsApi, ContentItem } from '../utils/api';

const History: React.FC = () => {
  const [contents, setContents] = useState<ContentItem[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedContent, setSelectedContent] = useState<ContentItem | null>(null);

  // 페이지네이션 상태
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12; // 3열 x 4행 = 12개

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  // 이미지 URL을 전체 URL로 변환
  const getFullImageUrl = (imageUrl: string) => {
    if (!imageUrl) return '';
    if (imageUrl.startsWith('http')) return imageUrl;
    return `${API_BASE_URL}${imageUrl}`;
  };

  useEffect(() => {
    loadContents(currentPage);
  }, [currentPage]);

  const loadContents = async (page: number) => {
    setIsLoading(true);
    setError('');
    try {
      const offset = (page - 1) * itemsPerPage;
      const response = await contentsApi.getContents({
        limit: itemsPerPage,
        offset: offset
      });
      setContents(response.data.contents);
      setTotal(response.data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : '콘텐츠 목록을 불러오는데 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 전체 페이지 수 계산
  const totalPages = Math.ceil(total / itemsPerPage);

  // 페이지 변경 핸들러
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDelete = async (contentId: number) => {
    if (!window.confirm('이 콘텐츠를 삭제하시겠습니까?')) {
      return;
    }

    try {
      await contentsApi.deleteContent(contentId);

      // 삭제 후 현재 페이지가 비었으면 이전 페이지로
      if (contents.length === 1 && currentPage > 1) {
        setCurrentPage(currentPage - 1);
      } else {
        // 현재 페이지 새로고침
        loadContents(currentPage);
      }

      if (selectedContent?.id === contentId) {
        setSelectedContent(null);
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : '삭제에 실패했습니다');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">콘텐츠 히스토리</h1>
          <p className="mt-2 text-gray-600">
            생성된 콘텐츠 총 <span className="font-semibold text-blue-600">{total}개</span>
          </p>
        </div>

        {/* Loading */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">로딩 중...</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && contents.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg shadow">
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
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
              />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">콘텐츠가 없습니다</h3>
            <p className="mt-2 text-gray-500">새로운 콘텐츠를 생성해보세요!</p>
          </div>
        )}

        {/* Contents Grid */}
        {!isLoading && !error && contents.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {contents.map((content) => (
              <div
                key={content.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer overflow-hidden"
                onClick={() => setSelectedContent(content)}
              >
                {/* Image */}
                <div className="aspect-video bg-gray-200 relative overflow-hidden">
                  {content.image_url ? (
                    <img
                      src={getFullImageUrl(content.image_url)}
                      alt={content.product_name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                        const parent = e.currentTarget.parentElement;
                        if (parent && !parent.querySelector('.fallback-text')) {
                          const fallback = document.createElement('div');
                          fallback.className = 'w-full h-full flex items-center justify-center text-gray-400 fallback-text';
                          fallback.textContent = '이미지를 불러올 수 없습니다';
                          parent.appendChild(fallback);
                        }
                      }}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      이미지 없음
                    </div>
                  )}
                </div>

                {/* Content Info */}
                <div className="p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 truncate">
                    {content.product_name}
                  </h3>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {content.copy_text}
                  </p>

                  {/* Meta Info */}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{content.category}</span>
                    <span>{formatDate(content.created_at)}</span>
                  </div>

                  {/* Hashtags */}
                  {content.hashtags && content.hashtags.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {content.hashtags.slice(0, 3).map((tag, index) => (
                        <span
                          key={index}
                          className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                      {content.hashtags.length > 3 && (
                        <span className="text-xs text-gray-500">
                          +{content.hashtags.length - 3}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Delete Button */}
                <div className="px-4 pb-4">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(content.id);
                    }}
                    className="w-full text-sm text-red-600 hover:text-red-700 py-2 border border-red-200 rounded hover:bg-red-50 transition"
                  >
                    삭제
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {!isLoading && !error && totalPages > 1 && (
          <div className="mt-8 flex justify-center items-center gap-2">
            {/* Previous Button */}
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              이전
            </button>

            {/* Page Numbers */}
            <div className="flex gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                // 현재 페이지 기준 앞뒤 2페이지씩만 표시
                if (
                  page === 1 ||
                  page === totalPages ||
                  (page >= currentPage - 2 && page <= currentPage + 2)
                ) {
                  return (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`px-4 py-2 border rounded-lg transition ${
                        currentPage === page
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      {page}
                    </button>
                  );
                } else if (
                  page === currentPage - 3 ||
                  page === currentPage + 3
                ) {
                  return (
                    <span key={page} className="px-2 py-2">
                      ...
                    </span>
                  );
                }
                return null;
              })}
            </div>

            {/* Next Button */}
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              다음
            </button>
          </div>
        )}

        {/* Detail Modal */}
        {selectedContent && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedContent(null)}
          >
            <div
              className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedContent.product_name}
                </h2>
                <button
                  onClick={() => setSelectedContent(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-6">
                {/* Image */}
                {selectedContent.image_url && (
                  <div className="mb-6 rounded-lg overflow-hidden">
                    <img
                      src={getFullImageUrl(selectedContent.image_url)}
                      alt={selectedContent.product_name}
                      className="w-full"
                    />
                  </div>
                )}

                {/* Copy Text */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">카피</h3>
                  <p className="text-gray-700 leading-relaxed">{selectedContent.copy_text}</p>
                </div>

                {/* Hashtags */}
                {selectedContent.hashtags && selectedContent.hashtags.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">해시태그</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedContent.hashtags.map((tag, index) => (
                        <span
                          key={index}
                          className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Product Info */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">제품 정보</h3>
                  <dl className="space-y-2">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">카테고리</dt>
                      <dd className="text-gray-900">{selectedContent.category}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">제품 설명</dt>
                      <dd className="text-gray-900">{selectedContent.product_description}</dd>
                    </div>
                  </dl>
                </div>

                {/* Target Info */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">타겟 정보</h3>
                  <dl className="grid grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">나이대</dt>
                      <dd className="text-gray-900">{selectedContent.target_age_group}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">성별</dt>
                      <dd className="text-gray-900">{selectedContent.target_gender}</dd>
                    </div>
                    <div className="col-span-2">
                      <dt className="text-sm font-medium text-gray-500">관심사</dt>
                      <dd className="text-gray-900">{selectedContent.target_interests.join(', ')}</dd>
                    </div>
                  </dl>
                </div>

                {/* Meta */}
                <div className="pt-4 border-t text-sm text-gray-500">
                  생성일: {formatDate(selectedContent.created_at)}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
