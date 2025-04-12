// src/App.tsx
import { useState, useRef, useEffect } from "react";
import logo from "/logo.png";

function App() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [typingMessage, setTypingMessage] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sends the user message to the backend and handles the response
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput(""); // Clear input field upon sending
    setIsTyping(true);
    setTypingMessage("");

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/ask/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: input,
          history: updatedMessages,
        }),
      });

      const data = await res.json();
      const fullText = data.answer;
      let current = "";
      let i = 0;

      // Simulates typing effect
      const type = () => {
        if (i < fullText.length) {
          current += fullText[i];
          setTypingMessage(current);
          i++;
          setTimeout(type, 15); // Typing speed
        } else {
          setMessages([...updatedMessages, { role: "bot", content: fullText }]);
          setIsTyping(false);
          setTypingMessage("");
        }
      };

      type();
    } catch (err) {
      console.error("Error:", err);
      setIsTyping(false);
    }
  };

  // Automatically scrolls to the bottom when messages or typing change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typingMessage]);

  return (
    <div className="min-h-screen flex flex-col bg-zinc-900 text-white p-4">
      {/* Header with logo and description */}
      <div className="flex flex-col items-center mb-6">
        <img src={logo} alt="LeagueGPT Logo" className="w-20 h-20 mb-5" />
        <h1 className="text-4xl font-bold text-center mb-2">lolGPT</h1>
        <p className="text-center text-zinc-400 max-w-xl mx-auto">
          Ask your questions about patch notes, builds, or game mechanics. lolGPT helps you improve with a League of Legends specialized AI.
        </p>
      </div>

      {/* Chat message display area */}
      <div className="flex-1 overflow-y-auto space-y-4 px-2">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`max-w-xl px-4 py-3 rounded-2xl ${
              msg.role === "user"
                ? "bg-blue-600 self-end ml-auto text-white"
                : "bg-zinc-800 text-gray-200"
            }`}
          >
            {msg.content}
          </div>
        ))}

        {/* Typing animation */}
        {isTyping && (
          <div className="max-w-xl px-4 py-3 rounded-2xl bg-zinc-800 text-gray-200">
            {typingMessage}
            <span className="animate-pulse">|</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="mt-4 flex gap-2">
        <input
          className="flex-1 px-4 py-2 rounded-xl bg-zinc-800 border border-zinc-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask a question about League of Legends..."
        />
        <button
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-xl font-semibold"
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default App;
