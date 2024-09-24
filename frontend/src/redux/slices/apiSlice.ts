// Or from '@reduxjs/toolkit/query' if not using the auto-generated hooks
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const ENV = process.env.NODE_ENV;
const baseUrl = ENV == "production" ? "/api/" : "http://localhost:8000/";

// initialize an empty api service that we'll inject endpoints into later as needed
export const apiSlice = createApi({
  baseQuery: fetchBaseQuery({ baseUrl }),
  endpoints: () => ({}),
});

export const apiSliceReducer = apiSlice.reducer;
export const apiSliceMiddleware = apiSlice.middleware;
