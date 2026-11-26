import { describe, it, expect } from "vitest";
import { vaerktoejer } from "./index";
describe("værktøjsregister", () => {
  it("har unikke id'er", () => {
    const ids = vaerktoejer.map((v) => v.id);
    expect(new Set(ids).size).toBe(ids.length);
  });
});
