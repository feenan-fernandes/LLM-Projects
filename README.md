# Digital Wedding Invitation

A premium, production-ready React web application for a digital wedding invitation. Built with Vite, React, and Tailwind CSS.

## Features
- **Modern Tech Stack**: React 18, Vite for lightning-fast builds, and Tailwind CSS for styling.
- **Luxury Aesthetic**: High-end editorial design with a warm ivory and muted sage palette, gold foil accents, and elegant typography (`Cormorant Garamond` and `Great Vibes`).
- **Smooth Animations**: Intersectional Observer hooks drive buttery smooth fade-in animations as the user scrolls.
- **Mobile-First Frame**: Designed specifically for a 9:16 mobile aspect ratio, with a gorgeous glassmorphic desktop frame.

## Local Development

To run this project locally, you must have [Node.js](https://nodejs.org/) installed on your machine.

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```
   The site will be available at `http://localhost:5173`.

3. **Build for production**:
   ```bash
   npm run build
   ```
   This will generate a `dist` directory with static assets.

## Deployment

This app is a static site and can be deployed easily for free.

### Netlify
This project includes a `netlify.toml` file.
1. Create a Netlify account and link your GitHub repository, or simply drag and drop the `dist/` folder into Netlify Drop.
2. Build command: `npm run build`
3. Publish directory: `dist`

### Firebase Hosting
This project includes a `firebase.json` file.
1. Install the Firebase CLI: `npm install -g firebase-tools`
2. Login: `firebase login`
3. Initialize (if needed): `firebase init hosting`
4. Deploy: `firebase deploy`
