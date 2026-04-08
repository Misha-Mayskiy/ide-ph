import { useState } from "react";

import type { Profile } from "../../types/ide";

interface ProfilesPanelProps {
  profiles: Profile[];
  selectedId: string | null;
  onCreate: (name: string) => Promise<void>;
  onOpen: (profileId: string) => Promise<void>;
  onUpdate: (profileId: string, name: string) => Promise<void>;
  onDelete: (profileId: string) => Promise<void>;
}

export function ProfilesPanel({
  profiles,
  selectedId,
  onCreate,
  onOpen,
  onUpdate,
  onDelete
}: ProfilesPanelProps) {
  const [newName, setNewName] = useState("My profile");

  return (
    <section className="card profiles-card">
      <h2>Profiles</h2>
      <div className="row">
        <input value={newName} onChange={(event) => setNewName(event.target.value)} placeholder="Profile name" />
        <button type="button" onClick={() => onCreate(newName)}>
          Save Current
        </button>
      </div>

      <ul className="profiles-list">
        {profiles.map((profile) => (
          <li key={profile.id} className={profile.id === selectedId ? "active" : ""}>
            <span>{profile.name}</span>
            <div className="row">
              <button type="button" onClick={() => onOpen(profile.id)}>
                Open
              </button>
              <button type="button" onClick={() => onUpdate(profile.id, `${profile.name}*`)}>
                Update
              </button>
              <button type="button" onClick={() => onDelete(profile.id)}>
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
