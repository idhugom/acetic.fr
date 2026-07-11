// Résout les images d'articles (dans src/assets/posts) vers des ImageMetadata
// pour l'optimisation build-time d'Astro (webp/avif responsive).
const modules = import.meta.glob('../assets/posts/*.{jpg,jpeg,png,webp,avif,JPG,JPEG,PNG}', {
  eager: true,
});

const byFilename = {};
for (const path in modules) {
  const filename = path.split('/').pop();
  byFilename[filename] = modules[path].default;
}

export function postImage(filename) {
  if (!filename) return null;
  return byFilename[filename] || null;
}
