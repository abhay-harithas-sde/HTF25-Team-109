import React, { useState, useRef } from 'react';

const ImageUpload = ({ onImageAnalysis }) => {
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [cameraActive, setCameraActive] = useState(false);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const imageData = e.target.result;
        setPreview(imageData);
      };
      reader.readAsDataURL(file);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
      });
      videoRef.current.srcObject = stream;
      setCameraActive(true);
    } catch (error) {
      alert('Camera access denied or not available');
    }
  };

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    const imageData = canvas.toDataURL('image/jpeg');
    setPreview(imageData);
    
    // Stop camera
    const stream = video.srcObject;
    const tracks = stream.getTracks();
    tracks.forEach(track => track.stop());
    setCameraActive(false);
  };

  const analyzeImage = () => {
    if (preview) {
      onImageAnalysis(preview);
    }
  };

  const resetUpload = () => {
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="image-upload">
      <h2>Upload or Capture Your Meal</h2>
      
      {!preview && !cameraActive && (
        <div className="upload-options">
          <div className="upload-button-container">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              ref={fileInputRef}
              style={{ display: 'none' }}
            />
            <button 
              className="upload-btn"
              onClick={() => fileInputRef.current.click()}
            >
              📁 Choose from Gallery
            </button>
            
            <button 
              className="camera-btn"
              onClick={startCamera}
            >
              📷 Take Photo
            </button>
          </div>
        </div>
      )}

      {cameraActive && (
        <div className="camera-container">
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline
            className="camera-video"
          />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          <div className="camera-controls">
            <button onClick={capturePhoto} className="capture-btn">
              📸 Capture
            </button>
            <button 
              onClick={() => setCameraActive(false)} 
              className="cancel-btn"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {preview && (
        <div className="preview-container">
          <img src={preview} alt="Food preview" className="food-preview" />
          <div className="preview-controls">
            <button onClick={analyzeImage} className="analyze-btn">
              🔍 Analyze Food
            </button>
            <button onClick={resetUpload} className="reset-btn">
              🔄 Try Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;