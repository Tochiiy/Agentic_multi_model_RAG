import { configureStore } from "@reduxjs/toolkit";
import { useDispatch, useSelector } from "react-redux";
import chatReducer from "./chatSlice";

// ── Redux store ───────────────────────────────────────────────────
export const store = configureStore({
  reducer: {
    chat: chatReducer,
  },
});

// ── TypeScript types ──────────────────────────────────────────────
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// ── Typed hooks ───────────────────────────────────────────────────
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector = <T>(selector: (state: RootState) => T) =>
  useSelector(selector);