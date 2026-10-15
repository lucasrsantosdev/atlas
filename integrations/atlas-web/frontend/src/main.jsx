import React from "react";
import ReactDOM from "react-dom/client";

import AtlasApp from "./AtlasApp";

ReactDOM
  .createRoot(
    document.getElementById("root")
  )
  .render(
    <React.StrictMode>
      <AtlasApp />
    </React.StrictMode>
  );
