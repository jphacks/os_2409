"use client";

import { doc, onSnapshot } from "firebase/firestore";
import { db } from "@/repository/frontend/firebase";
import { useEffect, useState } from "react";

type Data = {
  in_room: boolean;
};

export default function Home() {
  const [data, setData] = useState<Data>({
    in_room: false,
  });

  useEffect(() => {
    const docRef = doc(db, "dev", "data");
    const unsub = onSnapshot(docRef, (doc) => {
      const data = doc.data();
      setData(data as Data);
    });

    return unsub;
  }, []);

  useEffect(() => {
    console.log("data", data);
  }, [data]);

  return data.in_room ? (
    <div className="flex justify-center h-screen">
      <div className="text-center my-auto">
        <div className="balloon text-center">
          <p className="text-8xl" style={{ margin: 24 }}>
            おはよう☀️
            <br />
            ぼくがでそう？
          </p>
        </div>
        <h1 className="text-9xl">💩</h1>
      </div>
    </div>
  ) : (
    <div className="h-screen w-screen bg-black" />
  );
}
