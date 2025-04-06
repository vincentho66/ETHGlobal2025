// app/hooks/useDropdownData.ts
import { useState, useEffect } from "react";

export interface DropdownData {
  dropdown1: string[];
  dropdown2: string[];
}

export function useDropdownData() {
  const [dropdownData, setDropdownData] = useState<DropdownData | null>(null);
  const [dropdown1Value, setDropdown1Value] = useState<string | null>(null);
  const [dropdown2Value, setDropdown2Value] = useState<string | null>(null);

  useEffect(() => {
    // Fetch dropdown data from JSON
    fetch("/data/dropdown-data.json") // Assuming the JSON file is in the "public/data" folder
      .then((response) => response.json())
      .then((data) => setDropdownData(data))
      .catch((error) => console.error("Error fetching dropdown data:", error));
  }, []);

  const handleDropdown1Change = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setDropdown1Value(event.target.value);
  };

  const handleDropdown2Change = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setDropdown2Value(event.target.value);
  };

  return {
    dropdownData,
    dropdown1Value,
    dropdown2Value,
    handleDropdown1Change,
    handleDropdown2Change,
  };
}
