// gta6-meme-x-01 entry (Node 22, standard library only).
//
// The entry itself is a post on X: an agent-made GTA 6 meme ("Sick Day" —
// after 13 years of waiting, Jason & Lucia take the convertible out on
// launch day, and the make.fun ghost rides in the back seat holding its
// magenta coin). The post is made from a public X account with make.fun
// and the account's play code in its text; POST.json at the repo root
// names the post's address, and the house reads the post from X (its
// first picture, then its text) and hands that to the judge.
//
// All this program does is copy POST.json from the repository into
// /output, where the gate reads it. Nothing it writes is judged.
//
// The POST.json committed here holds a placeholder address, so the gate
// refuses it as it stands (valid 0). Replace it with the real post's
// address before submitting.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const botDir = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outputDir, { recursive: true });
try {
  copyFileSync(join(botDir, "POST.json"), join(outputDir, "POST.json"));
} catch (err) {
  console.error(
    `POST.json could not be copied from ${botDir}: ${(err as Error).message}`,
  );
  process.exit(1);
}
