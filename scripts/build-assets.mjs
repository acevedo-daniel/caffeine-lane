import { cp, mkdir } from "node:fs/promises";

await mkdir("static/dist/js", { recursive: true });
for (const name of ["base.js", "custom-select.js", "home-carousel-controller.mjs", "home-carousel.js", "search-filters.js"]) {
  await cp(`static/src/js/${name}`, `static/dist/js/${name}`);
}
