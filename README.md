# Between Us

A small, private communication space for two people. Built with Next.js, TypeScript and Firebase.

## Features
- Separate four-digit PINs for Francis and Angela, exchanged for Firebase custom-auth tokens on the server.
- Private real-time messaging.
- Optional emotional check-ins.
- Personal journal entries visible only to their author.
- Responsive, calm interface.

## Before deployment

1. **Make this GitHub repository private** before adding any real configuration or using it for personal conversations. The code currently contains no PINs or service-account credentials.
2. Create a Firebase project. Enable Firestore Database.
3. In Firebase Console > Project settings > General > Your apps, create a Web app and copy its API key, auth domain, project ID and app ID.
4. In Firebase Console > Authentication > Sign-in method, enable the **Custom** authentication provider if shown. Custom tokens are minted by the Admin SDK; Firebase Authentication must be enabled.
5. In Project settings > Service accounts, generate a private service-account key. Store its JSON as the single-line value of `FIREBASE_SERVICE_ACCOUNT_JSON` in Vercel. Never commit it or share it.
6. Add the four `NEXT_PUBLIC_FIREBASE_*` variables, plus `FRANCIS_PIN` and `ANGELA_PIN`, to Vercel. Use two different randomly chosen 4-digit PINs and keep them out of chat, source code and screenshots.
7. Deploy the Firestore rules in `firestore.rules` using Firebase Console > Firestore Database > Rules.
8. Deploy to Vercel. Add an edge/WAF rate limit to `POST /api/login` (for example, no more than 8 attempts per IP per 15 minutes). The in-memory throttle is only a lightweight additional guard and is not shared across serverless instances.

## Local development

```bash
npm install
cp .env.example .env.local
npm run dev
```

Fill in the environment variables before testing sign-in. Do not use real PINs in a public repository.

## Security notes
- PINs and the Firebase service account are server-only environment variables. The browser never receives the PIN values.
- Firebase custom tokens authenticate only the fixed participant UIDs `francis` and `angela`; Firestore rules reject all other users.
- Four-digit PINs are inherently low entropy. Keep the repository private, use rate limiting at the edge, and do not reuse either PIN elsewhere.
- Check-ins and messages are visible to both participants. Journal entries are readable only by their author.
- This app is not monitored and is not an emergency alert service. If someone may be in immediate danger, contact local emergency services or a trusted person directly.
