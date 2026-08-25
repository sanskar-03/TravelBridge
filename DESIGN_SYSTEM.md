# TravelBridge Design System & Visual Identity

## 1. Design Philosophy
TravelBridge is a peer-to-peer platform connecting real journeys with real deliveries. The interface must communicate trust, practicality, clarity, and professionalism. 
**Anti-AI Rule:** We do not use generic AI SaaS tropes (neon gradients, floating 3D blobs, "Revolutionize your journey" marketing copy). Everything is built to be useful first.

## 2. Copywriting Rules
* **Short, specific, human.**
* Use "Post your trip" instead of "Unlock seamless trip posting."
* Use "Send a package" instead of "Experience next-generation transportation."

## 3. Color Tokens
* **Primary (Trust/Anchor):** Slate 900 (`#0f172a`)
* **Secondary (Background accents):** Slate 50 (`#f8fafc`)
* **Accent (Action/Highlight):** Orange 600 (`#ea580c`)
* **Background:** Zinc 100 (`#f4f4f5`)
* **Surface:** White (`#ffffff`)
* **Text:** Zinc 900 (Primary), Zinc 500 (Secondary), Zinc 400 (Muted)
* **Status:** Green (Success), Yellow (Warning), Red (Error), Blue (Info)

## 4. Typography
* System fonts (sans-serif) prioritizing readability.
* Clear hierarchy: H1 (Display), H2 (Section), H3 (Card Titles), Body, Small/Muted.

## 5. Spacing & Radius
* **Spacing:** Tailwind default 4-point grid (e.g., p-4 = 1rem, p-6 = 1.5rem).
* **Radius:** Controlled (`sm` for inputs, `md` for buttons, `lg` for cards). No excessive pill shapes unless specific to badges.

## 6. Components
* **Button:** Primary, Secondary, Outline, Ghost, Destructive. Clear hover/focus states.
* **Input:** Standardized with labels, validation rings, and error text states.
* **Card:** Structural container for journeys/requests. Avoid nesting cards inside cards.
* **Badge:** Status indicators that use both color and semantic text for accessibility.

## 7. Accessibility & Responsive
* **Focus States:** Every interactive element has a visible `ring-2 ring-accent` on keyboard focus.
* **Responsive:** Mobile-first grid layouts. Touch targets are a minimum of 40px high (`h-10`).
