YatraPath App Summary
Evidence-based one-page summary generated from the
repository. Scope is limited to code, templates, settings,
dependencies, and routes found in the repo.
What It Is
YatraPath is a Django web app for discovering temples across
India, viewing them on interactive maps, reading journey-related
blog posts, and planning multi-stop temple routes. The UI is
styled with Tailwind CSS and uses Leaflet-based mapping in the
browser.
Who It's For
Primary persona: spiritual travelers or pilgrims who want to
browse temple destinations, inspect temple details, see locations
on a map, and plan routes between selected temples.
What It Does- Shows a home page with featured temples and a map-driven
exploration entry point.- Stores temple records with name, location, description, image,
latitude/longitude, and visit status.- Lists temples and provides per-temple detail pages with
images and descriptions.- Displays map markers for all temples, with marker color based
on status: completed, planned, or not visited.- Publishes blog posts with title, content, optional image, and
created date.- Includes a route planner where users select multiple temples
and generate a driving route.
How to Run
1. Create/activate a Python virtualenv.
2. Install backend deps: pip install -r
requirements.txt.
3. Install frontend deps: npm install.
4. Build Tailwind CSS: npm run build (this script watches and
writes core/static/css/output.css).
5. Apply DB migrations: python manage.py migrate.
6. Start dev server: python manage.py runserver.
Seed/sample-data import steps: Not found in repo. Temple and
blog content can be managed through Django models/admin
once data exists.
How It Works- Routing layer: yathrapath/urls.py sends root traffic to
core.urls; core/urls.py exposes home, temples, temple
detail, map, blog, blog detail/create, and route-planner pages.- Server layer: function-based Django views in
core/views.py query models and render templates under
core/templates/core/.- Data layer: SQLite (db.sqlite3) stores Temple and Blog
records defined in core/models.py; uploaded images are
served from media/.- Presentation layer: Tailwind input CSS in
core/static/src/input.css is compiled to
core/static/css/output.css; shared layout lives in
base.html.- Map flow: templates load Leaflet in the browser, request
OpenStreetMap tiles, and place markers from
Django-provided temple data.- Route-planner flow: the browser sends selected temple
coordinates directly to the OpenRouteService directions API
and renders the returned polyline, distances, and durations on
the map.- Background jobs, APIs beyond mapping/routing, auth flows,
and deployment config: Not found in repo
