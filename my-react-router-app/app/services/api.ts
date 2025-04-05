// app/services/api.ts
export interface ApiInputData {
    period: string;
    limit: string;
    lookback: string;
    rebalance: string;
    algorithm: string;
  }
  
  export async function fetchData(inputData: ApiInputData) {
    try {
      const response = await fetch("/your-api-endpoint", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(inputData),
      });
  
      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }
  
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("API error:", error);
      throw error; // Re-throw to handle in components
    }
  }
  
  export async function fetchChartData() {
    try {
      // Replace this with your actual API endpoint
      // const response = await fetch('/api/charts');
      // const data: ApiResponse = await response.json();
      // setChartData(data.charts);
  
      // Simulate data for now
      const simulatedData = [
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
      ];
      return simulatedData;
    } catch (error) {
      console.error("Error fetching chart data:", error);
      throw error;
    }
  }
  