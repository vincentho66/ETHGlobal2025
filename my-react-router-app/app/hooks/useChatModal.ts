// app/hooks/useChatModal.ts

import { useState, useCallback } from "react";

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export function useChatModal() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const openChat = useCallback(() => {
    setIsChatOpen(true);
  }, []);

  const closeChat = useCallback(() => {
    setIsChatOpen(false);
    // setMessages([]);
    setNewMessage("");
  }, []);

  const handleNewMessageChange = useCallback(
    (event: React.ChangeEvent<HTMLTextAreaElement>) => {
      setNewMessage(event.target.value);
    },
    []
  );

  const sendMessage = useCallback(async () => {
    if (newMessage.trim() === "") return;

    const userMessage: Message = { role: "user", content: newMessage };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setNewMessage("");
    setIsLoading(true);

    try {
      // Replace this with your actual API call
      const response = await fetch("http://127.0.0.1:8000/chat?user_input="+ newMessage, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_input: newMessage }),
      });
      const data = await response.json();
      const assistantMessage: Message = { role: 'assistant', content: data.answer };
      setMessages((prevMessages) => [...prevMessages, assistantMessage]);

      // Simulate API response for now
    //   await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate 1 second delay
    //   const assistantMessage: Message = {
    //     role: "assistant",
    //     content: `You said: ${newMessage}`,
    //   };
    //   setMessages((prevMessages) => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I'm having trouble connecting right now.",
      };
    //   setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [messages, newMessage]);

  return {
    isChatOpen,
    openChat,
    closeChat,
    messages,
    newMessage,
    handleNewMessageChange,
    sendMessage,
    isLoading,
  };
}
