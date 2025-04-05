// app/hooks/useChartData.ts
import { useState, useEffect } from "react";

// Placeholder for chart data type
export interface ChartData {
  id: string;
  title: string;
  data: any[]; // Replace 'any' with your actual data structure
}

// Placeholder for API response type
interface ApiResponse {
  charts: ChartData[];
}

export function useChartData() {
  const [chartData, setChartData] = useState<ChartData[] | null>(null);
  const [activeChart, setActiveChart] = useState<string | null>(null);

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        // Replace this with your actual API endpoint
        // const response = await fetch('/api/charts');
        // const data: ApiResponse = await response.json();
        // setChartData(data.charts);

        // Simulate data for now
        const simulatedData: ApiResponse = {
          charts: [
            {
              id: "chart1",
              title: "Chart 1",
              data: [
                { x: 1, y: 10 },
                { x: 2, y: 15 },
                { x: 3, y: 12 },
              ],
            },
            {
              id: "chart2",
              title: "Chart 2",
              data: [
                { x: 1, y: 5 },
                { x: 2, y: 8 },
                { x: 3, y: 6 },
              ],
            },
            {
              id: "chart3",
              title: "Chart 3",
              data: [], // Empty data example
            },
          ],
        };
        setChartData(simulatedData.charts);
        setActiveChart("chart1"); // Set the default active chart
      } catch (error) {
        console.error("Error fetching chart data:", error);
        setChartData([]); // Set to empty array on error
      }
    };

    fetchChartData();
  }, []);

  return { chartData, activeChart, setActiveChart };
}
