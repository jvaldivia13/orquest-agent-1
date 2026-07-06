# Basic API Frontend Design

## Goal

Provide a minimal browser interface to test the existing `/support/request` API without requiring Swagger, curl, or a separate frontend toolchain.

## Approach

FastAPI will serve static files from `app/static` and return `index.html` at `/`. The frontend will be plain HTML, CSS, and JavaScript. It will post the entered message to `/support/request` and render the returned category, priority, ticket status, ticket id, and response.

## User Flow

1. User opens `http://localhost:8000/`.
2. User writes a support request in a textarea.
3. User submits the form.
4. The page shows loading state while the API responds.
5. The page displays the structured API result or a readable error.

## Files

- `app/api.py`: mount static assets and serve the root page.
- `app/static/index.html`: form and result layout.
- `app/static/styles.css`: responsive basic styling.
- `app/static/app.js`: browser-side API call and rendering.
- `tests/test_api.py`: coverage that `/` serves the frontend.

## Out of Scope

- Authentication.
- A separate React/Vite application.
- Persistent frontend state.
- Production-grade UI design system.
