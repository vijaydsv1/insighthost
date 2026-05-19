import React, { useState, useEffect, useRef } from 'react';

const BrightSoftwareHost = () => {
  const [status, setStatus] = useState('SYSTEM_OFFLINE');
  const [chat, setChat] = useState([]);
  const [interimText, setInterimText] = useState('');
  const [isWaked, setIsWaked] = useState(false);
  const [mediaActive, setMediaActive] = useState(false);

  const stopFlagRef = useRef(false);
  const recognitionRef = useRef(null);
  const isActiveRef = useRef(true); 
  const isConversingRef = useRef(false);
  const isAISpeakingRef = useRef(false);
  const mediaActiveRef = useRef(false); 
  const socketRef = useRef(null);
  const videoRef = useRef(null); 

  const isMutedBySystemRef = useRef(false);
  const lastSpeechEndTimeRef = useRef(0);

  const synthRef = window.speechSynthesis || {
    getVoices: () => [],
    speak: () => {},
    cancel: () => {}
  };

  const chatEndRef = useRef(null);
  const ACCION_RED = "#E31E24";
  const GLOW_CYAN = "#00FFFF";

  const cleanResponseText = (text = "") => text
    .replace(/\s*\[Source\s*\d+\]/gi, "")
    .replace(/\s+/g, " ")
    .trim();

  const CATEGORY_DATA = [
    { name: 'Our services' },
    { name: 'our global talent base' },
    { name: 'our solutions accelerators and services' },
    { name: 'talent at accion' },
    { name: 'awards' },
    { name: 'partnerships and alliances' }
  ];

  const isChatVisible = chat.length > 0 || interimText.length > 0;

  useEffect(() => {
    const connectWebSocket = () => {
      if (socketRef.current && (socketRef.current.readyState === WebSocket.OPEN || socketRef.current.readyState === WebSocket.CONNECTING)) {
        return;
      }
      const socket = new WebSocket('ws://localhost:8000/api/ws');
      socket.onopen = () => {
        console.log("✅ WebSocket Connected");
        if (isWaked) setStatus(isConversingRef.current ? 'LISTENING' : 'STANDBY (Say Namaste)');
      };
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.answer) {
          const hasVideos = data.videos && data.videos.length > 0;
          
          const botMessage = {
            role: "assistant",
            // 🔥 Suppress text content completely if video payloads are sent back
            content: hasVideos ? "" : cleanResponseText(data.answer),
            images: data.images || [],
            videos: data.videos || [],
            links: data.links || []
          };
          setChat(prev => [...prev, botMessage]);
          if (botMessage.content) speak(botMessage.content);
        }
      };
      socket.onclose = () => { setTimeout(connectWebSocket, 3000); };
      socketRef.current = socket;
    };
    if (isWaked) {
      connectWebSocket();
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.close(1000, "Component Unmounted");
        socketRef.current = null;
      }
    };
  }, [isWaked]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat, interimText]);

  const safeStart = () => {
    if (!recognitionRef.current || !isActiveRef.current) return;
    try { 
      recognitionRef.current.start(); 
    } catch (e) {}
  };

  const stopEverything = () => {
    console.log("🛑 HARD STOP TRIGGERED");
    stopFlagRef.current = true;
    isAISpeakingRef.current = false;
    isMutedBySystemRef.current = false;
    lastSpeechEndTimeRef.current = Date.now();

    window.speechSynthesis.cancel();
    
    if (videoRef.current) {
      videoRef.current.pause();
    }
    
    mediaActiveRef.current = false;
    setMediaActive(false);

    setStatus('LISTENING (Ask your next question)');
    setInterimText('');
    
    setTimeout(() => {
      stopFlagRef.current = false;
      safeStart();
    }, 300);
  };

  const resumeVideo = () => {
    if (videoRef.current) {
      videoRef.current.play();
      setStatus('VIDEO PLAYING (Listening for STOP)');
      speak("Resuming video.");
    }
  };

  const toggleMediaMic = (isActive, videoElement = null) => {
    mediaActiveRef.current = isActive;
    setMediaActive(isActive);
    
    if (videoElement) {
      videoRef.current = videoElement;
    }

    if (isActive) {
      setStatus('VIDEO PLAYING (Listening for STOP)');
      setTimeout(safeStart, 100); 
    } else {
      setStatus(isConversingRef.current ? 'LISTENING' : 'STANDBY (Say Namaste)');
      setTimeout(safeStart, 300);
    }
  };

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition || !isWaked) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (e) => {
      let final = '';
      let interim = '';
      for (let i = e.resultIndex; i < e.results.length; ++i) {
        if (e.results[i].isFinal) final += e.results[i][0].transcript;
        else interim += e.results[i][0].transcript;
      }

      const lowerFinal = final.toLowerCase().trim();
      const lowerInterim = interim.toLowerCase().trim();

      if (lowerFinal.includes("stop listening") || lowerInterim.includes("stop listening")) {
        console.log("💤 STANDBY MODE ENGAGED (HISTORY PRESERVED)");
        
        stopFlagRef.current = true;
        isAISpeakingRef.current = false;
        isMutedBySystemRef.current = false;
        window.speechSynthesis.cancel();
        if (videoRef.current) videoRef.current.pause();
        mediaActiveRef.current = false;
        setMediaActive(false);

        isConversingRef.current = false;
        setStatus('STANDBY (Say Namaste)');
        setInterimText('');

        speak("If you want to wake me up say namaste");

        setTimeout(() => {
          stopFlagRef.current = false;
          safeStart();
        }, 400);
        return;
      }

      if (
        lowerFinal.includes("stop") || lowerFinal.includes("pause") ||
        lowerInterim.includes("stop") || lowerInterim.includes("pause")
      ) {
        stopEverything();
        return;
      }

      const timeSinceSpeechEnded = Date.now() - lastSpeechEndTimeRef.current;
      if (isMutedBySystemRef.current || isAISpeakingRef.current || timeSinceSpeechEnded < 800) {
        return; 
      }

      if (lowerFinal.includes("play again") || lowerFinal.includes("resume") || lowerFinal.includes("play")) {
        resumeVideo();
        return;
      }

      if (mediaActiveRef.current) return; 

      if (!isConversingRef.current) {
        if (lowerFinal.includes("namaste") || lowerInterim.includes("namaste")) {
          isConversingRef.current = true;
          setStatus('LISTENING');
          const welcomeMessage = {
            role: "assistant",
            content: "Namaste! Welcome to the Accion Experience Center.",            
          };
          setChat(prev => [...prev, welcomeMessage]);
          speak(welcomeMessage.content);
          setInterimText('');
        }
      } else {
        setInterimText(interim);
        if (final.trim() && !isAISpeakingRef.current && !stopFlagRef.current) {
          
          if (lowerFinal.includes("pbm migration case study")) {
            handleTurn(final, {
              video: "/assets/video/pbm_migration_case_study.mp4",
              answerText: "" // Left blank so no text or TTS runs
            });
          } else {
            handleTurn(final);
          }
        }
      }
    };

    recognition.onend = () => { 
      if (isActiveRef.current) {
        safeStart();
      }
    };

    recognitionRef.current = recognition;
    safeStart();

    return () => { 
      if (recognitionRef.current) recognitionRef.current.stop(); 
    };
  }, [isWaked]);

  const handleTurn = async (text, localMedia = null) => {
    if (mediaActiveRef.current) return; 
    isAISpeakingRef.current = true;
    setStatus('PROCESSING...');
    setInterimText('');
    setChat(prev => [...prev, { role: 'user', content: text }]);

    // 🔥 Force text visibility to clear out if user says or triggers a prompt containing "video"
    const userPromptContainsVideo = text.toLowerCase().includes("video");

    try {
      if (localMedia) {
        const botMessage = {
          role: 'assistant', 
          // Check if explicit video intercept or user query demands no text
          content: (localMedia.video || userPromptContainsVideo) ? "" : (localMedia.answerText || "Here is the information."),
          images: localMedia.url ? [{ url: localMedia.url }] : [],
          videos: localMedia.video ? [{ url: localMedia.video }] : [],
          links: []
        };
        setChat(prev => [...prev, botMessage]);
        if (botMessage.content) speak(botMessage.content);
        return;
      }

      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ question: text }));
      } else {
        const res = await fetch(`http://localhost:8000/api/chat/ask`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: text })
        });
        const data = await res.json();
        
        const hasVideos = (data.videos && data.videos.length > 0) || userPromptContainsVideo;

        const botMessage = {
          role: "assistant",
          // 🔥 Wipe output string completely if incoming REST response embeds videos
          content: hasVideos ? "" : cleanResponseText(data.answer || ""),
          images: data.images || [], 
          videos: data.videos || [], 
          links: data.links || []
        };
        setChat(prev => [...prev, botMessage]);
        if (botMessage.content) speak(botMessage.content);
      }
    } catch (err) { speak("Connection interrupted."); }
  };

  const speak = (text) => {
    if (!text || text.trim() === "") return; // Fallback to guard empty voice sequences

    stopFlagRef.current = false;
    window.speechSynthesis.cancel(); 
    isAISpeakingRef.current = true;
    setStatus('Speaking...');

    const voices = synthRef.getVoices();
    const selectedVoice =
      voices.find(v => v.name === 'Google US English' && !v.name.includes('Online')) ||
      voices.find(v => v.name.includes('Microsoft Aria')) ||
      voices[0];

    const chunks = text.match(/.{1,220}(\s|$)/g) || [text];
    let index = 0;

    const speakChunk = () => {
      if (stopFlagRef.current || index >= chunks.length) {
        isAISpeakingRef.current = false;
        isMutedBySystemRef.current = false;
        lastSpeechEndTimeRef.current = Date.now();
        if (!stopFlagRef.current && isActiveRef.current) {
          setStatus(isConversingRef.current ? 'LISTENING' : 'STANDBY (Say Namaste)');
        }
        return;
      }

      const utterance = new SpeechSynthesisUtterance(chunks[index]);
      if (selectedVoice) utterance.voice = selectedVoice;
      utterance.volume = 1.0; 

      utterance.onstart = () => {
        isMutedBySystemRef.current = true;
      };

      utterance.onend = () => {
        isMutedBySystemRef.current = false; 
        lastSpeechEndTimeRef.current = Date.now();
        
        if (!stopFlagRef.current) {
          index++;
          setTimeout(speakChunk, 80); 
        } else {
          isAISpeakingRef.current = false;
        }
      };

      utterance.onerror = (e) => {
        isMutedBySystemRef.current = false;
        lastSpeechEndTimeRef.current = Date.now();
        if (!stopFlagRef.current) {
          index++;
          speakChunk();
        } else {
          isAISpeakingRef.current = false;
        }
      };

      window.speechSynthesis.speak(utterance);
    };

    speakChunk();
  };

  const handleTabClick = (category) => {
    const prompts = {
      "Our services": { 
        text: "What specialized digital engineering and cloud services does Accion provide?", 
        image: "/assets/OurServices.png",
        answerText: "Accion provides specialized digital engineering services including cloud migration, cognitive computing, and collaborative software architecture solutions."
      },
      "our global talent base": { 
        text: "What is the scale and reach of Accion's global talent base?", 
        image: "/assets/GlobalTalentBase.png",
        answerText: "With over 5,000 employees globally distributed across 23 global locations, our engineering pool delivers seamless scaling capacities."
      },
      "our solutions accelerators and services": { 
        text: "How do Accion's accelerators speed up digital transformation?", 
        image: "/assets/SolutionsAccelerators.png",
        answerText: "Our 34 proprietary platforms and IP accelerators streamline software lifecycles, ensuring fast go-to-market execution."
      },
      "talent at accion": { 
        text: "What defines the engineering culture at Accion?", 
        image: "/assets/TalentAtAccion.png",
        answerText: "Our talent engineering culture is driven by continuous learning, complex technical innovation, and enterprise scaling principles."
      },
      "awards": { 
        text: "What industry awards has Accion received?", 
        image: "/assets/Awards.png",
        answerText: "Accion has consistently won distinguished industry awards for software architecture innovation and global delivery excellence."
      },
      "partnerships and alliances": { 
        text: "Which strategic partnerships does Accion leverage?", 
        image: "/assets/Partnerships.png",
        answerText: "We maintain highly focused strategic cloud partnerships and software ecosystem alliances to empower our collaborative delivery chains."
      }
    };
    const selectedPrompt = prompts[category];
    if (selectedPrompt) {
      window.speechSynthesis.cancel();
      if (!isWaked) wakeSystem();
      isConversingRef.current = true;
      
      handleTurn(selectedPrompt.text, { 
        url: selectedPrompt.image,
        answerText: selectedPrompt.answerText 
      });
    }
  };

  const wakeSystem = () => {
    setIsWaked(true);
    isActiveRef.current = true;
    const silent = new SpeechSynthesisUtterance(" ");
    silent.volume = 0;
    synthRef.speak(silent);
  };

  return (
    <div style={{
      height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', 
      padding: '20px', fontFamily: '"Inter", sans-serif', color: '#FFFFFF',
      backgroundColor: '#1A1A1A', overflow: 'hidden', position: 'relative'
    }}>
      
      {!isWaked && (
        <div onClick={wakeSystem} style={{
          position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
          backgroundColor: '#1A1A1A', zIndex: 100, display: 'flex',
          flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer'
        }}>
          <h1 style={{ fontSize: '40px', fontWeight: 800, margin: 0 }}>Insight<span style={{color: ACCION_RED}}>Host</span></h1>
          <p style={{ color: GLOW_CYAN, letterSpacing: '2px', fontWeight: 600, marginTop: '10px' }}>TAP TO ACTIVATE</p>
        </div>
      )}

      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
          .stat-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 12px; min-width: 120px; text-align: center; }
          .mic-outer { position: relative; width: 90px; height: 90px; display: flex; align-items: center; justify-content: center; transition: transform 0.3s; }
          .mic-glow { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 2px solid ${GLOW_CYAN}; opacity: 0.3; }
          .mic-glow-active { opacity: 1; animation: pulse-glow 2s infinite ease-in-out; box-shadow: 0 0 25px ${GLOW_CYAN}; }
          @keyframes pulse-glow { 0%, 100% { transform: scale(1); opacity: 0.6; } 50% { transform: scale(1.1); opacity: 1; } }
          .chat-window { width: 100%; max-width: 750px; flex: 1; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 20px; margin: 15px 0; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
          .bubble { padding: 12px 18px; border-radius: 15px; font-size: 14px; max-width: 85%; animation: fadeIn 0.3s ease forwards; }
          .user-bubble { align-self: flex-end; background: #FFFFFF; color: #1A1A1A; border-bottom-right-radius: 2px; }
          .ai-bubble { align-self: flex-start; background: rgba(255, 255, 255, 0.08); border-bottom-left-radius: 2px; border: 1px solid rgba(255,255,255,0.1); }
          @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        `}
      </style>

      <header style={{ textAlign: 'center', flexShrink: 0 }}>
        <h2 style={{ fontSize: '24px', fontWeight: 600, margin: 0 }}>Insight<span style={{color: ACCION_RED}}>Host</span></h2>
        <p style={{ fontSize: '14px', color: '#888', letterSpacing: '1px', textAlign: 'center' }}>ACCION XPERIENCE CENTER</p>
      </header>

      <div style={{ display: 'flex', gap: '15px', marginTop: '10px', flexShrink: 0 }}>
        {[['5000+', 'Employees Globally'], ['23+', 'Global Locations'], ['34+', 'Proprietary platforms and IP accelerators']].map(([val, label]) => (
          <div key={label} className="stat-card">
            <div style={{ color: '#7C3AED', fontSize: '18px', fontWeight: 800 }}>{val}</div>
            <div style={{ fontSize: '10px', color: '#888' }}>{label}</div>
          </div>
        ))}
      </div>

      <div className="mic-outer" style={{ margin: '15px 0', transform: isChatVisible ? 'scale(0.8)' : 'scale(1)', flexShrink: 0 }}>
        <div className={`mic-glow ${isConversingRef.current && !isAISpeakingRef.current && !mediaActive ? "mic-glow-active" : ""}`} />
        <div style={{
          width: '75px', height: '75px', background: 'rgba(255,255,255,0.1)', 
          borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2
        }}>
          <svg width="60" height="60" viewBox="0 0 24 24" fill={isConversingRef.current && !mediaActive ? GLOW_CYAN : "white"}>
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
          </svg>
        </div>
      </div>

      <p style={{ fontSize: '12px', color: (mediaActive || isAISpeakingRef.current) ? ACCION_RED : (isConversingRef.current ? GLOW_CYAN : '#666'), fontWeight: 600 }}>{status}</p>

      {isChatVisible ? (
        <div className="chat-window">
          {chat.map((msg, i) => (
            <div key={i} className={`bubble ${msg.role === 'user' ? 'user-bubble' : 'ai-bubble'}`} style={(msg.images?.length || msg.videos?.length) ? { maxWidth: '95%', width: '95%' } : {}}>
              <div style={{ fontSize: '10px', opacity: 0.6, marginBottom: '4px', fontWeight: 800 }}>{msg.role === 'user' ? 'YOU' : 'INSIGHT HOST'}</div>
              <div style={(msg.images?.length || msg.videos?.length) ? { display: "flex", gap: "18px" } : {}}>
                
                {/* Only render this content div if there's actually text to show */}
                {msg.content && <div style={{ flex: 1 }}>{msg.content}</div>}
                
                <div style={{ width: "260px", display: "flex", flexDirection: "column", gap: "10px" }}>
                  {msg.images?.map((img, idx) => {
                    let imageUrl = img.url || img; 
                    if (!imageUrl) return null;

                    const isFrontendAsset = imageUrl.startsWith('assets/') || imageUrl.startsWith('/assets/');

                    if (!imageUrl.startsWith('http') && !isFrontendAsset) {
                      let cleanImgPath = imageUrl.replace(/\\/g, '/');
                      cleanImgPath = cleanImgPath.replace(/^\/?media\//i, '');
                      cleanImgPath = cleanImgPath.replace(/^(knowledge_base\/|knowledgebase\/)/i, '');

                      if (!cleanImgPath.startsWith('images/') && !cleanImgPath.startsWith('assets/')) {
                        cleanImgPath = `images/${cleanImgPath}`;
                      }

                      cleanImgPath = cleanImgPath.split('/').map(seg => encodeURIComponent(seg)).join('/');
                      imageUrl = `http://localhost:8000/media/${cleanImgPath}`;
                    }

                    return (
                      <img 
                        key={idx} 
                        src={imageUrl} 
                        alt="Insight View Asset" 
                        style={{ 
                          width: "100%", 
                          borderRadius: "12px", 
                          border: "1px solid rgba(255,255,255,0.1)", 
                          display: "block",
                          backgroundColor: "rgba(255,255,255,0.02)",
                          marginBottom: "8px"
                        }} 
                        onError={(e) => {
                          console.error("❌ Failed to resolve image resource pipeline at:", imageUrl);
                        }}
                      />
                    );
                  })}
                  {msg.videos?.map((vid, idx) => {
                    let videoUrl = vid.url || vid;
                    const isFrontendAsset = videoUrl.startsWith('assets/') || videoUrl.startsWith('/assets/');

                    if (videoUrl && !videoUrl.startsWith('http') && !isFrontendAsset) {
                      let cleanPath = videoUrl.replace(/\\/g, '/');
                      cleanPath = cleanPath.replace(/^\/?media\//i, '');
                      cleanPath = cleanPath.replace(/^(knowledge_base\/|knowledgebase\/|knowledge_base-|knowledgebase-)/i, '');

                      if (cleanPath.startsWith('videos-')) {
                        cleanPath = cleanPath.replace('videos-', 'videos/');
                      }
                      if (!cleanPath.startsWith('videos/')) {
                        cleanPath = `videos/${cleanPath}`;
                      }

                      cleanPath = cleanPath.split('/').map(segment => encodeURIComponent(segment)).join('/');
                      videoUrl = `http://localhost:8000/media/${cleanPath}`;
                    }

                    return (
                      <div key={idx} style={{ width: '100%', marginBottom: '10px' }}>
                        <video 
                          src={videoUrl}
                          controls 
                          autoPlay 
                          playsInline
                          preload="metadata"
                          style={{ width: '100%', borderRadius: '10px', backgroundColor: '#000', display: 'block' }} 
                          onPlay={(e) => toggleMediaMic(true, e.target)} 
                          onPause={() => toggleMediaMic(false)} 
                          onEnded={() => toggleMediaMic(false)}
                          onError={(e) => {
                            console.error("❌ Failed Video Stream Target Location:", videoUrl);
                          }}
                        />
                      </div>
                    );
                  })}
                  {msg.links?.map((link,idx)=>(
                    <a
                      key={idx}
                      href={link}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        color:"#4DA6FF",
                        fontSize:"12px",
                        wordBreak:"break-word",
                        marginBottom:"8px"
                      }}
                    >
                      {link}
                    </a>
                  ))}
                </div>
              </div>
            </div>
          ))}

          {interimText && <div className="bubble user-bubble" style={{ opacity: 0.5 }}>{interimText}</div>}
          <div ref={chatEndRef} />
        </div>
      ) : (
        <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}><p style={{ color: '#444', fontStyle: 'italic' }}>Say "Namaste" to start</p></div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', width: '100%', maxWidth: '785px', paddingBottom: '20px' }}>
        {CATEGORY_DATA.map((cat) => (
          <div key={cat.name} onClick={() => handleTabClick(cat.name)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', textAlign: 'center', cursor: 'pointer', fontSize: '11px', fontWeight: '700' }}>
            {cat.name.toUpperCase()}
          </div>
        ))}
      </div>
    </div>
  );
};

export default BrightSoftwareHost;