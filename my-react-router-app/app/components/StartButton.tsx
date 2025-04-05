// app/components/StartButton.tsx
import React from "react";

interface StartButtonProps {
  onClick: () => void;
}

export function StartButton({ onClick }: StartButtonProps) {
  return (
    <button
      onClick={onClick}
      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
    >
      Start
    </button>
  );
}
