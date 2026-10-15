import { ATLAS_IDENTITY } from "../../config/identity";

export function AtlasBrand() {

  return (
    <div className="atlas-brand">

      <div className="atlas-orb">
        A
      </div>

      <div>

        <div className="atlas-brand-name">
          {ATLAS_IDENTITY.name}
        </div>

        <div className="atlas-brand-subtitle">
          Inteligencia ao seu lado
        </div>

      </div>

    </div>
  );
}
