import React, { useEffect, useState } from "react";
import { TextReference, VectorReference } from "./Reference";
import Session from "../Session";

type ReferenceSidebarProps = {
  reference: TextReference | VectorReference | null;
  closeSidebar: () => void;
  onTapReference: (any0: TextReference | VectorReference) => void;
};

function ReferenceSidebar({
  reference,
  closeSidebar,
  onTapReference,
}: ReferenceSidebarProps) {
  const [textReferences, setTextReferences] = useState<Array<TextReference>>(
    []
  );
  const [text, setText] = useState();

  useEffect(() => {
    if (reference !== null) {
      fetch(`${Session.api_source}/chat-mode/reference_lookup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: reference?.text, book: reference?.book }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
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
    }
  }, [reference]);

  const clickableText = () => {
    const chars = reference?.text.replace(/\/n/g, "\n\n").split("") ?? [""];
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
    <div id="referenceSidebar">
      {reference !== null && (
        <div>
          <div className="sidebarHeader">
            <button className="closeButton" onClick={closeSidebar}>
              &times;
            </button>
          </div>
          <h3>{reference.label}</h3>
          <p className="pre-wrap">
            {clickableText().reduce((prev, curr) => [prev, curr])}
          </p>
        </div>
      )}
    </div>
  );
}

export default ReferenceSidebar;
