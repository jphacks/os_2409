'use client';

import { firebaseConfig } from "@/repository/firebase/config";
import { initializeApp, getApps } from "firebase/app";
import { getFirestore } from "firebase/firestore";
// import { getAuth } from "firebase/auth";
export const firebaseApp = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
// export const auth = getAuth(firebaseApp);
export const db = getFirestore(firebaseApp);