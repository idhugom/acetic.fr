import { SITE } from '../lib/site.js';

export function GET() {
  const body = `User-agent: *
Allow: /

Sitemap: ${SITE.domain}/sitemap-index.xml
`;
  return new Response(body, { headers: { 'Content-Type': 'text/plain' } });
}
