class Tag {
  constructor(tag = {}) {
    this.id = tag.id;
    this.label = tag.label;
    this.color = tag.color;
    this.createdAt = tag.createdAt;
    this.usageCount = tag.usageCount ?? 0;
  }
}

class Note {
  constructor(note) {
    this.title = note?.title;
    this.lastModified = note?.lastModified;
    this.createdAt = note?.createdAt;
    this.content = note?.content;
    this.favorite = note?.favorite ?? false;
    this.tags = (note?.tags || []).map((tag) => new Tag(tag));
    this.groupId = note?.groupId ?? null;
    this.groupName = note?.groupName ?? null;
  }

  get lastModifiedAsDate() {
    return new Date(this.lastModified * 1000);
  }

  get lastModifiedAsString() {
    return this.lastModifiedAsDate.toLocaleString();
  }

  get createdAtAsDate() {
    return new Date(this.createdAt * 1000);
  }

  get createdAtAsString() {
    return this.createdAtAsDate.toLocaleString();
  }
}

class SearchResult extends Note {
  constructor(searchResult) {
    super(searchResult);
    this.score = searchResult.score;
    this.titleHighlights = searchResult.titleHighlights;
    this.contentHighlights = searchResult.contentHighlights;
    this.tagMatches = searchResult.tagMatches;
  }

  get uniqueKey() {
    return `${this.groupId || "legacy"}:${this.title}`;
  }

  get titleHighlightsOrTitle() {
    return this.titleHighlights ? this.titleHighlights : this.title;
  }

  get includesHighlights() {
    if (
      this.titleHighlights ||
      this.contentHighlights ||
      (this.tagMatches != null && this.tagMatches.length)
    ) {
      return true;
    } else {
      return false;
    }
  }
}

export { Note, SearchResult, Tag };
