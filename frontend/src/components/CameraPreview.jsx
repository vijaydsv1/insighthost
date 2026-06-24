import React, { useEffect, useRef } from "react";

function CameraPreview() {

  const videoRef = useRef(null);

  useEffect(() => {

    const startCamera = async () => {

      try {

        const stream =
          await navigator.mediaDevices.getUserMedia({
            video: true
          });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }

      } catch (err) {

        console.error(
          "Camera Error:",
          err
        );
      }
    };

    startCamera();

  }, []);

  return (

    <div>

      <h3>Camera Preview</h3>

      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        width="400"
      />

    </div>
  );
}

export default CameraPreview;