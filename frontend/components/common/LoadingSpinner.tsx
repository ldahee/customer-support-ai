export default function LoadingSpinner({ message = "답변을 생성 중입니다..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center gap-3 py-6">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-200 border-t-blue-500" />
      <p className="text-sm text-gray-500">{message}</p>
    </div>
  );
}
