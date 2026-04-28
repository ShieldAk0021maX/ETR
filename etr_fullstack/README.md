# Escape The Room Full-Stack Architecture

## Folder Layout
```
etr_fullstack/
  api/
    assets/
      iste_logo.png
      triveni_logo.png
    requirements.txt
    server.py
  web/
    assets/
      iste_logo.png
      triveni_logo.png
    public/
      assets/
        iste_logo.png
        triveni_logo.png
    src/
      components/
        Header.jsx
      App.jsx
      index.css
      main.jsx
    index.html
    package.json
    postcss.config.js
    tailwind.config.js
    vite.config.js
```

## Notes
- Backend is decoupled in `/api` with model loaded once at process start.
- Frontend is decoupled in `/web` and consumes `POST /predict`.
- Logos are copied into both `/api/assets` and `/web/assets` and served in frontend from `/assets`.
