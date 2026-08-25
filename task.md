# Redesign Wedding Invitation Envelope and Main View

## Steps
- [x] 1. Re-write the envelope scene in `index.html` to be a full-bleed 2D layout. The top half should contain the envelope flap and seal. The bottom half should have the "Requests the pleasure of your company" text.
- [x] 2. Completely rewrite `css/envelope.css` to handle this new full-bleed 2D layout. Use `assets/envelope.jpg` as the background for both halves. Remove ALL 3D CSS (perspective, rotateX, backface-visibility).
- [x] 3. Update `js/app.js` to animate the parting transition: clicking the seal makes the top half slide UP (`transform: translateY(-100%)`) and the bottom half slide DOWN (`transform: translateY(100%)`), revealing the invitation beneath.
- [x] 4. Polish `css/invitation.css` to ensure the main invitation looks elegant, using a sage green or warm grey typography to match the reference.
- [x] 5. Refine envelope animation in `app.js` and `envelope.css`. Top slides up, bottom stays and fades, card slides up from pocket.
- [x] 6. Add CSS pulse to wax seal in `envelope.css`.
- [x] 7. Apply Ivory & Gold bespoke theme in `invitation.css` with gold foil effects and increased editorial margins.
- [x] 8. Add premium glassmorphic mobile frame for desktop view in `index.css`.
