import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export type PingType = "WAIT" | "OK" | "FAIL";

export interface PingState {
    http: PingType;
    ws: PingType;
    cassandra: PingType;
    loki: PingType;
    grafana: PingType;
    train: PingType;
    lionel: PingType;
}

type PartialPingState = Partial<PingState>;

const websocketSlice = createSlice({
    name: 'websocket',
    initialState: {
        http: "WAIT",
        ws: "WAIT",
        cassandra: "WAIT",
        loki: "WAIT",
        grafana: "WAIT",
        train: "WAIT",
        lionel: "WAIT"
    },
    reducers: {
        setPingState: (state, action: PayloadAction<PartialPingState>) => {
            state.http = action.payload.http ?? state.http;
            state.ws = action.payload.ws ?? state.ws;
            state.cassandra = action.payload.cassandra ?? state.cassandra;
            state.loki = action.payload.loki ?? state.loki;
            state.grafana = action.payload.grafana ?? state.grafana;
            state.train = action.payload.train ?? state.train;
            state.lionel = action.payload.lionel ?? state.lionel;
        },
    },
});

export const { setPingState } = websocketSlice.actions;
export const websocketReducer = websocketSlice.reducer;