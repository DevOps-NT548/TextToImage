import HOST from "@/app/components/config";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";


// GET handler
export async function GET(req: NextRequest) {
  const usernameCookie = cookies().get("username");

  if (!usernameCookie) {
    return NextResponse.json({ error: "No username cookie found" }, { status: 400 });
  }

  const username = usernameCookie.value;

  try {
    const res = await fetch(`${HOST}/user/${username}`, { method: "POST" });
    if (!res.ok) {
      throw new Error("Failed to fetch user data");
    }
    const data = await res.json();

    return NextResponse.json({ ...data, loggedIn: req.cookies.has("user_id") });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: "Failed to fetch user data" }, { status: 500 });
  }
}

export async function PUT(req: Request) {

  try {
    const body = await req.formData();
    console.log("Received formData:");
    body.forEach((value, key) => {
      console.log(key, value);
    });

    const usernameCookie = cookies().get("username");

    if (!usernameCookie) {
      return NextResponse.json({ error: "No username cookie found" }, { status: 400 });
    }

    const username = usernameCookie.value;

    // Check if avatar file is present
    const avatarFile = body.get("avatar");
    if (avatarFile && avatarFile instanceof Blob) {
      // Convert Blob to Buffer
      const arrayBuffer = await avatarFile.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);
      const base64data = buffer.toString('base64');
      body.set("avatar", `data:${avatarFile.type};base64,${base64data}`);

      const res = await fetch(`${HOST}/updateprofile/${username}`, {
        method: "POST",
        body: body,
      });

      if (!res.ok) {
        throw new Error("Failed to update profile");
      }

      const data = await res.json();
      console.log("Response data:", data);

      return NextResponse.json(data);
    } else {
      const res = await fetch(`${HOST}/updateprofile/${username}`, {
        method: "POST",
        body: body,
      });

      if (!res.ok) {
        throw new Error("Failed to update profile");
      }

      const data = await res.json();
      console.log("Response data:", data);

      return NextResponse.json(data);
    }
  } catch (error) {
    console.error("Error in PUT handler:", error);
    return NextResponse.json({ error: "Failed to update profile" }, { status: 500 });
  }
}