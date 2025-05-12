export default class Session {
  sessionID: string;
  languageIsGerman: Boolean = true;

  constructor(sessionID: string) {
    this.sessionID = sessionID;
  }

  static api_source = process.env.REACT_APP_API_URL ? `${process.env.REACT_APP_API_URL}` : 'http://127.0.0.1:5000';

  // add error handling to these...
  get baseFetchURL(): string {
    return `${Session.api_source}/chat-mode/sessions/${this.sessionID}`;
  }

  get legalTextURL(): string {
    return `${Session.api_source}/chat-mode/sessions/${this.sessionID}/text`;
  }

  get summaryURL(): string {
    return `${Session.api_source}/chat-mode/sessions/${this.sessionID}/summary`;
  }

  get chatURL(): string {
    return `${Session.api_source}/chat-mode/sessions/${this.sessionID}/qa`;
  }

  get referencesURL(): string {
    return `${Session.api_source}/chat-mode/sessions/${this.sessionID}/references`;
  }
}
