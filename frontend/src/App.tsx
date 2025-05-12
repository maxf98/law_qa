import React, { useState, useEffect, useCallback } from "react";
import "./App.css";
import ChatHistory from "./Chat/ChatHistory";
import Session from "./Session";
import {
  Reference,
  TextReference,
  VectorReference,
  ChatItemReferences,
} from "./References/Reference";
import ReferenceSidebar from "./References/ReferenceSidebar";
import ChatInteractionContainer from "./Chat/ChatInteractionContainer";

function App() {
  // add state variable for awaiting response?
  const [session, setSession] = useState<Session>();
  const [references, setReferences] = useState<Array<ChatItemReferences>>([]);
  const [chat, setChat] = useState<Array<[string, string | null]>>([]);
  const [isAwaitingChatResponse, setAwaitingChatResponse] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("german");

  const [selectedReference, setSelectedReference] = useState<
    TextReference | VectorReference | null
  >(null);

  const [uploadedDocuments, setUploadedDocuments] = useState<Array<File>>([]);
  const [selectedDocument, setSelectedDocument] = useState<File | null>(null);

  useEffect(() => {
    // not sure if this could cause problems...
    // it seems like it sometimes creates a new session when I don't want it to...
    // maybe we should create this manually, e.g. when pressing summarise...
    createSession();
  }, []);

  async function createSession() {
    const response = await fetch(`${Session.api_source}/chat-mode/sessions/`, {
      method: "POST",
    });
    const data = await response.json();
    setSession(new Session(data.session_id));
  }

  const pollChatResponse = useCallback(() => {
    // definitely need some better error handling here...
    if (session?.chatURL !== undefined) {
      setTimeout(async () => {
        const response = await fetch(session.chatURL);
        if (response.status === 200) {
          const data = await response.json();
          setChat(data.q_and_a);
          setAwaitingChatResponse(false);
        } else if (response.status === 404) {
          console.log("qa endpoint not found" + session.chatURL);
          setAwaitingChatResponse(false);
        } else {
          pollChatResponse();
        }
      }, 500);
    } // Poll every 0.5s
  }, [session, setChat]);

  const pollReferencesResponse = useCallback(() => {
    if (session?.referencesURL !== undefined) {
      setTimeout(async () => {
        const response = await fetch(session.referencesURL);
        if (response.status === 200) {
          console.log(response);
          const data = await response.json();
          console.log(data);
          const textRefs = data.regex_references.map((trefs: any) => {
            return trefs.map((tref: any) => {
              return new TextReference(
                tref.begin,
                tref.end,
                tref.book,
                tref.paragraph,
                tref.subparagraph,
                tref.name,
                tref.text
              );
            });
          });

          const vectorRefs = data.vector_references.map((vrefs: any) => {
            return vrefs.map((vref: any) => {
              return new VectorReference(vref.book, vref.paragraph, vref.text);
            });
          });

          let chatItemReferences: Array<ChatItemReferences> = [];
          for (let i = 0; i < textRefs.length; i++) {
            chatItemReferences = [
              ...chatItemReferences,
              new ChatItemReferences(textRefs[i], vectorRefs[i]),
            ];
          }

          setReferences(chatItemReferences);
        } else {
          pollReferencesResponse();
        }
      }, 500); // Poll every 0.5s
    } else {
      alert("There is no session! For whatever reason...");
    }
  }, [session, setReferences]);

  const onSend = useCallback(
    (question: string) => {
      setChat([...chat, [question, null]]);
      setAwaitingChatResponse(true);
      pollChatResponse();
      pollReferencesResponse();
    },
    [chat, setChat, pollChatResponse, pollReferencesResponse]
  );

  function addToDocuments(file: File) {
    setUploadedDocuments([...uploadedDocuments, file]);
    setSelectedDocument(file);
  }

  async function restart() {
    // create a new session from the new qa mode
    // present an alert that you will lose the chat history
    await createSession();
    setChat([]);
    setReferences([]);
    setUploadedDocuments([]);
  }

  const onTapReference = useCallback(
    (ref: TextReference | VectorReference) => {
      if (selectedLanguage == "english") {
        const translatedText = fetch(
          `${Session.api_source}/chat-mode/translate`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ text: ref.text }),
          }
        )
          .then((response) => {
            if (!response.ok) {
              throw new Error("Network response was not ok");
            }
            return response.json();
          })
          .then((data) => {
            setSelectedReference(
              new Reference(ref.book, ref.paragraph, data.text)
            );
          })
          .catch((error) => {
            console.error("Error:", error);
          });
      } else {
        setSelectedReference(ref);
      }
    },
    [selectedLanguage]
  );

  return (
    <div id="root">
      <div id="Header">
        <div>
          <h3>Der Chatbot für das Deutsche Recht</h3>
        </div>

        <div>
          <button
            className={`langButton ${
              selectedLanguage === "german" ? "selected" : ""
            }`}
            onClick={() => setSelectedLanguage("german")}
          >
            🇩🇪
          </button>
          <button
            className={`langButton ${
              selectedLanguage === "english" ? "selected" : ""
            }`}
            onClick={() => setSelectedLanguage("english")}
          >
            🇬🇧
          </button>
        </div>
      </div>

      {session !== undefined && (
        <div className="chatcontainer">
          <ChatHistory
            chat={chat}
            references={references}
            onTapReference={onTapReference}
          />

          <ChatInteractionContainer
            session={session}
            onSend={onSend}
            isDisabled={isAwaitingChatResponse}
            uploadDocument={addToDocuments}
          />
        </div>
      )}

      <div className={`sidebar ${selectedReference === null ? "" : "open"}`}>
        <ReferenceSidebar
          reference={selectedReference}
          closeSidebar={() => {
            setSelectedReference(null);
          }}
          onTapReference={onTapReference}
        />
      </div>

      {/* {selectedDocument !== null ? (
        <FilePreviewModal file={selectedDocument} />
      ) : (
        <div />
      )} */}
    </div>
  );
}

export default App;
