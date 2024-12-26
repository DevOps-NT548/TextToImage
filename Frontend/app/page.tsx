'use client';
import { useEffect, useState } from "react";
import Navbar from './components/navbar';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Link from "next/link";
import ReactLoading from 'react-loading';
import HOST from "./components/config";

export default function Home() {
    const [loggedIn, setLoggedIn] = useState(false);
    const [loading, setLoading] = useState(false);
    const [generated, setGenerated] = useState(false);
    const [status, setStatus] = useState("");
    const [prompt, setPrompt] = useState("");
    const [imageSrc, setImageSrc] = useState<string | null>(null);

    useEffect(() => {
        fetch("/api")
            .then(res => res.json())
            .then(data => setLoggedIn(data.loggedIn));
    }, []);

    const submitPrompt = async () => {
        if (!prompt.trim()) {
            toast("Prompt cannot be empty");
            return;
        }

        try {
            setLoading(true);
            setGenerated(false);
            setStatus("Generating...");

            const formData = new FormData();
            formData.append("prompt", prompt);

            const response = await fetch(HOST+"/generate", {
                method: "POST",
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob(); // Retrieve the image as a blob
                const imageUrl = URL.createObjectURL(blob); // Generate an object URL for the image
                setImageSrc(imageUrl); // Update state with the image URL
                setLoading(false);
                setGenerated(true);
                setStatus("");
            } else {
                const data = await response.json();
                toast.error(data.detail); // Show error message if request fails
            }
        } catch (err) {
            toast("Internal error, try again");
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex">
            <Navbar />
            <main className="p-4 w-full">
                {loggedIn && (
                    <>
                        <textarea
                            className="w-full h-24 p-4 border border-gray-300 rounded outline-none resize-none text-neutral-700"
                            placeholder="Enter your prompt here..."
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                        />
                        <div className="flex items-center gap-2 mt-2">
                            <button
                                className="bg-sky-400 text-white px-4 py-2 rounded hover:bg-sky-500"
                                onClick={submitPrompt}
                            >
                                Generate
                            </button>
                            <span>{status}</span>
                            {loading && <ReactLoading type="balls" color="#38BDF8" />}
                            {generated && (
                                <Link href="/history" className="hover:text-blue-600 hover:underline px-2">
                                    Generated
                                </Link>
                            )}
                        </div>

                        {imageSrc && (
                            <div className="mt-4">
                                <h3 className="text-lg font-medium">Generated Image:</h3>
                                <img
                                    src={imageSrc}
                                    alt="Generated Output"
                                    className="mt-2 w-full max-w-md rounded shadow-md border border-gray-300"
                                />
                            </div>
                        )}
                    </>
                )}

                <div className="flex gap-8 md:flex-row flex-col mt-8">
                    <div>
                        <h2 className="my-2 text-xl font-semibold">Introduction</h2>
                        <p>This website ensures accurate generations from text to image.</p>
                    </div>
                </div>

                <ToastContainer />
            </main>
        </div>
    );
}
