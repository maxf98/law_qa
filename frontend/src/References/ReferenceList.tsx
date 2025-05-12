import React, { useState } from "react";
import { VectorReference } from "./Reference";
import "./References.css";

type ReferenceListProps = {
  references: Array<VectorReference>;
  onTapReference: (arg0: VectorReference) => void;
};

function ReferenceList({ references, onTapReference }: ReferenceListProps) {
  return (
    <div className="referenceList">
      {references.map((ref, idx, arr) => (
        <button
          type="button"
          key={idx}
          className="referenceItem"
          onClick={() => onTapReference(ref)}
        >
          {ref.label}
        </button>
      ))}
    </div>
  );
}

export default ReferenceList;
