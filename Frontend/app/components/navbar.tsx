
import Link from "next/link"
import { useEffect, useState } from "react"

export default function Navbar() {
    const [loggedIn, setLoggedIn] = useState(false);
    useEffect(() => {
        fetch("/api")
            .then(res => res.json())
            .then(data => setLoggedIn(data.loggedIn))
    }, [])
    const logout = () => {
    fetch("/api", { method: "DELETE" })
        .then(res => res.json())
        .then(data => {
            setLoggedIn(data.loggedIn);
            window.location.href = "/login";
        })
        .catch(err => console.error("Logout failed:", err));
    };

    return (
        <nav className="flex flex-col min-h-screen bg-neutral-50 w-1/4 drop-shadow-xl">
            <h1 className="m-4 text-sky-500">Group20</h1>
            <ul className="h-full">
                <li className="hover:bg-sky-50 p-4 text-lg font-semibold"><Link href="/">Home</Link></li>
                {loggedIn ? <>
                    <li className="hover:bg-sky-50 p-4 text-lg font-semibold"><Link href="/profile">Profile</Link></li>
                    <li className="hover:bg-sky-50 p-4 text-lg font-semibold text-red-600">
                        <a href="/" onClick={(event) => {
                            event.preventDefault(); // Prevent navigation
                            logout();
                        }}>Logout</a>
                    </li>
                </> : <>
                    <li className="hover:bg-sky-50 p-4 text-lg font-semibold"><Link href="/login">Sign in</Link></li>
                </>}
            </ul>
            {!loggedIn && <p className="p-4"><b>Pro tip:</b> You must sign in to use our app</p>}

        </nav>
    )
}