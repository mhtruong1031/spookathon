import { useEffect, useRef, useState } from 'react';
import takePhotoIcon from '../assets/take_photo.png';
import cameraViewIcon from '../assets/camera_view.png';
import backIcon from '../assets/back_button.png';
import { Link } from 'react-router-dom';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Skeleton from '@mui/material/Skeleton';
import ReactKatex from '@matejmazur/react-katex';
import 'katex/dist/katex.min.css';
import './Feed.css';

function Feed() {
    const videoRef = useRef(null);
    const textOutputRef = useRef(null);
    const [shouldFlicker, setShouldFlicker] = useState(false);
    const [showButtons, setShowButtons] = useState(false);
    const [showFlash, setShowFlash] = useState(false);
    const [showLoading, setShowLoading] = useState(false);
    const [showAlert, setShowAlert] = useState(false);
    const [textOutput, setTextOutput] = useState('');

  // Function to parse text and render LaTeX expressions and markdown
  const parseTextWithLatex = (text) => {
    if (!text) return null;

    console.log('DEBUG Frontend: Raw text received:', text); // Debug: show raw text

    // Clean up literal \n characters and normalize whitespace
    text = text.replace(/\\n/g, ' ');
    
    // Clean up excessive line breaks and normalize spacing
    text = text.replace(/\n\s*\n\s*\n+/g, ' '); // Replace multiple line breaks with space
    text = text.replace(/\n\s+/g, ' '); // Replace line breaks followed by spaces with single space
    text = text.replace(/\s+\n/g, ' '); // Replace spaces followed by line breaks with single space
    text = text.replace(/\n/g, ' '); // Replace all remaining line breaks with spaces
    text = text.replace(/\s+/g, ' '); // Replace multiple spaces with single space
    
    console.log('DEBUG Frontend: Cleaned text:', text); // Debug: show cleaned text
    
    // Match LaTeX expressions - be more precise
    const latexRegex = /\$\$([^$]+?)\$\$|\$([^$]+?)\$/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = latexRegex.exec(text)) !== null) {
      console.log('DEBUG Frontend: Found LaTeX match:', match[0]); // Debug: show LaTeX match
      
      // Add text before the LaTeX expression
      if (match.index > lastIndex) {
        const textBefore = text.slice(lastIndex, match.index);
        if (textBefore.trim()) {
          parts.push({
            type: 'text',
            content: textBefore
          });
        }
      }

      // Determine the type of mathematical expression
      let latexContent, isBlock;
      if (match[1]) {
        // $$...$$ block
        latexContent = match[1].trim()
          .replace(/\\\\/g, '\\') // Fix double backslashes to single
          .replace(/\\newline/g, '') // Remove \newline in display mode
          .replace(/\\n/g, '') // Remove literal \n
          .replace(/\s+/g, ' '); // Normalize spaces
        isBlock = true;
      } else if (match[2]) {
        // $...$ inline
        latexContent = match[2].trim()
          .replace(/\\\\/g, '\\') // Fix double backslashes to single
          .replace(/\\newline/g, '') // Remove \newline in inline mode
          .replace(/\\n/g, '') // Remove literal \n
          .replace(/\s+/g, ' '); // Normalize spaces
        isBlock = false;
      }
      
      console.log('DEBUG Frontend: Processed LaTeX:', latexContent, 'isBlock:', isBlock); // Debug: show processed LaTeX
      
      parts.push({
        type: 'latex',
        content: latexContent,
        isBlock: isBlock
      });

      lastIndex = match.index + match[0].length;
    }

        // Add remaining text after the last LaTeX expression
        if (lastIndex < text.length) {
            const remainingText = text.slice(lastIndex);
            if (remainingText.trim()) {
                parts.push({
                    type: 'text',
                    content: remainingText
                });
            }
        }

        return parts;
    };

    // Function to parse markdown formatting in text
    const parseMarkdown = (text) => {
        if (!text) return text;

        // Handle bold text **text**
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Handle italic text *text* (but not if it's part of **text**)
        text = text.replace(/(?<!\*)\*([^*]+?)\*(?!\*)/g, '<em>$1</em>');
        
        // Handle headers #### text
        text = text.replace(/^#### (.*$)/gm, '<h4>$1</h4>');
        text = text.replace(/^### (.*$)/gm, '<h3>$1</h3>');
        text = text.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        text = text.replace(/^# (.*$)/gm, '<h1>$1</h1>');
        
        // Handle bullet points - simplified
        text = text.replace(/^\* (.*$)/gm, '<li>$1</li>');
        text = text.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        // Wrap in paragraph tags
        if (!text.startsWith('<')) {
            text = '<p>' + text + '</p>';
        }

        return text;
    };

    // Function to render parsed text parts with MathJax
    const renderParsedText = (parts) => {
        if (!parts || parts.length === 0) return null;

        // Group consecutive text parts to minimize fragmentation
        const groupedParts = [];
        let currentText = '';
        let currentIndex = 0;

        for (let i = 0; i < parts.length; i++) {
            const part = parts[i];
            
            if (part.type === 'text') {
                currentText += part.content;
            } else {
                // If we have accumulated text, add it as a group
                if (currentText.trim()) {
                    groupedParts.push({
                        type: 'text',
                        content: currentText,
                        index: currentIndex++
                    });
                    currentText = '';
                }
                
                // Add the LaTeX part
                groupedParts.push({
                    ...part,
                    index: currentIndex++
                });
            }
        }

        // Add any remaining text
        if (currentText.trim()) {
            groupedParts.push({
                type: 'text',
                content: currentText,
                index: currentIndex++
            });
        }

        return (
            <>
                {groupedParts.map((part) => {
                    if (part.type === 'text') {
                        // Parse markdown in text parts
                        const markdownContent = parseMarkdown(part.content);
                        return (
                            <span 
                                key={part.index} 
                                dangerouslySetInnerHTML={{ __html: markdownContent }}
                            />
                        );
                    } else if (part.type === 'latex') {
                        console.log('DEBUG Frontend: Rendering LaTeX:', part.content, 'isBlock:', part.isBlock); // Debug: show what's being rendered
                        try {
                            if (part.isBlock) {
                                return (
                                    <div key={part.index} style={{ margin: '10px 0', textAlign: 'center' }}>
                                        <ReactKatex math={part.content} block />
                                    </div>
                                );
                            } else {
                                return <ReactKatex key={part.index} math={part.content} />;
                            }
                        } catch (error) {
                            console.error('LaTeX rendering error:', error, 'Content:', part.content);
                            return <span key={part.index} style={{ color: 'red' }}>${part.content}$</span>;
                        }
                    }
                    return null;
                })}
            </>
        );
    };

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

    // Ensure text output stays visible
    useEffect(() => {
        if (textOutputRef.current && textOutput) {
            textOutputRef.current.style.opacity = '1';
            textOutputRef.current.style.animation = 'none';
            // Force reflow
            textOutputRef.current.offsetHeight;
            textOutputRef.current.style.animation = 'textSlideIn 0.4s ease-out';
        }
    }, [textOutput]);

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
                        setTextOutput('');
                    } else {
                        setTextOutput(result);
                        setShowAlert(false);
                    }
                    // Hide loading overlay
                    setShowLoading(false);
                } catch (error) {
                    console.error('Error analyzing image:', error);
                    setShowLoading(false);
                    setTextOutput('');
                }
            }, 'image/png');
        }, 120);
    };

    return (
        <div className="feed-wrapper">
            {showAlert ? <Alert severity="error" className="alert-overlay" onClose={() => setShowAlert(false)}>{showAlert}</Alert> : <></>}
            {!showLoading && !showAlert && textOutput && (
                <div 
                    ref={textOutputRef}
                    className="text-output-overlay" 
                    onAnimationEnd={() => console.log('Text output animation ended')}
                    style={{ opacity: 1 }}
                >
                    <button className="close-text-output" onClick={() => setTextOutput('')}>×</button>
                    <div className="text-content">
                        {renderParsedText(parseTextWithLatex(textOutput))}
                    </div>
                </div>
            )}
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