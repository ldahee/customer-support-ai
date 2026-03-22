interface AnswerDisplayProps {
  answer: string;
}

export default function AnswerDisplay({ answer }: AnswerDisplayProps) {
  return (
    <div className="rounded-xl border border-blue-100 bg-blue-50 px-5 py-4">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-blue-400">
        답변
      </p>
      <p className="text-sm leading-relaxed text-gray-800 whitespace-pre-wrap">{answer}</p>
    </div>
  );
}
