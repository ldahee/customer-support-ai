"use client";

interface HelpButtonProps {
  onClick: () => void;
}

export default function HelpButton({ onClick }: HelpButtonProps) {
  return (
    <button
      onClick={onClick}
      aria-label="도움말"
      className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-gray-300 text-gray-500 hover:border-blue-400 hover:text-blue-500 transition-colors font-semibold text-sm"
    >
      ?
    </button>
  );
}
