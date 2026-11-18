"use client";

import { useEffect, useState } from "react";
import {
  signInWithCustomToken,
  onAuthStateChanged,
  signOut,
  User,
} from "firebase/auth";
import {
  addDoc,
  collection,
  onSnapshot,
  orderBy,
  query,
  serverTimestamp,
  limit,
  where,
} from "firebase/firestore";
import { auth, db } from "@/lib/firebase";

type Msg = { id: string; text: string; sender: string; createdAt?: { toDate: () => Date } };
type Check = { id: string; feeling: string; note?: string; sender: string; createdAt?: { toDate: () => Date } };
type JournalEntry = { id: string; text: string; sender: string; createdAt?: { toDate: () => Date } };

const feelings = [
  ["😊", "I'm doing okay"],
  ["🙂", "I'm alright"],
  ["😔", "Not feeling great"],
  ["😢", "I need someone to talk to"],
  ["❤️", "Just need company"],
];

function stamp(value?: { toDate: () => Date }) {
  return value?.toDate().toLocaleString([], { dateStyle: "medium", timeStyle: "short" }) ?? "Just now";
}

function person(uid: string, currentUid: string) {
  if (uid === currentUid) return "You";
  return uid === "angela" ? "Angela" : "Francis";
}

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState("chat");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [checks, setChecks] = useState<Check[]>([]);
  const [journalEntries, setJournalEntries] = useState<JournalEntry[]>([]);
  const [text, setText] = useState("");
  const [note, setNote] = useState("");
  const [journal, setJournal] = useState("");

  useEffect(() => onAuthStateChanged(auth, setUser), []);

  useEffect(() => {
    if (!user) return;
    const q = query(collection(db, "messages"), orderBy("createdAt", "asc"), limit(250));
    return onSnapshot(q, (snapshot) => {
      setMessages(snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() } as Msg)));
    }, () => setError("Messages could not be loaded. Please check your connection."));
  }, [user]);

  useEffect(() => {
    if (!user) return;
    const q = query(collection(db, "checkins"), orderBy("createdAt", "desc"), limit(20));
    return onSnapshot(q, (snapshot) => {
      setChecks(snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() } as Check)));
    }, () => setError("Check-ins could not be loaded. Please check your connection."));
  }, [user]);

  useEffect(() => {
    if (!user) return;
    const q = query(
      collection(db, "journal"),
      where("sender", "==", user.uid),
      orderBy("createdAt", "desc"),
      limit(30),
    );
    return onSnapshot(q, (snapshot) => {
      setJournalEntries(snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() } as JournalEntry)));
    }, () => setError("Your private thoughts could not be loaded. Please check your connection."));
  }, [user]);

  async function login(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pin }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Sign-in failed. Please try again.");
      await signInWithCustomToken(auth, data.token);
      setPin("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not sign in. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  async function send(event: React.FormEvent) {
    event.preventDefault();
    if (!text.trim() || !user) return;
    const value = text.trim();
    setText("");
    setError("");
    try {
      await addDoc(collection(db, "messages"), {
        text: value,
        sender: user.uid,
        createdAt: serverTimestamp(),
      });
    } catch {
      setError("Message not sent. Check your connection and Firebase rules.");
      setText(value);
    }
  }

  async function checkIn(feeling: string) {
    if (!user) return;
    setError("");
    setSuccess("");
    try {
      await addDoc(collection(db, "checkins"), {
        feeling,
        note: note.trim(),
        sender: user.uid,
        createdAt: serverTimestamp(),
      });
      setNote("");
      setSuccess("Your check-in has been shared.");
    } catch {
      setError("Check-in not saved. Check your connection and Firebase rules.");
    }
  }

  async function saveJournal(event: React.FormEvent) {
    event.preventDefault();
    if (!user || !journal.trim()) return;
    setError("");
    setSuccess("");
    try {
      await addDoc(collection(db, "journal"), {
        text: journal.trim(),
        sender: user.uid,
        createdAt: serverTimestamp(),
      });
      setJournal("");
      setSuccess("Saved. This entry is visible only to you.");
    } catch {
      setError("Journal entry not saved. Check your connection and Firebase rules.");
    }
  }

  async function lockSpace() {
    setError("");
    setSuccess("");
    await signOut(auth);
    setTab("chat");
  }

  if (!user) {
    return (
      <main className="shell">
        <div className="wrap">
          <header className="top">
            <div className="brand">between <span>us.</span></div>
            <div className="tag">A little space for two</div>
          </header>
          <section className="card login-card">
            <div className="cloud" aria-hidden="true">☁️</div>
            <p className="tag">Just the two of you</p>
            <h1 className="serif-title">A place to be heard.</h1>
            <p className="muted intro">No pressure. No judgement. Just a quiet space to talk, check in and share what’s on your mind.</p>
            <form onSubmit={login} className="login-form">
              <label htmlFor="pin" className="tag pin-label">Enter your private four-digit PIN</label>
              <input
                id="pin"
                className="field pin"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={4}
                pattern="[0-9]{4}"
                value={pin}
                onChange={(event) => setPin(event.target.value.replace(/\D/g, "").slice(0, 4))}
                placeholder="••••"
                aria-label="Four digit PIN"
                required
              />
              <button className="btn full" disabled={busy || pin.length !== 4}>
                {busy ? "Opening your space…" : "Enter our space"}
              </button>
            </form>
            {error && <p className="error" role="alert">{error}</p>}
            <p className="muted login-foot">A small reminder: you deserve care, patience and support.</p>
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className="shell">
      <div className="wrap">
        <header className="top">
          <div>
            <div className="brand">between <span>us.</span></div>
            <div className="muted subtitle">Your little corner of the internet</div>
          </div>
          <button className="btn ghost" onClick={lockSpace}>Lock space</button>
        </header>

        <section className="support-note" aria-label="Important support information">
          <strong>You matter, even on the difficult days.</strong>
          <p>This space is for connection, but it is not monitored and cannot send emergency alerts. If you might hurt yourself or you are in immediate danger, please tell someone you trust who can be with you now. In Ghana, call <a href="tel:112">112</a> for emergency help.</p>
        </section>

        <nav className="tabs" aria-label="Your space">
          <button className={"tab " + (tab === "chat" ? "active" : "")} onClick={() => { setTab("chat"); setError(""); setSuccess(""); }}>💬 Messages</button>
          <button className={"tab " + (tab === "checkin" ? "active" : "")} onClick={() => { setTab("checkin"); setError(""); setSuccess(""); }}>💗 Check-in</button>
          <button className={"tab " + (tab === "journal" ? "active" : "")} onClick={() => { setTab("journal"); setError(""); setSuccess(""); }}>✍️ My thoughts</button>
        </nav>

        {error && <p className="feedback error" role="alert">{error}</p>}
        {success && <p className="feedback success" role="status">{success}</p>}

        {tab === "chat" && (
          <section className="card">
            <h2 className="section-title">A conversation between us</h2>
            <p className="muted section-intro">Say what you need to say. You don’t have to find perfect words.</p>
            <div className="conversation" aria-live="polite">
              {messages.length === 0 ? (
                <p className="empty-state">Your conversation starts with a hello. 🌷</p>
              ) : messages.map((message) => (
                <div key={message.id} className={"message " + (message.sender === user.uid ? "mine" : "")}>
                  <div className="message-author">{person(message.sender, user.uid)}</div>
                  <div>{message.text}</div>
                  <small>{stamp(message.createdAt)}</small>
                </div>
              ))}
            </div>
            <form onSubmit={send} className="send-form">
              <input className="field" value={text} onChange={(event) => setText(event.target.value)} placeholder="Write something kind…" maxLength={3000} aria-label="Write a message" />
              <button className="btn" disabled={!text.trim()}>Send</button>
            </form>
          </section>
        )}

        {tab === "checkin" && (
          <section className="card">
            <h2 className="section-title">How are you, really?</h2>
            <p className="muted section-intro">No explanation needed. Choose what feels closest right now.</p>
            <div className="status">
              {feelings.map(([emoji, label]) => (
                <button key={label} onClick={() => checkIn(emoji + " " + label)}>
                  <span className="feeling-emoji">{emoji}</span>{label}
                </button>
              ))}
            </div>
            <label className="field-label" htmlFor="checkin-note">Add a little context (optional)</label>
            <textarea id="checkin-note" className="field note-field" rows={3} value={note} onChange={(event) => setNote(event.target.value)} placeholder="Anything you'd like the other person to know?" maxLength={1000} />
            <h3 className="subheading">Recent check-ins</h3>
            <div className="list">
              {checks.length === 0 ? <p className="muted">No check-ins yet. You can start whenever you feel ready.</p> : checks.map((check) => (
                <article key={check.id} className="check-card">
                  <strong>{person(check.sender, user.uid)}</strong>
                  <div className="check-feeling">{check.feeling}</div>
                  {check.note && <p className="muted check-note">{check.note}</p>}
                  <small className="muted">{stamp(check.createdAt)}</small>
                </article>
              ))}
            </div>
          </section>
        )}

        {tab === "journal" && (
          <section className="card">
            <h2 className="section-title">A thought for yourself</h2>
            <p className="muted section-intro">This journal is private to the person who writes each entry. The other person cannot read these notes.</p>
            <form onSubmit={saveJournal}>
              <textarea className="field journal-field" rows={6} value={journal} onChange={(event) => setJournal(event.target.value)} placeholder="Write whatever is on your mind…" maxLength={5000} />
              <button className="btn journal-save" disabled={!journal.trim()}>Save my thought</button>
            </form>
            <div className="journal-history">
              <h3 className="subheading">Your saved thoughts</h3>
              {journalEntries.length === 0 ? <p className="muted">Your private notes will appear here after you save one.</p> : journalEntries.map((entry) => (
                <article key={entry.id} className="journal-entry">
                  <p>{entry.text}</p>
                  <small className="muted">{stamp(entry.createdAt)}</small>
                </article>
              ))}
            </div>
          </section>
        )}

        <footer className="muted page-footer">Be gentle with yourself. One moment at a time. ♡</footer>
      </div>
    </main>
  );
}
