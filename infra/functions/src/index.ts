/**
 * Import function triggers from their respective submodules:
 *
 * import {onCall} from "firebase-functions/v2/https";
 * import {onDocumentWritten} from "firebase-functions/v2/firestore";
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

import {https, logger} from "firebase-functions/v2";
import {initializeApp} from "firebase-admin/app";
import {getFirestore} from "firebase-admin/firestore";

// Start writing functions
// https://firebase.google.com/docs/functions/typescript

// export const helloWorld = onRequest((request, response) => {
//   logger.info("Hello logs!", {structuredData: true});
//   response.send("Hello from Firebase!");
// });

initializeApp();
const db = getFirestore();

export const editData = https.onRequest({
  region: "asia-northeast2",
}, async (req, res) => {
  res.set("Access-Control-Allow-Headers", "*");
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS, POST");
  try {
    logger.log(req.body);
    await db.doc("dev/data").set(req.body, {merge: true});
    res.status(200).send("edit complete!");
  } catch (e) {
    res.status(500).send(`error ${e}`);
  }
});

export const getData = https.onRequest({
  region: "asia-northeast2",
}, async (req, res) => {
  res.set("Access-Control-Allow-Headers", "*");
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS, POST");
  try {
    const data = await db.doc("dev/data").get();
    res.status(200).send(data);
  } catch (e) {
    res.status(500).send(`error ${e}`);
  }
});
