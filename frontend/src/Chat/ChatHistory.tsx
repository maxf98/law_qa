import React, { useState, useEffect, useCallback } from "react";
import "./Chat.css";
import TypingIndicator from "./TypingIndicator";
import ChatItem from "./ChatItem";
import {
  TextReference,
  VectorReference,
  ChatItemReferences,
} from "../References/Reference";

type ChatHistoryProps = {
  chat: Array<[string, string | null]>;
  references: Array<ChatItemReferences>;
  onTapReference: (arg0: TextReference | VectorReference) => void;
};

// presents QA
function ChatHistory({ chat, references, onTapReference }: ChatHistoryProps) {
  useEffect(() => {
    document.getElementById("scrollTarget")?.scrollIntoView();
  }, [chat]);

  return (
    <div id="chat-container">
      {chat.length > 0 && (
        <div className="chat">
          {chat.map(([question, answer], idx, arr) => (
            <div key={idx}>
              <ChatItem
                text={question}
                isQuestion={true}
                onTapReference={onTapReference}
              />

              {answer !== null && references[idx] !== undefined ? (
                <ChatItem
                  text={answer}
                  vectorReferences={references[idx].vector_references}
                  onTapReference={onTapReference}
                  isQuestion={false}
                />
              ) : (
                <TypingIndicator />
              )}
            </div>
          ))}
          <div id="scrollTarget"></div>
        </div>
      )}
    </div>
  );
}

export default ChatHistory;
