# Fox & Fable · Website (Interior Design Version)

> This repository is a copy of the Fox & Fable site, the starting point for an interior-design-focused version.
> It is a separate mock-up; the original site lives in `cschlawin/fox-and-fable`.

A hand-coded, responsive three-page site for **Fox & Fable**, Jessica's home and lifestyle brand from the
Greater Salt Lake Area, Utah: room tours, favorite finds, design tips and everyday home moments, in her own voice.
*Come on in, make yourself at home.*

> **Status:** design mockup. The shop, journal, newsletter, Pinterest/TikTok handles, media kit and contact email are
> placeholders, and the "Work with me" and newsletter forms validate in the browser but do not send anything.

## Editing and building (Pages CMS + Jekyll)

> Branch `cms-editable`. The site is now a small **Jekyll** site so Jessica can edit it in
> **[Pages CMS](https://pagescms.org)** (free, open source). Her plain-English guide is
> [`docs/EDITING-GUIDE.md`](docs/EDITING-GUIDE.md). Everything here uses free features only: Pages CMS, GitHub
> Actions and GitHub Pages. No paid services, no secrets.

**Where the content lives**

| What | File | Edited in Pages CMS as |
|---|---|---|
| Home page text, buttons, featured rooms, form choices | `_data/home.yml` | Home page |
| Room Tours filters, videos, photo tours (+ extra photos) | `_data/room_tours.yml` | Room tours |
| Shop cards | `_data/shop.yml` | Shop |
| Journal posts (one Markdown file each) | `_journal/*.md` | Journal posts |
| About page story, family captions, "What I share" | `_data/about.yml` | About page |
| Instagram / Pinterest / TikTok … | `_data/social.yml` | Social links |
| Work-with-me band (About + Room Tours) | `_data/call_to_action.yml` | Work-with-me band |
| Footer text and contact email | `_data/settings.yml` | Footer & contact |
| Page titles, descriptions, share text | `_data/seo.yml` | Page titles & share text |
| Uploaded photos / videos | `uploads/`, `uploads/videos/` | Media |
| Photo sizes (generated, don't edit) | `_data/image_sizes.yml` | (hidden) |

The editor itself is configured in `.pages.yml`. Templates are in `_layouts/` and `_includes/`; `index.html`,
`gallery.html` and `about.html` are now Liquid templates that read the files above. The rendered HTML is the same as
the hand-coded version.

**Not editable in the CMS (on purpose):** the `<head>` (CSP, `noindex`), page structure and nav, the logo and About
page watermark art, icons, the About family photos (fixed in `about.html` with their blur), the contact form's labels
and validation messages (`js/main.js`), the lightbox, and new filter categories (add the key to the `room_type`
select in `.pages.yml` and a filter in `_data/room_tours.yml`).

**Build model.** One workflow, `.github/workflows/site.yml`, on every push to `main`:

1. **media** (`contents: write`): `tools/media/process_uploads.py` processes new or changed photos in `uploads/`.
   It applies the phone's rotation, **strips all EXIF/GPS/XMP metadata**, converts to **sRGB**, caps the long edge
   at **2000 px**, converts HEIC to JPEG (and updates references), and writes a `.webp` copy plus
   `-card-480`/`-card-960` thumbnails. It refreshes `_data/image_sizes.yml`, then commits back with the built-in
   `GITHUB_TOKEN` (no secrets). A commit made with `GITHUB_TOKEN` does not start another run, so there is no loop.
   `uploads/.processed.json` records what was already done.
2. **build** (`contents: read`): `actions/jekyll-build-pages` (the same `github-pages` gem as GitHub's classic build),
   then a check that every page still has `noindex` and `form-action 'none'`.
3. **deploy** (`pages: write`, `id-token: write`): `actions/deploy-pages`.

Pushes to other branches only run the build, as a check. This needs **Settings → Pages → Source: GitHub Actions**.
The classic "Deploy from a branch" mode can't be used, because GitHub doesn't rebuild Pages for commits pushed with
`GITHUB_TOKEN`, so processed photos would never go live.

**Build locally** (same gem versions as the Action):

```bash
gem install bundler
bundle install                       # once (add BUNDLE_PATH=vendor/bundle to keep gems in the repo folder; it's git-ignored)
bundle exec jekyll serve             # http://localhost:4000, rebuilds on save
bundle exec jekyll build             # writes _site/
pip install pillow pillow-heif && python3 tools/media/process_uploads.py   # optional: same photo step as the Action
```

`README.md`, `SECURITY.md`, `LICENSE`, `docs/`, `tools/`, `Gemfile` and `.pages.yml` are excluded from the published site.

## Pages

| Page | What's on it |
|---|---|
| `index.html` | Hello from Jessica (hero), a little about me, room tours (four featured rooms), Shop my home (placeholder cards), journal (placeholder post ideas), follow along + newsletter sign-up (preview only), Work with me contact form (preview only) |
| `about.html` | "Meet the Designer" (HTML/CSS version of Cody's graphic: framed portrait, logo with Design + Construction, verbatim bio, signature), three family photos, what she shares, Work with me CTA |
| `gallery.html` | Room tours: three self-hosted finished-room videos (color-drenched pantry walkthrough, pale blue walk-in closet reveal, his & hers closet) and fifteen photo projects. Sets show finished photos, "Design" renderings where they exist, and "Before" photos. Category filters (All / Closets & Storage / Bedrooms / Living Spaces / Offices & Flex Rooms / Laundry Rooms / Pantries / Playrooms) and an accessible `<dialog>` lightbox |

## Features

- **FF monogram logo** (October 2026). The originals live in `docs/brand-reference/`: the primary lockup
  (`fox-and-fable-logo-original.png`) and the brand sheet (`fox-and-fable-brand-sheet.png`). `tools/build-logo-assets.py`
  builds the web assets into `assets/logo/`: the full lockup (WebP + PNG, 520/1040 `srcset`, on the
  artwork's own paper with a matching `#F0ECE5` card), the FF + fox monogram for the nav (1x/2x/3x, keyed to
  transparency) beside the live-text wordmark, the horizontal light lockup from the brand sheet for the charcoal footer
  (keyed off its olive panel so there's no box edge), plus the favicon
  set (`favicon.ico`, `favicon-32.png`, `apple-touch-icon.png`, `icon-192.png`, `icon-512.png`) and the 1200×630
  Open Graph image. The engraved artwork stays raster; it would not survive a vector trace. Earlier logos are kept as
  `docs/brand-reference/previous-*`. In this interior design version, the footer lockup (`horizontal-light-*`) and
  `og-image.png` were edited by hand to drop the logo's "Design + Construction" descriptor line; re-running the
  logo script restores that line, so re-apply the edit afterwards.
- **About page "Meet the Designer" art.** That section deliberately keeps the full logo *with* "Design + Construction"
  (`assets/logo/lockup-descriptor-400/800`) plus a faded FF-and-fox monogram watermark (`monogram-watermark-560.webp`);
  both come from the original artwork via `tools/build-about-logo.py`, which leaves the other logo files alone. The faint
  fox line sketch (`assets/images/about/meet-fox-sketch`) has no source file of its own, so it was copied from Cody's
  "Meet the Designer" graphic with `tools/extract-meet-fox.py` (the graphic is not stored in the repo). Script headings
  use *Allison* (SIL OFL, self-hosted).
- **Shared header and footer** on every page, with `aria-current="page"` on the active link.
- **Mobile navigation** with an accessible toggle (`aria-expanded`; it closes on link click, on Escape, and on resize).
- **Client-side form validation** (Work with me form and newsletter) with friendly inline messages, a live character counter, and a preview-only success state.
- **Gallery filters and lightbox.** Progressive enhancement: without JS, every project shows and each link opens the full image.
- **Self-hosted project videos** (WebM/VP9 + MP4/H.264) that play inline with native controls. Nothing autoplays, and `preload="none"` means no video bytes load until the visitor presses play.
- **SEO**: a per-page title and description, canonical URLs, Open Graph and Twitter tags, `robots.txt`, and `sitemap.xml`.
- **Security hardening**: a strict CSP, security headers, and no third-party requests (see [Security](#security)).

## Tech stack

Plain **HTML5, CSS3, and vanilla JavaScript**, assembled by **Jekyll** (GitHub Pages' built-in generator) from the
content files in `_data/` and `_journal/`. No frameworks or runtime dependencies; the browser gets static files.

```
site/
├── index.html, about.html, gallery.html
├── css/styles.css            # Mobile-first stylesheet based on design tokens
├── js/main.js                # Nav, form validation, gallery filters + lightbox
├── assets/
│   ├── logo/                 # Generated logo assets (full lockup, footer horizontal lockup, nav monogram), WebP + PNG
│   ├── favicon.ico, favicon-32.png, apple-touch-icon.png, icon-192.png, icon-512.png, og-image.png
│   ├── fonts/                # Self-hosted Cormorant Garamond, Inter + Allison script (woff2) + OFL licenses
│   ├── video/                # Self-hosted MP4 (H.264/AAC) + WebM (VP9/Opus) pairs, metadata stripped
│   └── images/
│       ├── placeholders/     # landscape / portrait / square placeholder art
│       ├── about/            # Jessica's portrait (jessica.*) and family photos (family.*, family-snow.*, family-summer.*)
│       ├── home/             # Home page hero crops
│       └── gallery/          # video posters + project photos
├── tools/build-logo-assets.py # Rebuilds every logo/icon asset from the original (needs: pip install pillow numpy scipy)
├── tools/build-about-logo.py  # About-page lockup (with descriptor) + monogram watermark only
├── tools/extract-meet-fox.py  # About-page fox sketch, cut from the Meet the Designer graphic
├── docs/                     # brand-reference/ holds the logo artwork and brand sheet (plus previous logos)
├── _headers, robots.txt, sitemap.xml, site.webmanifest
└── README.md, SECURITY.md, LICENSE
```

## Design decisions

- **The palette comes from the original branding-iron logo** (kept through the October 2026 logo change). Charcoal ink, parchment, oak, and wrought iron. Soft sage and blush
  macaron accents appear only in illustrations and small details.

  | Token | Hex | Use | Contrast |
  |---|---|---|---|
  | `--c-ink` | `#2B2A28` | Text, dark bands | 12.4:1 on parchment, 11.2:1 on parchment-2 |
  | `--c-iron` | `#4A4A48` | Secondary text | 7.7:1 on parchment, 7.0:1 on parchment-2, 5.6:1 on oak band |
  | `--c-parchment` | `#F3EEE4` | Page background, text on charcoal | 12.4:1 on ink |
  | `--c-parchment-2` | `#EAE3D6` | Alternate bands | |
  | `--c-paper` | `#FBF8F2` | Cards, inputs | |
  | `--c-oak` | `#B07A45` | Rules, borders, decorative accents (non-text only) | 3.2:1 on parchment |
  | `--c-oak-deep` | `#8A5A2E` | Accent text (eyebrows, links) | 5.1:1 on parchment, 4.6:1 on parchment-2, 5.5:1 on paper |
  | `--c-oak-dark` | `#6E5034` | Accent text on the oak-grain band | 4.7–5.3:1 |
  | `--c-oak-light` | `#D9B48A` | Accent text on charcoal | 7.4:1 on ink, 8.6:1 on ink-deep |
  | `--c-on-dark` | `#CFC8BC` | Body text on charcoal | 8.6:1 on ink, 10:1 on ink-deep, 7.0:1 on ink-soft cards |

- **Textures are CSS gradients only.** That covers the parchment wash, the oak grain (`--tex-wood`), and the brushed-iron
  bands. They need no image requests, so the CSP stays strict.
- **Typography.** *Cormorant Garamond* for headings and the spaced-caps wordmark (close to the logo's serif wordmark, with the `&` picked out in the accent color) and
  *Inter* for body text and the spaced-caps eyebrows (an echo of the logo's spaced-caps tagline). Each eyebrow gets a short rule
  like the one under the logo's descriptor.
- **Editorial, image-first layout.** Large finished-room photography, generous white space, serif headings, and short copy about how a room feels.
- **Honest content.** There are no invented testimonials, stats, awards, projects, or bios. Every slot is labeled as a placeholder.

## Accessibility notes

- Semantic landmarks, one `h1` per page, a logical heading order, and a skip link on every page.
- Visible `:focus-visible` outlines, and tap targets of 44px or more.
- Meaningful SVGs have a `role="img"` and `<title>`. Decorative SVGs are `aria-hidden`. Every photo has `alt` text
  (placeholders say they are placeholders).
- Form labels, `aria-describedby` errors, `aria-invalid`, a live status region, and focus moved to the first error.
- Gallery filters are toggle buttons (`aria-pressed`) with a polite live region announcing the result count.
- The lightbox uses a native modal `<dialog>`, so focus is trapped by the browser. **Esc** closes it, **← / →** navigate,
  and focus returns to the thumbnail that opened it.
- `prefers-reduced-motion` turns off smooth scrolling, transitions, and hover lifts.

## Run locally

```bash
bundle exec jekyll serve          # then open http://localhost:4000 (see "Editing and building" above)
npx html-validate _site/*.html _site/journal/*.html   # optional HTML check, after a build
```

## Adding photos

> **Since the move to Jekyll, the easy way is Pages CMS** (see [`docs/EDITING-GUIDE.md`](docs/EDITING-GUIDE.md)).
> Photos uploaded there are cleaned up automatically. The notes below are the by-hand method. The HTML snippets
> show what the templates output: add a project by editing `_data/room_tours.yml` rather than `gallery.html`, and
> run `python3 tools/media/process_uploads.py --sizes-only` after adding files under `assets/images/` so their
> `width`/`height` are known.

### Privacy first: strip metadata

Phone photos carry **EXIF metadata, including GPS coordinates of where they were taken** (often your home).
This repository is public, so strip metadata from every photo, especially photos of people, before committing:

```bash
exiftool -all= -overwrite_original photo.jpg          # https://exiftool.org
# or with ImageMagick:
magick photo.jpg -strip -resize "1600x1600>" -quality 82 photo.jpg
```

Double-check with `exiftool photo.jpg` (it should show no GPS, camera, or date fields).

### About page (`about.html`)

| Slot | Drop the file at | Aspect | Suggested size |
|---|---|---|---|
| Jessica's portrait | `assets/images/about/jessica.webp` (+ `.jpg`) | 4:5 portrait | 640 × 800 |

Then, in `about.html`:

1. Use `<picture>` with a WebP `<source>` and a JPEG fallback.
2. Update `width`/`height` to the real pixel size. This prevents layout shift.
3. Write a real description in `alt`, e.g. `alt="Jessica in a finished living room"`.
4. Replace the `[bracketed]` role placeholder.

### Adding gallery photos (`gallery.html`)

1. Export the photo at about **1600px on the long edge** as **WebP** (or JPEG), strip the metadata (see above), and save it as
   `assets/images/gallery/<project-slug>.webp`.
2. Copy one `<figure class="gallery-item">` block in `gallery.html` and edit it:

   ```html
   <figure class="gallery-item photo ratio-landscape" data-category="living-spaces">
     <a class="gallery-link" href="assets/images/gallery/project-slug.webp">
       <img src="assets/images/gallery/project-slug.webp" width="1600" height="1200"
            loading="lazy" decoding="async"
            alt="Describe the finished room: palette, materials, lighting and key pieces">
     </a>
     <figcaption><span class="gallery-cat">Living Spaces</span> <span class="gallery-meta">Living room · [Design summary] · [City, ST]</span></figcaption>
   </figure>
   ```

   - `data-category` is one or more of `closets`, `bedrooms`, `living-spaces`, `offices`, `laundry`, `pantries`, `playrooms`, separated by spaces. These drive the filter buttons. Add a filter button only when a project uses it.
   - `ratio-landscape` (4:3), `ratio-portrait` (4:5), `ratio-square` (1:1), or `ratio-reel` (9:16, for vertical phone video) sets the frame shape.
   - The link `href` is what the lightbox shows. Keep it a local file (the lightbox only accepts same-origin URLs).
   - Write descriptive `alt` text: what's in the room, not "photo of project".
   - The gallery shows finished rooms. Captions describe design choices (palette, materials, mood) in the format `Room · Design summary · Location`.
3. Ask clients for permission before publishing photos of their home, and never include names or street addresses.

**Multi-photo projects.** To give a project extra photos, add a hidden set after its cover link. The lightbox cycles
through the set with ← / → and shows "2 / 3". Add `data-label="Before"` to a slide and the indicator reads "3 / 3 · Before" (any label works, e.g. `data-label="Design"` for a rendering):

```html
<div class="gallery-set" hidden>
  <a href="assets/images/gallery/project-2.webp" data-width="1320" data-height="864" data-alt="Describe photo 2">Photo 2</a>
  <a href="assets/images/gallery/project-before.webp" data-width="1200" data-height="1600" data-label="Before" data-alt="Before: …">Before</a>
</div>
```

For a **video** card (no cover link), give the set an `id` and add `<button class="before-btn" type="button" data-before-set="that-id">See the before (2 photos)</button>`
to the caption. The button opens the lightbox on just that set, and focus returns to it on close (see His & her closets).
The grid card always shows only the finished photo or video. Before shots appear only in the lightbox.

### Adding project videos

Videos are self-hosted in `assets/video/` (the CSP allows `media-src 'self'` only, so there are no YouTube or Instagram embeds).
They play inline and **never open in the lightbox**: the lightbox only picks up items with a `.gallery-link`.

**1. Transcode and strip metadata.** Phone video stores **GPS coordinates** (`com.apple.quicktime.location.ISO6709`),
the device model, and the creation date. Remove all of them:

```bash
# MP4 / H.264 + AAC, long edge 1080px, streamable (+faststart). ffmpeg applies the phone's rotation automatically.
ffmpeg -i input.mov -map 0:v:0 -map 0:a:0 -map_metadata -1 -map_metadata:s:v -1 -map_metadata:s:a -1 -map_chapters -1 \
  -vf "scale='if(gt(iw,ih),1080,-2)':'if(gt(iw,ih),-2,1080)',format=yuv420p" \
  -c:v libx264 -preset slow -crf 25 -profile:v high -c:a aac -b:a 96k \
  -movflags +faststart -fflags +bitexact -flags:v +bitexact -flags:a +bitexact project.mp4
# WebM / VP9 + Opus (smaller in Chrome/Firefox/Edge)
ffmpeg -i input.mov -map 0:v:0 -map 0:a:0 -map_metadata -1 -map_chapters -1 \
  -vf "scale='if(gt(iw,ih),1080,-2)':'if(gt(iw,ih),-2,1080)'" \
  -c:v libvpx-vp9 -crf 34 -b:v 0 -row-mt 1 -c:a libopus -b:a 80k project.webm
# Poster: one sharp frame
ffmpeg -ss 4.8 -i project.mp4 -frames:v 1 -map_metadata -1 project-poster.jpg
# Verify: this should print nothing
ffprobe -v error -show_entries format_tags:stream_tags -of compact project.mp4 | grep -iE 'location|ISO6709|make|model|creation'
```

**2. Add the markup** (copy the pantry walkthrough item in `gallery.html`):

```html
<figure class="gallery-item photo ratio-reel video-item" data-category="closets">
  <video class="gallery-video" controls preload="none" playsinline width="608" height="1080"
         poster="assets/images/gallery/project-poster.webp"
         aria-label="Video: [room] [design summary], designed by Fox &amp; Fable">
    <source src="assets/video/project.webm" type="video/webm">
    <source src="assets/video/project.mp4" type="video/mp4">
    <track kind="captions" src="assets/video/project.en.vtt" srclang="en" label="English">
  </video>
  <figcaption>…</figcaption>
</figure>
```

- Don't add `autoplay` or force `muted`. Visitors start playback and control the sound themselves.
- **Captions.** If a video has speech or meaningful sound, add a WebVTT file next to it (`assets/video/<name>.en.vtt`) and
  the `<track>` line above. Same-origin `.vtt` files work under the current CSP. A starter file:
  ```
  WEBVTT

  00:00:00.000 --> 00:00:04.000
  [Describe the speech or sound]
  ```
  The pantry video has no captions file yet. The exact `<track>` line for it is in the HTML comment above its item in `gallery.html`.

The gallery shows **finished rooms only** (videos should be finished-room walkthroughs or reveals).

**Current videos** (all 608 × 1080 portrait, `controls preload="none" playsinline`, no autoplay):

| File (`assets/video/`) | Where | Notes |
|---|---|---|
| `custom-pantry` | Gallery | Color-drenched pantry walkthrough, 9.7 s |
| `closet-reveal` | Gallery | Pale blue walk-in closet, empty → finished reveal, 32.2 s |
| `his-her-closets` | Gallery | Finished his & hers walk-in closet, 12.6 s |

**Privacy.** Never put children's names in captions, alt text, file names, or commits. Before publishing, check the frames
for name signs or decals, house numbers, readable family photos, and faces.

## Deploy to GitHub Pages

1. Create a repository (for example `fox-and-fable-design`) and push:
   ```bash
   git remote add origin https://github.com/<your-username>/fox-and-fable-design.git
   git push -u origin main
   ```
2. On GitHub, open **Settings → Pages → Build and deployment** and set **Source** to **GitHub Actions**
   (the workflow in `.github/workflows/site.yml` builds and publishes on every push to `main`).
3. Check **Enforce HTTPS**.
4. The site goes live at `https://<your-username>.github.io/fox-and-fable-design/`.
5. Before launch, set `canonical_base` in `_config.yml` (used for `canonical`, `og:url` and `og:image`), plus `robots.txt` and `sitemap.xml`, to the real domain.

## Security

| Control | Where |
|---|---|
| **Strict Content-Security-Policy**: `default-src 'self'`; scripts, styles, fonts, images, and media (video/audio) only from `'self'` (plus `data:` images); `object-src 'none'`; `base-uri 'self'`; `form-action 'none'` (the form is a mock-up and can never submit); `frame-ancestors 'none'`; `upgrade-insecure-requests` | `_headers` (HTTP) + `<meta http-equiv>` fallback in every page |
| **No inline JS or event handlers.** All behavior lives in `js/main.js`, so there's no `'unsafe-inline'` | all pages |
| **Zero third-party requests.** Fonts are self-hosted and there are no CDNs, analytics, or trackers. Any future external resource must use Subresource Integrity + `crossorigin` | `assets/fonts/` |
| **Security headers**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` (camera, microphone, geolocation… off), `Strict-Transport-Security`, COOP/CORP | `_headers` |
| **Safe DOM updates.** User input and captions are written with `textContent`, never `innerHTML`. The lightbox only loads same-origin image URLs | `js/main.js` |
| **Form hardening**: `maxlength` on every field, email types and patterns, trimming and control-character stripping, a hidden honeypot | `index.html`, `js/main.js` |
| **`rel="noopener noreferrer"`** on outbound links | all pages |
| **Repo hygiene and privacy**: `.gitignore` blocks `.env*`, keys, and OS files. No secrets are committed. Photo and video metadata (EXIF, QuickTime GPS, device, and dates) is stripped | `.gitignore`, `assets/images/`, `assets/video/` |
| **Disclosure policy** | `SECURITY.md` |

**Hosting notes.** Netlify and Cloudflare Pages read `_headers` automatically. **GitHub Pages cannot set custom
headers**, so there the `<meta>` CSP and referrer policy are the fallback (`frame-ancestors` and `X-Frame-Options`
don't work from a meta tag). Enable **Enforce HTTPS**, or put the site behind Cloudflare for full header support.

**The forms are mock-ups on purpose.** Neither the "Work with me" form nor the newsletter sign-up has an `action`, the CSP sets `form-action 'none'`, and `main.js` blocks submit and only shows a "preview, nothing was sent" note. No fetch/XHR is made.

**Client-side validation is not security.** A real submission must go through a backend or form service (Formspree,
Netlify Forms, or a serverless function) with **server-side validation and sanitization, rate limiting, and spam protection**
(honeypot plus a CAPTCHA such as Turnstile or hCaptcha), over HTTPS only. When it's added, allow its endpoint in the CSP's
`form-action` / `connect-src`.

## Maintenance notes

- The header and footer are shared Jekyll includes (`_includes/header.html`, `_includes/footer.html`). After changing
  `css/styles.css` or `js/main.js`, bump `asset_version` in `_config.yml` so browsers fetch the new file.
- To change the logo, replace the files in `docs/brand-reference/` and run `python3 tools/build-logo-assets.py`
  (adjust the crop boxes at the top of the script if the layout changed). The old badge generator `tools/build-logo.py`
  and its SVGs were retired in the October 2026 rebrand.

## Roadmap

- More finished-room photography (responsive `srcset`, AVIF/WebP).
- After the mock-up / business-design phase, decide whether and how the forms should deliver messages and newsletter sign-ups (they intentionally send nothing today).
- Individual project case-study pages linked from the gallery.
- WebVTT captions for the videos, and privacy policy and terms pages.
- `LocalBusiness` structured data (JSON-LD in an external file), plus Lighthouse and axe checks in CI.

## License

Code is released under the [MIT License](LICENSE) © 2026 Cody Schlawin. The fonts are licensed separately under the
SIL Open Font License (`assets/fonts/OFL-*.txt`). The Fox & Fable name, logo, and photographs are **not** covered by the
MIT license; all rights are reserved.
