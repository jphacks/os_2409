"use client";

import { doc, onSnapshot } from "firebase/firestore";
import { db } from "@/repository/frontend/firebase";
import { useCallback, useEffect, useRef, useState } from "react";
import Image from "next/image";
import BananaUnch from "../../public/banana.png";
import KataiUnch from "../../public/katai.png";
import BishaUnch from "../../public/bisha.png";
import { RealtimeClient } from "@openai/realtime-api-beta";
import { ItemType } from "@openai/realtime-api-beta/dist/lib/client";
import { WavRecorder, WavStreamPlayer } from "../lib/wavtools/index.js";
import { instructions } from "../utils/conversation_config";

type Data = {
  in_room: boolean;
};

type PageType = "screen_save" | "first" | "conversation" | "finish";

export default function Home() {
  const [pageType, setPageType] = useState<PageType>("screen_save");
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
    if (data.in_room) {
      setPageType("first");
    } else {
      setPageType("screen_save");
    }
  }, [data.in_room]);

  let timer: NodeJS.Timeout;
  useEffect(() => {
    clearTimeout(timer);
    if (pageType === "first") {
      timer = setTimeout(() => setPageType("conversation"), 10 * 1000);
    }
    if (pageType === "conversation") {
      timer = setTimeout(() => setPageType("finish"), 5 * 60 * 1000);
    }
  }, [pageType, setPageType]);

  const screenBuilder = () => {
    switch (pageType) {
      case "screen_save":
        return <div className="h-screen w-screen bg-black" />;
      case "first":
        return <FirstScreen />;
      case "conversation":
        return <ConversationScreen />;
      case "finish":
        return <FinishScreen />;
    }
  };

  return screenBuilder();
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

function FinishScreen() {
  return (
    <div className="flex justify-center h-screen">
      <div className="text-center my-auto">
        <div className="balloon text-center">
          <p className="text-8xl" style={{ margin: 24 }}>
            ちょっとトイレしすぎだよ！！
            <br />
            また今度会おう👋
          </p>
        </div>
        <h1 className="text-9xl">💩</h1>
      </div>
    </div>
  );
}

function ConversationScreen() {
  const [items, setItems] = useState<ItemType[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const wavRecorderRef = useRef<WavRecorder>(
    new WavRecorder({ sampleRate: 24000 })
  );
  const wavStreamPlayerRef = useRef<WavStreamPlayer>(
    new WavStreamPlayer({ sampleRate: 24000 })
  );
  const clientRef = useRef<RealtimeClient>(
    new RealtimeClient({
      apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY,
      dangerouslyAllowAPIKeyInBrowser: true,
    })
  );

  useEffect(() => {
    console.log(items);
  }, [items]);

  const connectConversation = useCallback(async () => {
    const client = clientRef.current;
    const wavRecorder = wavRecorderRef.current;
    const wavStreamPlayer = wavStreamPlayerRef.current;

    setIsConnected(true);
    setItems(client.conversation.getItems());

    // Connect to microphone
    await wavRecorder.begin();

    // Connect to audio output
    await wavStreamPlayer.connect();

    // Connect to realtime API
    await client.connect();
    client.sendUserMessageContent([
      {
        type: `input_text`,
        text: `こんにちは!`,
        // text: `For testing purposes, I want you to list ten car brands. Number each item, e.g. "one (or whatever number you are one): the item name".`
      },
    ]);
  }, []);

  /**
   * Disconnect and reset conversation state
   */
  const disconnectConversation = useCallback(async () => {
    setIsConnected(false);
    setItems([]);

    const client = clientRef.current;
    client.disconnect();

    const wavRecorder = wavRecorderRef.current;
    await wavRecorder.end();

    const wavStreamPlayer = wavStreamPlayerRef.current;
    await wavStreamPlayer.interrupt();
  }, []);

  /**
   * In push-to-talk mode, start recording
   * .appendInputAudio() for each sample
   */
  const startRecording = async () => {
    setIsRecording(true);
    const client = clientRef.current;
    const wavRecorder = wavRecorderRef.current;
    const wavStreamPlayer = wavStreamPlayerRef.current;
    const trackSampleOffset = await wavStreamPlayer.interrupt();
    if (trackSampleOffset?.trackId) {
      const { trackId, offset } = trackSampleOffset;
      await client.cancelResponse(trackId, offset);
    }
    await wavRecorder.record((data) => client.appendInputAudio(data.mono));
  };

  /**
   * In push-to-talk mode, stop recording
   */
  const stopRecording = async () => {
    setIsRecording(false);
    const client = clientRef.current;
    const wavRecorder = wavRecorderRef.current;
    await wavRecorder.pause();
    client.createResponse();
  };

  /**
   * Core RealtimeClient and audio capture setup
   * Set all of our instructions, tools, events and more
   */
  useEffect(() => {
    // Get refs
    const wavStreamPlayer = wavStreamPlayerRef.current;
    const client = clientRef.current;

    // Set instructions
    client.updateSession({ instructions: instructions });
    // Set transcription, otherwise we don't get user transcriptions back
    client.updateSession({ input_audio_transcription: { model: "whisper-1" } });

    client.on("error", (event: any) => console.error(event));
    client.on("conversation.interrupted", async () => {
      const trackSampleOffset = await wavStreamPlayer.interrupt();
      if (trackSampleOffset?.trackId) {
        const { trackId, offset } = trackSampleOffset;
        await client.cancelResponse(trackId, offset);
      }
    });
    client.on("conversation.updated", async ({ item, delta }: any) => {
      const items = client.conversation.getItems();
      if (delta?.audio) {
        wavStreamPlayer.add16BitPCM(delta.audio, item.id);
      }
      if (item.status === "completed" && item.formatted.audio?.length) {
        const wavFile = await WavRecorder.decode(
          item.formatted.audio,
          24000,
          24000
        );
        item.formatted.file = wavFile;
      }
      setItems(items);
    });

    setItems(client.conversation.getItems());

    return () => {
      // cleanup; resets to defaults
      client.reset();
    };
  }, []);

  const assistantItems = items.filter((item) => item.role === "assistant");

  return (
    <div className="flex flex-col justify-center h-screen items-center">
      <div className="text-center mx-10">
        <div className="balloon text-center">
          <div style={{ margin: 24 }}>
            {assistantItems.length !== 0 ? (
              <p className="text-4xl">
                {assistantItems[assistantItems.length - 1].formatted.transcript}
              </p>
            ) : (
              <p className="text-8xl">
                もう会えないんだし
                <br />
                ちょっと話そうよ！
              </p>
            )}
          </div>
        </div>
        <h1 className="text-9xl">💩</h1>
      </div>
      <div className="mb-12">
        {isConnected && (
          <button
            className={`rounded-full text-white px-8 py-4 font-bold mr-4 ${
              isRecording ? "bg-red-300" : "bg-blue-300"
            }`}
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
          >
            push to talk
          </button>
        )}
        <button
          className="bg-blue-300 rounded-full text-white px-8 py-4 font-bold"
          onClick={() =>
            isConnected ? disconnectConversation() : connectConversation()
          }
        >
          {isConnected ? "会話を終える" : "会話する"}
        </button>
      </div>
      <div className="h-10" />
      <RatingBar />
    </div>
  );
}

// うんちタイプを選択するコンポーネント
function RatingBar() {
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
    <div className="flex flex-row justify-center space-x-4 w-4/5 h-1/4 text-center mb-5">
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
