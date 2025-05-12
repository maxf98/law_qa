import React, { useState } from "react";
import "./Chat.css";
import Session from "../Session";
import ChatBox from "./ChatBox";
import LegalTextUpload from "./LegalTextUpload";
import { Document } from "react-pdf";

type ChatInteractionContainerProps = {
  session: Session;
  onSend: (arg0: string) => void;
  isDisabled: boolean;
  uploadDocument: (arg0: File) => void;
};

function ChatInteractionContainer({
  session,
  onSend,
  isDisabled,
  uploadDocument,
}: ChatInteractionContainerProps) {
  const [isChatting, setIsChatting] = useState(true);

  return (
    <div className="ChatInteractionContainer">
      {/* <LegalTextUpload session={session} uploadDocument={uploadDocument} /> */}
      <ChatBox session={session} onSend={onSend} isDisabled={isDisabled} />
    </div>
  );
}

export default ChatInteractionContainer;
