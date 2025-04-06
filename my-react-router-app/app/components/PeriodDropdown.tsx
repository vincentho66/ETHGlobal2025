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
        <option value="month">month</option>
        <option value="week">week</option>
        <option value="day">day</option>
        <option value="4hour">4hour</option>
        <option value="hour">hour</option>
        <option value="15min">15min</option>
        <option value="5min">5min</option>
      </select>
    </div>
  );
}
