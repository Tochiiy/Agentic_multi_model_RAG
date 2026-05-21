// chatSlice.ts line 1 — fix import
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import type { Message, ChatState } from "@/types";
import { API_BASE } from "@/lib/utils";

// ── Async: fetch chat history from backend ────────────────────────
export const fetchChatHistory = createAsyncThunk(
  "chat/fetchHistory",
  async (_, { rejectWithValue }) => {
    try {
      const res = await fetch(`${API_BASE}/api/agent/chat-history`);
      if (!res.ok) return [];
      const data = await res.json();

      // convert backend format → frontend Message format
      
      return (data.messages || []).map((msg: any) => ({
        role: msg.role === "ai" ? "assistant" : "user",
        text: msg.content,
        thinking: msg.thinking || "",
      })) as Message[];
    } catch {
      return rejectWithValue([]);
    }
  }
);

// ── Initial state ─────────────────────────────────────────────────
const initialState: ChatState = {
  messages: [],
  loading: false,
  sessionId: null,
};

// ── Slice ─────────────────────────────────────────────────────────
const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    // Add user message + empty assistant placeholder
    // Called when user hits send
    addUserMessageWithAssistant: (state, action: PayloadAction<string>) => {
      state.messages.push({ role: "user", text: action.payload });
      state.messages.push({ role: "assistant", text: "", thinking: "" });
      state.loading = true;
    },

    // Append one character at a time to last assistant message
    // Used for typewriter streaming effect
    appendToLastAssistant: (state, action: PayloadAction<string>) => {
      const last = state.messages[state.messages.length - 1];
      if (last && last.role === "assistant") {
        last.text += action.payload;
      }
    },

    // Append to thinking section of last assistant message
    appendToAssistantThinking: (state, action: PayloadAction<string>) => {
      const last = state.messages[state.messages.length - 1];
      if (last && last.role === "assistant") {
        last.thinking = (last.thinking || "") + action.payload;
      }
    },

    // Mark streaming as done
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },

    // Clear all messages
    clearMessages: (state) => {
      state.messages = [];
    },

    // Store MCP session ID
    setSessionId: (state, action: PayloadAction<string>) => {
      state.sessionId = action.payload;
    },
  },

  // Handle async fetchChatHistory states
  extraReducers: (builder) => {
    builder
      .addCase(fetchChatHistory.fulfilled, (state, action) => {
        state.messages = action.payload;
      })
      .addCase(fetchChatHistory.rejected, (state) => {
        state.messages = [];
      });
  },
});

export const {
  addUserMessageWithAssistant,
  appendToLastAssistant,
  appendToAssistantThinking,
  setLoading,
  clearMessages,
  setSessionId,
} = chatSlice.actions;

export default chatSlice.reducer;