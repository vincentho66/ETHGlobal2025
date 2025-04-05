// app/components/PeriodDropdown.tsx
import React from "react";

interface PeriodDropdownProps {
  period: string;
  onChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
}

export function PeriodDropdown({ period, onChange }: PeriodDropdownProps) {
  return (
    <div className="mb-4">
      <label htmlFor="period" className="block text-sm font-medium text-gray-700">
        Period
      </label>
      <select
        id="period"
        value={period}
        onChange={onChange}
        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
      >
        <option value="M">M</option>
        <option value="W">W</option>
        <option value="D">D</option>
        <option value="4h">4h</option>
        <option value="1h">1h</option>
        <option value="15m">15m</option>
        <option value="5m">5m</option>
      </select>
    </div>
  );
}
