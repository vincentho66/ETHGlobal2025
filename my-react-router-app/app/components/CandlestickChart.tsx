import {
    ResponsiveContainer,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ComposedChart, // Use ComposedChart instead
    Bar, // Use Bar to render candlestick-like visuals
  } from "recharts";
  

interface CandlestickChartProps {
  data: {
    time: number;
    open: number;
    high: number;
    low: number;
    close: number;
  }[];
}

export function CandlestickChart({ data }: CandlestickChartProps) {
  console.trace(data);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <ComposedChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="time"
          type="number"
          domain={["dataMin", "dataMax"]}
          tickFormatter={(unixTimestamp) =>
            new Date(unixTimestamp).toLocaleDateString()
          }
        />
        <YAxis domain={["dataMin", "dataMax"]} />
        <Tooltip />
        <Bar
          dataKey="close"
          fill="#8884d8"
          isAnimationActive={false}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
