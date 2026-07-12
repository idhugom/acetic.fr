// Post-build : transforme dist/top5/{slug}/index.html -> dist/top5/{slug}.htm
// afin de reproduire À L'IDENTIQUE les URLs du site WordPress d'origine
// (https://www.acetic.fr/top5/{slug}.htm) et préserver 100% du référencement.
import { readdir, rename, rm, stat } from 'node:fs/promises';
import { join } from 'node:path';

const dir = 'dist/top5';
let count = 0;

let entries;
try {
  entries = await readdir(dir, { withFileTypes: true });
} catch {
  console.error(`postbuild: ${dir} introuvable`);
  process.exit(1);
}

for (const entry of entries) {
  if (!entry.isDirectory()) continue;
  const slug = entry.name;
  const indexPath = join(dir, slug, 'index.html');
  try {
    await stat(indexPath);
  } catch {
    continue; // pas d'index.html : on ignore
  }
  const target = join(dir, `${slug}.htm`);
  await rename(indexPath, target);
  await rm(join(dir, slug), { recursive: true, force: true });
  count++;
}

console.log(`postbuild: ${count} pages transformées en /top5/{slug}.htm`);
