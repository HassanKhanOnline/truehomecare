// Rewrite a live truehomecare.co.uk upload URL to a local /public path.
export function localImg(url: string | undefined | null): string {
  if (!url) return '';
  return url
    .replace('https://www.truehomecare.co.uk', '')
    .replace('https://truehomecare.co.uk', '');
}
