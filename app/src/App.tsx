import { vaerktoejer } from "./tools";
export function App() {
  return (
    <main style={{ fontFamily: "system-ui", maxWidth: 800, margin: "2rem auto", padding: "0 1rem" }}>
      <h1>Byggeværktøjer</h1>
      <p>Fiktiv demo. Alle data og regler er opdigtede og må ikke bruges fagligt.</p>
      {vaerktoejer.length === 0 ? <p>Ingen værktøjer endnu.</p> :
        <ul>{vaerktoejer.map((v) => <li key={v.id}><b>{v.navn}</b>: {v.beskrivelse}</li>)}</ul>}
    </main>
  );
}
