import { useState, useEffect } from "react";
import { useChartData } from "../hooks/useChartData";
import { useDropdownData } from "../hooks/useDropdownData";
import { useChatModal } from "../hooks/useChatModal";
import { InputForm } from "../components/InputForm";
import type { InputFormData } from "../components/InputForm";
import { fetchData } from "../services/api";
import type { ApiInputData } from "../services/api";

declare global {
  interface Window {
    ethereum?: any;
  }
}

export function Welcome() {
  const [account, setAccount] = useState<string | null>(null);
  const [isMetaMaskInstalled, setIsMetaMaskInstalled] = useState(false);
  const {
    chartData,
    activeChart,
    setActiveChart,
    isLoading: isChartLoading,
    error: chartError,
  } = useChartData();
  const {
    dropdownData,
    dropdown1Value,
    dropdown2Value,
    handleDropdown1Change,
    handleDropdown2Change,
  } = useDropdownData();
  const {
    isChatOpen,
    openChat,
    closeChat,
    messages,
    newMessage,
    handleNewMessageChange,
    sendMessage,
    isLoading: isChatLoading,
  } = useChatModal();
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isApiLoading, setIsApiLoading] = useState<boolean>(false);

  useEffect(() => {
    // Check if MetaMask is installed
    setIsMetaMaskInstalled(typeof window.ethereum !== "undefined");
  }, []);

  const connectWallet = async () => {
    if (window.ethereum) {
      try {
        // Request account access
        const accounts = await window.ethereum.request({
          method: "eth_requestAccounts",
        });
        setAccount(accounts[0]);
      } catch (error) {
        console.error("Error connecting to MetaMask:", error);
      }
    }
  };

  const handleTabClick = (chartId: string) => {
    setActiveChart(chartId);
  };

  const handleStart = async (inputData: InputFormData) => {
    setIsApiLoading(true);
    setApiError(null);
    try {
      const data = await fetchData(inputData as ApiInputData);
      setApiResponse(data);
    } catch (error) {
      setApiError("Failed to fetch data from API.");
    } finally {
      setIsApiLoading(false);
    }
  };

  return (
    <main className="welcome-main">
      {/* Header Section */}
      <header className="welcome-header">
        {/* MetaMask Button (Top Right) */}
        <div className="p-4">
          {isMetaMaskInstalled ? (
            <button
              onClick={connectWallet}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              {account
                ? `Connected: ${account.substring(0, 6)}...${account.substring(
                    38
                  )}`
                : "Connect to MetaMask"}
            </button>
          ) : (
            <p className="text-red-500">MetaMask not installed!</p>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="welcome-container">
        {/* Dropdowns */}
        <div className="welcome-dropdown-container">
          {dropdownData && (
            <div className="flex space-x-4">
              {/* Dropdown 1 */}
              <select
                value={dropdown1Value || ""}
                onChange={handleDropdown1Change}
                className="welcome-dropdown"
              >
                <option value="" disabled>
                  Select Option 1
                </option>
                {dropdownData.dropdown1.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>

              {/* Dropdown 2 */}
              <select
                value={dropdown2Value || ""}
                onChange={handleDropdown2Change}
                className="welcome-dropdown"
              >
                <option value="" disabled>
                  Select Option 2
                </option>
                {dropdownData.dropdown2.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Chart and Button Section */}
        <div className="welcome-chart-section">
          <div className="welcome-chart-and-buttons">
            {/* Chart Area */}
            <div className="welcome-chart-area">
              <div className="welcome-chart-content">
                {isChartLoading ? (
                  <div className="h-full flex items-center justify-center">
                    <p className="text-center">Loading charts...</p>
                  </div>
                ) : chartError ? (
                  <div className="h-full flex items-center justify-center">
                    <p className="text-center text-red-500">
                      {chartError}
                    </p>
                  </div>
                ) : chartData?.length === 0 ? (
                  <div className="h-full flex items-center justify-center">
                    <p className="text-center">No chart data available.</p>
                  </div>
                ) : (
                  <>
                    {/* Tab Navigation */}
                    <div className="welcome-chart-tab-container">
                      {chartData?.map((chart) => (
                        <button
                          key={chart.id}
                          onClick={() => handleTabClick(chart.id)}
                          className={`welcome-chart-tab ${
                            activeChart === chart.id
                              ? "welcome-chart-tab-active"
                              : "welcome-chart-tab-inactive"
                          }`}
                        >
                          {chart.title}
                        </button>
                      ))}
                    </div>

                    {/* Chart Display Area */}
                    <div className="welcome-chart-display">
                      {chartData?.map((chart) => {
                        if (chart.id === activeChart) {
                          return (
                            <div key={chart.id} className="h-full">
                              {chart.data.length > 0 ? (
                                // Replace this with your actual chart component
                                <div className="h-full bg-gray-100 flex items-center justify-center">
                                  <p>
                                    {chart.title} Data:{" "}
                                    {JSON.stringify(chart.data)}
                                  </p>
                                </div>
                              ) : (
                                <div className="h-full bg-gray-100 flex items-center justify-center">
                                  <p>
                                    No data available for {chart.title}
                                  </p>
                                </div>
                              )}
                            </div>
                          );
                        }
                        return null;
                      })}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
        {/* Input Form */}
        <InputForm onSubmit={handleStart} />
        {isApiLoading && <p>Loading API data...</p>}
        {apiError && <p className="text-red-500">{apiError}</p>}
        {apiResponse && (
          <pre>
            <code>{JSON.stringify(apiResponse, null, 2)}</code>
          </pre>
        )}
      </div>
      {/* Chat Modal */}
      {isChatOpen && (
        <div className="chat-modal">
          <div className="chat-header">
            <h3 className="font-bold">AI Assistant</h3>
            <button onClick={closeChat}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-6 h-6"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
          <div className="chat-body">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`chat-message ${
                  message.role === "user"
                    ? "chat-message-user"
                    : "chat-message-assistant"
                }`}
              >
                {message.content}
              </div>
            ))}
            {isChatLoading && (
              <div className="chat-message chat-message-assistant">
                Loading...
              </div>
            )}
          </div>
          <div className="chat-footer">
            <textarea
              className="chat-input"
              value={newMessage}
              onChange={handleNewMessageChange}
              placeholder="Type your message..."
            />
            <button className="chat-send-button" onClick={sendMessage}>
              Send
            </button>
          </div>
        </div>
      )}

      {/* Chat Open Button */}
      {!isChatOpen && (
        <button className="chat-open-button" onClick={openChat}>
          💬 {/* Chat Bubble Emoji */}
        </button>
      )}
    </main>
  );
}
