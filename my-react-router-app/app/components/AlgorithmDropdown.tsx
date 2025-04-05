// app/components/AlgorithmDropdown.tsx
import React from "react";

interface AlgorithmDropdownProps {
  algorithm: string;
  onChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
}

export function AlgorithmDropdown({
  algorithm,
  onChange,
}: AlgorithmDropdownProps) {
  return (
    <div className="mb-4">
      <label
        htmlFor="algorithm"
        className="block text-sm font-medium text-gray-700"
      >
        Algorithm
      </label>
      <select
        id="algorithm"
        value={algorithm}
        onChange={onChange}
        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
      >
        <option value="mvo">MVO</option>
        <option value="hrp">HRP</option>
      </select>
    </div>
  );
}
