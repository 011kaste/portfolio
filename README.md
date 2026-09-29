# Alessandro Castellani · Portfolio

Static site, served with GitHub Pages at https://011kaste.github.io/portfolio/

- `index.html`: the page. Interactive interview scene, then the portfolio as a scrollable book with a section index, zoom, arrow-key navigation and contacts.
- `assets/portfolio.pdf`: the full portfolio PDF, offered as a download in the book view.
- `pages/sm/` and `pages/lg/`: one image per PDF page (p01 cover, p02 to p38 spreads, p40 back; p39 is a blank endpaper and is left out), in two sizes for responsive loading.
- `assets/*.jpg`: the idle frame and the three speaking frames
- Contacts: the phone on the table (click it, press `C`, or the C hint). Edit the `contacts` array at the top of the script in `index.html`.
- `assets/nokia.png` (optional): a transparent photo of the phone. If present it replaces the drawn one on the table automatically.
- `assets/favicon.svg`: tab icon

Deep links: `#portfolio` opens the book, `#pigro`, `#nikon`, `#chiaromonte` and the other section slugs in `index.html` open it at that section.

To update the portfolio: replace `assets/portfolio.pdf`, then re-export the page images into `pages/` (spreads 2807×993 as `lg`, half size as `sm`, WebP) and adjust the `SECTIONS` table in `index.html` if the page order changed.

To publish: Settings → Pages → Source "Deploy from a branch", branch `main`, folder `/ (root)`.
