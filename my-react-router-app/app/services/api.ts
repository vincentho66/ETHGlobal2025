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
  
  // New fetchChartData
  export interface TokenPriceData {
    time: number;
    open: number;
    high: number;
    low: number;
    close: number;
  }
  
  export async function fetchChartData(
    symbol: string,
    period: string,
    limit: string
  ): Promise<string> {
    try {
      const response = await fetch(
        `http://192.168.253.51:8000/token_price?symbol=${symbol}&period=${period}&limit=${limit}`
      );
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          `HTTP error! status: ${response.status}, message: ${
            errorData.message || "Unknown error"
          }`
        );
      }
  
      const responseText = await response.text(); // Get the response as text
      const data = responseText; // Parse the string to JSON
        console.log(data); // Log the parsed data
      return data;
    } catch (error) {
      console.error("Error fetching chart data:", error);
      throw error;
    }
  }
  