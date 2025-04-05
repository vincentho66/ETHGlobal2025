// app/hooks/useChartData.ts
import { useState } from "react";
import type { TokenPriceData } from "../services/api";

// Placeholder for chart data type
export interface ChartData {
  id: string;
  title: string;
  data: string;
}

export function useChartData() {
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [activeChart, setActiveChart] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  return {
    chartData,
    activeChart,
    setActiveChart,
    isLoading,
    error,
    setChartData,
  };
}
