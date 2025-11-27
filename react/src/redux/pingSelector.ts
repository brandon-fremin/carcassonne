
import type { RootState } from "./store";

export const selectPingWs = (state: RootState) => state.websocket.ws;
export const selectPingHttp = (state: RootState) => state.websocket.http;
export const selectPingCassandra = (state: RootState) => state.websocket.cassandra;
export const selectPingLoki = (state: RootState) => state.websocket.loki;
export const selectPingGrafana = (state: RootState) => state.websocket.grafana;
export const selectPingTrain = (state: RootState) => state.websocket.train;
export const selectPingLionel = (state: RootState) => state.websocket.lionel;