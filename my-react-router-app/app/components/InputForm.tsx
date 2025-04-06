// app/components/InputForm.tsx
import React, { useState } from "react";
import { PeriodDropdown } from "./PeriodDropdown";
import { IntegerInput } from "./IntegerInput";
import { AlgorithmDropdown } from "./AlgorithmDropdown";
import { StartButton } from "./StartButton";

export interface InputFormData {
  period: string;
  limit: string;
  lookback: string;
  rebalance: string;
  algorithm: string;
}

interface InputFormProps {
  onSubmit: (data: InputFormData) => void;
  onPeriodChange: (period: string) => void;
  onLimitChange: (limit: string) => void;
}

export function InputForm({ onSubmit, onPeriodChange, onLimitChange }: InputFormProps) {
  const [formData, setFormData] = useState<InputFormData>({
    period: "D",
    limit: "100",
    lookback: "10",
    rebalance: "1",
    algorithm: "mvo",
  });

  const handleChange = (
    key: keyof InputFormData,
    value: string
  ) => {
    setFormData((prevData) => ({
      ...prevData,
      [key]: value,
    }));
    if (key === "period") {
      onPeriodChange(value);
    }
    if (key === "limit") {
      onLimitChange(value);
    }
  };

  const handleStartClick = () => {
    onSubmit(formData);
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <PeriodDropdown
        period={formData.period}
        onChange={(e) => handleChange("period", e.target.value)}
      />
      <IntegerInput
        label="Limit"
        value={formData.limit}
        onChange={(e) => handleChange("limit", e.target.value)}
        id="limit"
      />
      <IntegerInput
        label="Lookback"
        value={formData.lookback}
        onChange={(e) => handleChange("lookback", e.target.value)}
        id="lookback"
      />
      <IntegerInput
        label="Rebalance"
        value={formData.rebalance}
        onChange={(e) => handleChange("rebalance", e.target.value)}
        id="rebalance"
      />
      <AlgorithmDropdown
        algorithm={formData.algorithm}
        onChange={(e) => handleChange("algorithm", e.target.value)}
      />
      <StartButton onClick={handleStartClick} />
    </div>
  );
}
