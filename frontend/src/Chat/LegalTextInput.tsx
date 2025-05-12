import React, { useState, useEffect, useRef } from "react";
import Session from "../Session";

type LegalTextInputProps = {
  session: Session;
  onSummarise: () => void;
};

function LegalTextInput({ session, onSummarise }: LegalTextInputProps) {
  const [submitted, setSubmitted] = useState(false);
  const [isEmpty, setIsEmpty] = useState(true);
  const inputElement = useRef<HTMLTextAreaElement>(null);

  const handleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (event.target.value.trim().length > 0) {
      setIsEmpty(false);
    } else {
      setIsEmpty(true);
    }
  };

  useEffect(() => {
    setSubmitted(false);
    if (inputElement.current) {
      inputElement.current.value = "";
    }
  }, [session]);

  function submitLegalText() {
    const legalTextData = { legal_text: inputElement?.current?.value };

    fetch(session.legalTextURL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(legalTextData),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then(() => {
        onSummarise();
        setSubmitted(true);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  return (
    <div className="LegalTextInputContainer">
      <textarea
        id="LegalTextArea"
        ref={inputElement}
        readOnly={submitted}
        onChange={handleChange}
        placeholder="Enter legal text you wish to summarise"
      />

      {!submitted ? (
        <button
          type="button"
          className="SummariseButton basic-button"
          onClick={submitLegalText}
          disabled={isEmpty}
        >
          Summarise
        </button>
      ) : null}
    </div>
  );
}

export default LegalTextInput;
