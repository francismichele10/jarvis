# Between Us

A calm, two-person communication space built with Next.js, TypeScript, Firebase Authentication and Cloud Firestore.

## What is included

- Two separate four-digit PINs, checked on the server.
- Firebase custom-token sign-in with fixed participant accounts: `francis` and `angela`.
- Live shared messages.
- Optional emotional check-ins shared between both participants.
- Personal journal with a saved-entry history. Each person can read only their own entries.
- Responsive layout with a gentle, accessible interface.
- A clear emergency-support reminder. This app is not monitored and cannot send emergency alerts.

## Firebase setup

1. Create a Firebase project at the Firebase Console.
2. Open **Build → Firestore Database** and create a database. Choose a region close to the people who will use the app.
3. Open **Build → Authentication** and click **Get started** so Firebase Authentication is enabled. This app uses Firebase custom tokens minted by the server; you do not need to enable Google or email/password sign-in providers.
4. In **Project settings → General → Your apps**, register a Web app and copy its Firebase configuration values:
   - API key
   - Auth domain
   - Project ID
   - App ID
5. Open **Firestore Database → Rules**, replace the rules with the contents of `firestore.rules` in this repository, and publish them.
6. In **Project settings → Service accounts**, generate a private service-account key. Keep the downloaded JSON private. It will be added to Vercel as a server-only environment variable; never commit it to GitHub or place it in a `NEXT_PUBLIC_*` variable.

## Vercel environment variables

Import this repository into Vercel and add these variables under **Project → Settings → Environment Variables**. Add them to the Production environment (and Preview only if you intend to test previews).

| Variable | Value |
| --- | --- |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | Firebase Web app API key |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | Firebase Web app auth domain |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Firebase project ID |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | Firebase Web app app ID |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Entire service-account JSON, pasted as one line |
| `FRANCIS_PIN` | A unique four-digit PIN for Francis |
| `ANGELA_PIN` | A different four-digit PIN for Angela |

Use two different PINs and do not reuse either PIN elsewhere. Do not send the PINs or service-account JSON in this chat. After adding or changing environment variables, trigger a fresh Vercel deployment.

## Local development

```bash
npm install
cp .env.example .env.local
npm run dev
```

Fill in `.env.local` with test Firebase values before signing in. Keep `.env.local` out of version control.

## Security and operational notes

- PIN values and the Firebase service account are read only by the server. The browser never receives the PIN values.
- The server exchanges a valid PIN for a Firebase custom token. Firestore rules allow only the two fixed participant UIDs.
- Messages and check-ins are shared between both participants. Journal entries are private to their author.
- Four-digit PINs have limited strength. The API includes a lightweight per-instance attempt throttle, but serverless instances do not share that counter. Configure an edge/WAF rate limit for `POST /api/login` (for example, 8 attempts per IP per 15 minutes) before real use.
- The app is not monitored, does not detect suicidal intent, and cannot contact anyone on a person's behalf. If someone may be in immediate danger, contact them directly, involve a trusted person who can be physically present, and call local emergency services.
