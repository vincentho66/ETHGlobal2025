// app/hooks/useChartData.ts
import { useState, useEffect } from "react";
import { fetchChartData } from "../services/api";

// Placeholder for chart data type
export interface ChartData {
  id: string;
  title: string;
  data: any[]; // Replace 'any' with your actual data structure
}

export function useChartData() {
  const [chartData, setChartData] = useState<ChartData[] | null>(null);
  const [activeChart, setActiveChart] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadChartData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchChartData();
        setChartData(data);
        setActiveChart(data[0]?.id || null);
      } catch (err) {
        setError("Failed to load chart data.");
      } finally {
        setIsLoading(false);
      }
    };

    loadChartData();
  }, []);

  return { chartData, activeChart, setActiveChart, isLoading, error };
}
