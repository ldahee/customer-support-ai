"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/", label: "사용자 화면" },
  { href: "/operator", label: "운영자 화면" },
];

export default function TabNav() {
  const pathname = usePathname();

  return (
    <div className="flex gap-1">
      {TABS.map((tab) => {
        const isActive = pathname === tab.href;
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={[
              "px-4 py-2 rounded-t-lg text-sm font-medium transition-colors",
              isActive
                ? "bg-white text-blue-600 border border-b-white border-gray-200 -mb-px"
                : "text-gray-500 hover:text-gray-700 hover:bg-white/50",
            ].join(" ")}
          >
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}
