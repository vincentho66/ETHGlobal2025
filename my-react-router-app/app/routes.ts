import { type RouteConfig, index } from "@react-router/dev/routes";

export default [
    index("routes/home.tsx"),
    { path: "/survey", file: "routes/survey.tsx" },
] satisfies RouteConfig;
