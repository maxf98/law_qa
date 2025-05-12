import React, { useState, useEffect, useCallback } from "react";
import "./Chat.css";
import Session from "../Session";
import {
  ChatItemReferences,
  TextReference,
  VectorReference,
} from "../References/Reference";
import ReferenceList from "../References/ReferenceList";

type ChatItemProps = {
  text: string;
  vectorReferences?: Array<VectorReference>;
  onTapReference?: (arg0: TextReference | VectorReference) => void;
  isQuestion: boolean;
};

function ChatItem({
  text,
  isQuestion,
  vectorReferences = [],
  onTapReference = () => {},
}: ChatItemProps) {
  const className = `chat-item ${isQuestion ? "question" : "answer"}`;
  const [textReferences, setTextReferences] = useState<Array<TextReference>>(
    []
  );

  useEffect(() => {
    console.log("fetching");
    fetch(`${Session.api_source}/chat-mode/reference_lookup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: text }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        console.log(data.regex_references);
        const textRefs = data.regex_references.map((tref: any) => {
          return tref.begin.map((beg: number, index: number) => {
            return new TextReference(
              beg,
              tref.end[index],
              tref.book,
              tref.paragraph,
              tref.subparagraph,
              tref.name,
              tref.text
            );
          });
        });
        const flattenedRefs = textRefs.flat();
        const sortedRefs = flattenedRefs.sort(
          (a: TextReference, b: TextReference) => a.begin - b.begin
        );
        setTextReferences(sortedRefs);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }, []);

  const clickableText = () => {
    const chars = text.split("");
    let outText: Array<any> = [];
    let lastIndex = 0;
    textReferences.forEach((ref) => {
      outText = [...outText, chars.slice(lastIndex, ref.begin).join("")];
      outText = [
        ...outText,
        <span
          onClick={() => {
            onTapReference(ref);
          }}
          className="text-reference"
        >
          {chars.slice(ref.begin, ref.end).join("")}
        </span>,
      ];

      lastIndex = ref.end;
    });

    outText = [...outText, chars.slice(lastIndex).join("")];

    return outText;
  };

  return (
    <div className={className}>
      {vectorReferences.length > 0 && (
        <ReferenceList
          references={vectorReferences}
          onTapReference={onTapReference}
        />
      )}
      <div className="chat-item-text">
        {clickableText().reduce((prev, curr) => [prev, curr])}
      </div>
    </div>
  );
}

export default ChatItem;
