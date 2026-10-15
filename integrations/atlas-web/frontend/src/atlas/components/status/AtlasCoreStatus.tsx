import {
  useEffect,
  useState
} from "react";

import { atlasApi } from "../../services/atlasApi";

type Status =
  | "loading"
  | "online"
  | "offline";

export function AtlasCoreStatus() {

  const [status, setStatus] =
    useState<Status>("loading");

  useEffect(() => {

    atlasApi
      .health()

      .then((health: any) => {

        const valid =
          health?.name === "Atlas" &&
          health?.core === "atlas.core.app.Atlas";

        setStatus(
          valid
            ? "online"
            : "offline"
        );
      })

      .catch(() =>
        setStatus("offline")
      );

  }, []);

  return (
    <div className={`atlas-core-status ${status}`}>

      <span className="atlas-status-dot" />

      {status === "loading" &&
        "Conectando ao Atlas Core"}

      {status === "online" &&
        "Atlas Core online"}

      {status === "offline" &&
        "Atlas Core indisponivel"}

    </div>
  );
}
