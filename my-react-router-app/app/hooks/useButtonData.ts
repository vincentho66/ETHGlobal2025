// app/hooks/useButtonData.ts
import { useState, useEffect } from "react";

// Placeholder for button data type
export interface ButtonData {
  id: string;
  label: string;
  value: string | number; // You can adjust the type as needed
}

// Placeholder for API response type for buttons
interface ButtonApiResponse {
  buttons: ButtonData[];
}

export function useButtonData() {
  const [buttonData, setButtonData] = useState<ButtonData[] | null>(null);

  useEffect(() => {
    const fetchButtonData = async () => {
      try {
        // Replace this with your actual API endpoint
        // const response = await fetch('/api/buttons');
        // const data: ButtonApiResponse = await response.json();
        // setButtonData(data.buttons);

        // Simulate data for now
        const simulatedButtonData: ButtonApiResponse = {
          buttons: [
            { id: "button1", label: "Button 1", value: "Data 1" },
            { id: "button2", label: "Button 2", value: 123 },
            { id: "button3", label: "Button 3", value: "Data 3" },
            { id: "button4", label: "Button 4", value: 456 },
          ],
        };
        setButtonData(simulatedButtonData.buttons);
      } catch (error) {
        console.error("Error fetching button data:", error);
        setButtonData([]); // Set to empty array on error
      }
    };

    fetchButtonData();
  }, []);

  return { buttonData };
}
