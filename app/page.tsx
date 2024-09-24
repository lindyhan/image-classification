"use client";

import { useState } from 'react';
import Image from 'next/image';

export default function Home() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [classification, setClassification] = useState<string | null>(null);
  const [animalInfo, setAnimalInfo] = useState<string | null>(null);
  const [isDangerous, setIsDangerous] = useState<boolean | null>(null);

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = async (event) => {
        const imageData = event.target?.result as string;
        setSelectedImage(imageData);

        // Send image to backend for classification
        const response = await fetch('/api/classify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: imageData }),
        });

        const data = await response.json();

        if (data.classification === "No animal detected") {
          setClassification("No animal detected");
          setAnimalInfo(null);
          setIsDangerous(null);
        } else {
          setClassification(data.classification);
          setAnimalInfo(data.animalInfo);
          setIsDangerous(data.isDangerous);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">Animal Image Classification</h1>
      <div className="mb-8">
        <label htmlFor="imageUpload" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded cursor-pointer">
          Upload Image
        </label>
        <input
          id="imageUpload"
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="hidden"
        />
      </div>
      {selectedImage && (
        <div className="mb-8">
          <Image src={selectedImage} alt="Uploaded image" width={300} height={300} />
        </div>
      )}
      {classification && (
        <div className="text-center">
          <h2 className="text-2xl font-semibold mb-4">Classification Result:</h2>
          <p className="text-xl mb-2">{classification}</p>
          {animalInfo && (
            <>
              <p className="mb-2">{animalInfo}</p>
              <p className="font-bold">
                This animal is {isDangerous ? 'dangerous' : 'not dangerous'}.
              </p>
            </>
          )}
        </div>
      )}
    </main>
  );
}