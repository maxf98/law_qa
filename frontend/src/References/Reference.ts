export class Reference {
  book: string;
  paragraph: string;
  text: string;

  constructor(book: string, paragraph: string, text: string) {
    this.book = book;
    this.paragraph = paragraph;
    this.text = text;
  }

  static copyWithNewText(ref: Reference, text: string): Reference {
    return new Reference(ref.book, ref.paragraph, text);
  }

  get label(): string {
    return this.book + " §" + this.paragraph;
  }

  get fullBookName(): string {
    return this.book;
  }
}

export class TextReference extends Reference {
  begin: number;
  end: number;
  subparagraph: string;
  name: string;

  constructor(
    begin: number,
    end: number,
    book: string,
    paragraph: string,
    subparagraph: string,
    name: string,
    text: string
  ) {
    super(book, paragraph, text);
    this.begin = begin;
    this.end = end;
    this.subparagraph = subparagraph;
    this.name = name;
  }
}

export class VectorReference extends Reference {
  constructor(book: string, paragraph: string, text: string) {
    super(book, paragraph, text);
  }
}

export class ChatItemReferences {
  text_references: Array<TextReference>;
  vector_references: Array<VectorReference>;

  constructor(
    text_references: Array<TextReference>,
    vector_references: Array<VectorReference>
  ) {
    this.text_references = text_references;
    this.vector_references = vector_references;
  }
}
