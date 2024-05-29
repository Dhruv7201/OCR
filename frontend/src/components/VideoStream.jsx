import React, { useEffect, useRef } from "react";

const VideoStream = ({
  videoConstraints,
  videoRef,
  canvasRef,
  sendFrameToBackend,
}) => {
  const streamRef = useRef(null);

  useEffect(() => {
    const startVideo = async () => {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: videoConstraints,
          });
          videoRef.current.srcObject = stream;
          videoRef.current.onloadedmetadata = () => {
            videoRef.current.play();
          };
          streamRef.current = stream;
        } catch (error) {
          console.error("Error accessing webcam:", error);
        }
      } else {
        console.error(
          "navigator.mediaDevices.getUserMedia is not supported in this browser."
        );
      }
    };

    startVideo();

    const captureInterval = setInterval(sendFrameToBackend, 2000);

    return () => {
      clearInterval(captureInterval);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, [sendFrameToBackend, videoConstraints, videoRef]);

  return (
    <div>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        width={videoConstraints.width}
        height={videoConstraints.height}
      />
      <canvas ref={canvasRef} style={{ display: "none" }} />
    </div>
  );
};

export default VideoStream;
