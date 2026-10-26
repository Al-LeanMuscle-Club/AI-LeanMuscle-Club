# Homepage cover

`club-cover.png` is the shared cover for the Chinese and English READMEs. It is an original AI-generated still life, not a member photo. Keep the title and participation links in Markdown so they stay readable, selectable, and accessible on mobile.

- Tool: built-in `imagegen`, new image generation, opaque background.
- Format: PNG, 2172 × 724 pixels.
- Compression: `pngquant 2.17.0`, 80-color palette quantization with dithering (`--strip --speed 1`); original dimensions and composition retained. Palette quantization is lossy.
- File size: 478,426 bytes, down from 1,914,686 bytes (24.99% of the original; 75.01% smaller).
- Direction: warm neutral sports editorial photography with a restrained cobalt accent; no text or logos.

## Generation prompt

```text
Create one original premium editorial still-life image for the GitHub homepage of AI LeanMuscle Club, a friendly community of AI researchers who work and exercise. A very wide panoramic cover, approximately 3:1 aspect ratio, ideally 1536 x 512. Calm sophisticated sports magazine photography, physically believable materials and proportions, warmly lit pale off-white plaster studio backdrop and seamless tabletop. A carefully balanced simple grouping of exactly three objects: an unbranded slim silver aluminum laptop open at a natural angle, a textured muted copper-orange basketball, and a single compact matte graphite dumbbell. The laptop screen has a subtle abstract cobalt-blue graph/node visualization, with no characters or numbers. Include only a small restrained cobalt accent, warm neutrals and graphite elsewhere. Soft directional daylight from upper left, elegant natural shadows, gentle film-like texture, refined tactile surfaces. Central two thirds contain the objects, generous whitespace at both ends and above, enough breathing room to remain clear in a small mobile banner. The laptop and exercise objects feel equally important, thoughtful composition, welcoming and quietly energetic, not a product advertisement. Do not add any other props. No people, hands, logos, branding, letters, text, captions, numerals, interface text, watermark, QR codes or frame. No neon, dramatic black background, busy gradients, sci-fi holograms, or bodybuilding imagery. The image will sit above a separate accessible Markdown title. Deliver the finished image.
```

The existing `club-poster.png` is a separate community poster.
