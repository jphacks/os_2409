"use client";

import { doc, onSnapshot } from "firebase/firestore";
import { db } from "@/repository/frontend/firebase";
import { useEffect, useState } from "react";
import Image from "next/image";
import BananaUnch from "../../public/banana.png";
import KataiUnch from "../../public/katai.png";
import BishaUnch from "../../public/bisha.png";

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
    // <FirstScreen />
    <ConversationScreen />
  ) : (
    <div className="h-screen w-screen bg-black" />
  );
}

function FirstScreen() {
  return (
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
  );
}

function ConversationScreen() {
  return (
    <div className="flex flex-col justify-center h-screen items-center">
      <div className="text-center my-auto">
        <div className="balloon text-center">
          <p className="text-8xl" style={{ margin: 24 }}>
            もう会えないんだし
            <br />
            ちょっと話そうよ！
          </p>
        </div>
        <h1 className="text-9xl">💩</h1>
      </div>
      <Component />
    </div>
  );
}

// 評価するコンポーネント TODO あとで名前変える
function Component() {
  const [unchType, setUnchType] = useState("");

  useEffect(() => {
    if (!unchType) return;
    fetch("https://editdata-t2l7bkkhbq-dt.a.run.app", {
      method: "POST",
      headers: {
        "Content-Type": "application/json;charset=utf-8",
      },
      body: JSON.stringify({
        unch_type: unchType,
      }),
    });
  }, [unchType]);

  return (
    <div className="flex flex-row justify-center space-x-4 w-4/5 h-1/4 text-center mb-10">
      <button
        className={`flex flex-col bounded-full ${
          unchType === "banana" && "border-solid border-2 border-indigo-600"
        }`}
        onClick={() => setUnchType("banana")}
      >
        <Image src={BananaUnch} alt="バナナうんちの画像" />
        <p className="text-5xl mt-12 mx-auto">バナナ</p>
      </button>
      <button
        className={`flex flex-col bounded-full ${
          unchType === "katai" && "border-solid border-2 border-indigo-600"
        }`}
      >
        <Image
          src={KataiUnch}
          alt="硬いうんちの画像"
          onClick={() => setUnchType("katai")}
        />
        <p className="text-5xl mt-12 mx-auto">カタイ</p>
      </button>
      <button
        className={`flex flex-col bounded-full ${
          unchType === "korokoro" && "border-solid border-2 border-indigo-600"
        }`}
      >
        <Image
          src={BananaUnch}
          alt="コロコロうんちの画像"
          onClick={() => setUnchType("korokoro")}
        />
        <p className="text-5xl mt-12 mx-auto">コロコロ</p>
      </button>
      <button
        className={`flex flex-col bounded-full ${
          unchType === "bisha" && "border-solid border-2 border-indigo-600"
        }`}
      >
        <Image
          src={BishaUnch}
          alt="びしゃびしゃうんちの画像"
          onClick={() => setUnchType("bisha")}
        />
        <p className="text-5xl mx-auto">びしゃびしゃ</p>
      </button>
    </div>
  );
}
