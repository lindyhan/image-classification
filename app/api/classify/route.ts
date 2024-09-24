import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const { image } = await req.json();

  try {
    // Send the image to the FastAPI backend for classification
    const response = await fetch('http://localhost:8000/classify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return NextResponse.json(result);
  } catch (error) {
    console.error('Error classifying image:', error);
    return NextResponse.json({ error: 'Failed to classify image' }, { status: 500 });
  }
}