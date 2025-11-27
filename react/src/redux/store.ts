import { configureStore } from "@reduxjs/toolkit";
import { websocketReducer } from "./pingReducer";
import { useSelector, type TypedUseSelectorHook } from "react-redux";

export const store = configureStore({
  reducer: {
    websocket: websocketReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;