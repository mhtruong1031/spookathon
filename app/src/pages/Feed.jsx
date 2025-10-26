import { useEffect, useRef, useState } from 'react';
import takePhotoIcon from '../assets/take_photo.png';
import cameraViewIcon from '../assets/camera_view.png';
import backIcon from '../assets/back_button.png';
import { Link } from 'react-router-dom';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import './Feed.css';

function Feed() {
    const videoRef = useRef(null);
    const [shouldFlicker, setShouldFlicker] = useState(false);
    const [showButtons, setShowButtons] = useState(false);
    const [showFlash, setShowFlash] = useState(false);
    const [showLoading, setShowLoading] = useState(false);
    const [showAlert, setShowAlert] = useState(false);
    useEffect(() => {
        const initializeCamera = async () => {
            try {
                const constraints = {
                    video: {
                      facingMode: { ideal: 'environment' },
                      width: { ideal: 1280 },
                      height: { ideal: 720 }
                    },
                    audio: false
                  };
                  
                
                const stream = await navigator.mediaDevices.getUserMedia(constraints);
                
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    
                    // Trigger flicker effect when camera initializes
                    setShouldFlicker(false);
                    setTimeout(() => {
                        setShouldFlicker(true);
                        setTimeout(() => {
                            setShouldFlicker(false);
                            // Show buttons after flicker completes
                            setShowButtons(true);
                        }, 3000);
                    }, 50);
                }
            } catch (error) {
                console.error('Error initializing camera:', error);
            }
        };

        initializeCamera();


    }, []);

    const takePhoto = async () => {
        if (!videoRef.current) return;
        
        // Trigger flash effect
        setShowFlash(true);
        setTimeout(() => {
            setShowFlash(false);
        }, 240);
        
        // Take the photo
        setTimeout(async () => {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = videoRef.current.videoWidth;
            canvas.height = videoRef.current.videoHeight;
            
            // Draw the current video frame onto the canvas
            context.drawImage(videoRef.current, 0, 0);
            
            // Convert canvas to blob
            canvas.toBlob(async (blob) => {
                if (!blob) return;
                
                // Show loading overlay after 300ms
                setTimeout(() => {
                    setShowLoading(true);
                }, 300);
                
                try {
                    // Send to backend
                    const formData = new FormData();
                    formData.append('file', blob, 'photo.png');
                    
                    const response = await fetch('http://localhost:8000/math/explain', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.text();
                    console.log('Analysis result:', result);
                    if (result === "This is not a math problem") {
                        setShowAlert("This is not a math problem");
                    } else {
                        setShowAlert(result);
                    }
                    // Hide loading overlay
                    setShowLoading(false);
                } catch (error) {
                    console.error('Error analyzing image:', error);
                    setShowLoading(false);
                }
            }, 'image/png');
        }, 120);
    };

    return (
        <div className="feed-wrapper">
            {showAlert ? <Alert severity="error" className="alert-overlay" onClose={() => setShowAlert(false)}>{showAlert}</Alert> : <></>}
            <Link to="/"><img src={backIcon} alt="Back" id="back-icon" className={showButtons ? 'fade-in' : ''}/></Link>
            <div id="camera-feed-container">
                <video 
                    ref={videoRef}
                    autoPlay 
                    playsInline 
                    className="background-federal-blue-100"
                >
                    Unable to access camera
                </video>
                <img src={cameraViewIcon} alt="Camera View" id="camera-view-overlay" className={shouldFlicker ? 'flicker' : ''}/>
                {showFlash && <div id="photo-flash"></div>}
                {showLoading && <div id="loading-overlay"></div>}
            </div>
            {showLoading ? <CircularProgress id="loading-spinner" /> : <></>}
            <button onClick={takePhoto} id="take-photo-btn" className={showButtons ? 'fade-in' : ''}>
                <img src={takePhotoIcon} alt="Take Photo" id="take-photo-btn-img"/>
            </button>
        </div>
    );
}

export default Feed;