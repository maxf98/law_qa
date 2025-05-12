import React, { useState, useRef, useEffect } from "react";
import "./Chat.css";
import Session from "../Session";

type ChatBoxProps = {
  session: Session;
  onSend: (arg0: string) => void;
  isDisabled: boolean;
};

function ChatBox({ session, onSend, isDisabled }: ChatBoxProps) {
  const [inputValue, setInputValue] = useState<string>("");
  const textbox = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    adjustSize();
  }, [inputValue]);

  function submitQuestion() {
    fetch(session.chatURL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ new_question: inputValue }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  function adjustSize() {
    if (textbox.current !== null) {
      textbox.current.style.height = "inherit";
      textbox.current.style.height = `${textbox.current.scrollHeight}px`;
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
  };

  const handleSend = () => {
    submitQuestion();
    onSend(inputValue);
    setInputValue("");
    adjustSize();
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chatbox-container ChatInteractionBorder">
      <textarea
        id="chat-input-textarea"
        value={inputValue}
        rows={1}
        ref={textbox}
        onChange={handleInputChange}
        onKeyDown={handleKeyPress}
        placeholder="Ask a legal question..."
        disabled={isDisabled}
      />
      <button
        type="button"
        onClick={handleSend}
        className="send-button basic-button"
        disabled={isDisabled || inputValue === ""}
      >
        Send
        {/* <img src="sendIcon.png" alt="send" /> */}
      </button>
    </div>
  );
}

export default ChatBox;
