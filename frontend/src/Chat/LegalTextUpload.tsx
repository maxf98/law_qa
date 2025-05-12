import React, { useState, useEffect, useRef } from "react";
import Session from "../Session";
import "./Chat.css";

type LegalTextUploadProps = {
  session: Session;
  uploadDocument: (arg0: File) => void;
  //   onUpload: () => void;
};

function LegalTextInput({ session, uploadDocument }: LegalTextUploadProps) {
  const hiddenFileInput = useRef<HTMLInputElement>(null);

  function handleClick() {
    hiddenFileInput.current?.click();
  }

  function upload() {
    const file = hiddenFileInput.current?.files?.[0];
    if (file) {
      uploadDocument(file);
      // Process the file as needed
    }
  }

  return (
    <button className="LegalTextUploadButton ChatInteractionBorder">
      <img
        src="legalTextIcon.png"
        alt="legal text upload"
        onClick={handleClick}
      />
      <input
        type="file"
        accept=".pdf"
        ref={hiddenFileInput}
        id="fileInput"
        name="fileInput"
        style={{ display: "none" }}
        onChange={upload}
      />
    </button>
  );
}

export default LegalTextInput;
