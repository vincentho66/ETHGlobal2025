// app/hooks/usePeriodLookbackData.ts
import { useState } from "react";

export function usePeriodLookbackData() {
  const [period, setPeriod] = useState<string>("day"); // Default to "day"
  const [lookback, setLookback] = useState<string>("10"); // Default to "10"

  const handlePeriodChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setPeriod(event.target.value);
  };

  const handleLookbackChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLookback(event.target.value);
  };

  return {
    period,
    lookback,
    handlePeriodChange,
    handleLookbackChange,
  };
}
