// change all interface exports to type exports
export type Message = {
  role: "user" | "assistant";
  text: string;
  thinking?: string;
};

export type ChatState = {
  messages: Message[];
  loading: boolean;
  sessionId: string | null;
};

export type ChatHistoryResponse = {
  messages: {
    role: "human" | "ai";
    content: string;
    thinking?: string;
  }[];
};

export type StreamEvent = {
  message?: string;
  thinking?: string;
  error?: string;
};