# Security Policy

## Reporting a vulnerability

If you find a security issue in this site, please **do not open a public issue**.
Instead, use GitHub's private **"Report a vulnerability"** button on the repository's
**Security** tab (Security → Advisories), or contact the maintainer through their GitHub profile.

Please include the affected page or file, steps to reproduce, and the impact you expect.
You can expect an acknowledgement within a few days. This is a static portfolio project,
so there is no bug bounty.

## Supported versions

Only the latest commit on `main` is maintained.

## Controls in place

| Area | Control |
|---|---|
| Content Security Policy | Strict policy: everything (including `media-src` for self-hosted video) from `'self'`; no inline scripts or styles, no `eval`, `object-src 'none'`, `base-uri 'self'`, `form-action 'none'` (the consultation form is a mock-up and never submits), `frame-ancestors 'none'` (header only). Delivered as an HTTP header via `_headers`, with a `<meta>` fallback for hosts that can't set headers. |
| Third parties | None. Fonts are self-hosted (SIL OFL), there are no CDNs, analytics, trackers, or third-party scripts, so no visitor data leaks to other origins. If an external resource is ever added, it must use Subresource Integrity (`integrity` + `crossorigin`) and be added to the CSP explicitly. |
| HTTP headers (`_headers`) | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` (camera, microphone, geolocation, payment, USB off), `Strict-Transport-Security`, `Cross-Origin-Opener-Policy`, `Cross-Origin-Resource-Policy`. |
| DOM safety | JavaScript never writes user input or captions with `innerHTML`; it uses `textContent` and DOM nodes. The gallery lightbox only loads same-origin image URLs. No inline event handlers. |
| Form | `maxlength` on every text field, `type="email"` / `type="tel"` with patterns, input trimmed and stripped of control characters, a hidden honeypot field for bots. The form submits nowhere. |
| Links | Outbound links use `rel="noopener noreferrer"`. |
| Repository hygiene | `.gitignore` excludes `.env*`, keys, certificates, and OS/editor files. No secrets or API keys are committed, the contact email is a placeholder, and photos have all EXIF/GPS metadata stripped before they are committed. Videos are re-encoded with all container and stream metadata removed (including QuickTime GPS, device make/model, and creation date) and checked with `ffprobe`. |

## Important limitation

Client-side validation is a usability feature, **not a security control**. Anything that
can be done in the browser can be bypassed. When a real form backend is added, it must:

- re-validate and sanitize every field on the server,
- rate-limit submissions per IP or session,
- use spam protection (honeypot plus a CAPTCHA such as Cloudflare Turnstile or hCaptcha),
- escape or encode data before it is shown anywhere (emails, dashboards),
- store as little personal data as possible, and only over HTTPS.
