import React, { useState, useEffect, useRef } from 'react';

// Configurable per deployment via frontend/.env - falls back to
// localhost for local development. Set REACT_APP_BACKEND_ORIGIN
// to the backend's real host:port on the kiosk PC / server it's
// actually deployed to (build-time value - requires a rebuild
// after changing it, per Create React App's env var handling).
const BACKEND_HTTP_ORIGIN = process.env.REACT_APP_BACKEND_ORIGIN || 'http://localhost:8002';
const BACKEND_WS_ORIGIN = BACKEND_HTTP_ORIGIN.replace(/^http/, 'ws');

const SUPPORTED_LANGUAGES = [
  { code: 'en-US', label: 'English' },
  { code: 'hi-IN', label: 'Hindi' },
  { code: 'te-IN', label: 'Telugu' },
  { code: 'ta-IN', label: 'Tamil' },
  { code: 'ml-IN', label: 'Malayalam' },
  { code: 'kn-IN', label: 'Kannada' },
  { code: 'es-ES', label: 'Spanish' },
  { code: 'fr-FR', label: 'French' },
  { code: 'de-DE', label: 'German' }
];

// The dropdown in the header is a touch fallback only - this is a
// no-touch, voice-first kiosk, so language switching and both
// greetings need to work by voice alone, in the chosen language.

const GREETINGS = {
  'en-US': {
    camera: "Welcome to InsightHost. How may I assist you today?",
    namaste: "Namaste! Welcome to the Accion Experience Center. How may I help you today?"
  },
  'hi-IN': {
    camera: "इनसाइटहोस्ट में आपका स्वागत है। मैं आपकी कैसे सहायता कर सकता हूँ?",
    namaste: "नमस्ते! एक्सियन एक्सपीरियंस सेंटर में आपका स्वागत है। मैं आपकी कैसे मदद कर सकता हूँ?"
  },
  'te-IN': {
    camera: "ఇన్‌సైట్‌హోస్ట్‌కు స్వాగతం. నేను మీకు ఈరోజు ఎలా సహాయపడగలను?",
    namaste: "నమస్తే! యాక్షన్ ఎక్స్‌పీరియన్స్ సెంటర్‌కు స్వాగతం. నేను మీకు ఈరోజు ఎలా సహాయపడగలను?"
  },
  'ta-IN': {
    camera: "இன்‌சைட்‌ஹோஸ்ட்டிற்கு வரவேற்கிறோம். நான் இன்று உங்களுக்கு எப்படி உதவ முடியும்?",
    namaste: "வணக்கம்! ஆக்சியன் எக்ஸ்பீரியன்ஸ் சென்டருக்கு வரவேற்கிறோம். நான் இன்று உங்களுக்கு எப்படி உதவ முடியும்?"
  },
  'ml-IN': {
    camera: "ഇൻസൈറ്റ്‌ഹോസ്റ്റിലേക്ക് സ്വാഗതം. ഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കും?",
    namaste: "നമസ്തേ! ആക്ഷൻ എക്സ്പീരിയൻസ് സെന്ററിലേക്ക് സ്വാഗതം. ഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കും?"
  },
  'kn-IN': {
    camera: "ಇನ್‌ಸೈಟ್‌ಹೋಸ್ಟ್‌ಗೆ ಸ್ವಾಗತ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
    namaste: "ನಮಸ್ತೆ! ಆಕ್ಷನ್ ಎಕ್ಸ್‌ಪೀರಿಯನ್ಸ್ ಸೆಂಟರ್‌ಗೆ ಸ್ವಾಗತ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?"
  },
  'es-ES': {
    camera: "Bienvenido a InsightHost. ¿Cómo puedo ayudarle hoy?",
    namaste: "¡Namaste! Bienvenido al Centro de Experiencia de Accion. ¿Cómo puedo ayudarle hoy?"
  },
  'fr-FR': {
    camera: "Bienvenue chez InsightHost. Comment puis-je vous aider aujourd'hui ?",
    namaste: "Namaste ! Bienvenue au Centre d'Expérience Accion. Comment puis-je vous aider aujourd'hui ?"
  },
  'de-DE': {
    camera: "Willkommen bei InsightHost. Wie kann ich Ihnen heute helfen?",
    namaste: "Namaste! Willkommen im Accion Experience Center. Wie kann ich Ihnen heute helfen?"
  }
};

// Voice command to change language, e.g. "switch to Hindi",
// "speak in French", "change language to Spanish", "change the
// shift the language to Telugu" (real speech - and speech-to-text
// transcription - doesn't come in neat fixed phrases, so this
// matches loosely: any switch-ish verb OR the word "language",
// plus a recognized language name, anywhere in the sentence -
// rather than requiring one of a fixed list of exact phrases).
const LANGUAGE_SWITCH_VERBS = [
  'switch', 'change', 'shift', 'speak', 'talk', 'set', 'use'
];

const LANGUAGE_NAME_MATCHES = {
  'en-US': ['english'],
  'hi-IN': ['hindi'],
  'te-IN': ['telugu'],
  'ta-IN': ['tamil'],
  'ml-IN': ['malayalam'],
  'kn-IN': ['kannada'],
  'es-ES': ['spanish', 'español'],
  'fr-FR': ['french', 'français'],
  'de-DE': ['german', 'deutsch']
};

const LANGUAGE_SWITCH_CONFIRM = {
  'en-US': "Sure, I'll continue in English.",
  'hi-IN': "ठीक है, अब मैं हिंदी में बात करूँगा।",
  'te-IN': "సరే, ఇప్పుడు నేను తెలుగులో మాట్లాడతాను.",
  'ta-IN': "சரி, இப்போது நான் தமிழில் பேசுவேன்.",
  'ml-IN': "ശരി, ഇനി ഞാൻ മലയാളത്തിൽ സംസാരിക്കാം.",
  'kn-IN': "ಸರಿ, ಈಗ ನಾನು ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡುತ್ತೇನೆ.",
  'es-ES': "Claro, continuaré en español.",
  'fr-FR': "D'accord, je continuerai en français.",
  'de-DE': "Gut, ich spreche jetzt auf Deutsch."
};

const detectLanguageSwitchCommand = (text) => {
  const lower = (text || '').toLowerCase();
  if (!lower) return null;

  const soundsLikeALanguageRequest =
    lower.includes('language') ||
    LANGUAGE_SWITCH_VERBS.some((verb) => lower.includes(verb));

  if (!soundsLikeALanguageRequest) return null;

  for (const [code, names] of Object.entries(LANGUAGE_NAME_MATCHES)) {
    if (names.some((name) => lower.includes(name))) {
      return code;
    }
  }
  return null;
};

const BrightSoftwareHost = () => {
  const [status, setStatus] = useState('SYSTEM_OFFLINE');
  const [chat, setChat] = useState([]);
  const [interimText, setInterimText] = useState('');
  const [isWaked, setIsWaked] = useState(false);
  const [mediaActive, setMediaActive] = useState(false);
  const [language, setLanguage] = useState('en-US');
  const languageRef = useRef('en-US');

  const [cameraEnabled, setCameraEnabled] = useState(false);

  const stopFlagRef = useRef(false);
  const recognitionRef = useRef(null);
  const isActiveRef = useRef(true); 
  const isConversingRef = useRef(false);
  const isAISpeakingRef = useRef(false);
  const mediaActiveRef = useRef(false); 
 const socketRef = useRef(null);
 const mediaVideoRef = useRef(null);
 const cameraRef = useRef(null);
 const greetedRef = useRef(false);
 const userPresentRef = useRef(false);
 const namasteGreetedRef = useRef(false);

  const isMutedBySystemRef = useRef(false);
  const lastSpeechEndTimeRef = useRef(0);
  const missedDetectionsRef = useRef(0);
  const audioUnlockedRef = useRef(false);
  const [audioBlocked, setAudioBlocked] = useState(false);

  // Face detection can flicker for a moment (someone turns their
  // head, blinks, or a frame is briefly poorly lit) even while
  // they are still there and actively talking. Requiring several
  // consecutive misses (rather than a single one) before treating
  // the visitor as "gone" stops the greeting/standby cycle from
  // re-triggering mid-conversation.
  const PRESENCE_MISS_THRESHOLD = 3;

  const synthRef = window.speechSynthesis || {
    getVoices: () => [],
    speak: () => {},
    cancel: () => {}
  };

  const chatEndRef = useRef(null);
  const startCamera = async () => {

    try {

      const stream =
        await navigator.mediaDevices.getUserMedia({
          video: true
        });

      if (cameraRef.current) {

        cameraRef.current.srcObject =
          stream;

        setCameraEnabled(true);
      }

    } catch (error) {

      console.error(
        "Camera access denied",
        error
      );
    }
  };
  const ACCION_RED = "#E31E24";
  const GLOW_CYAN = "#00FFFF";

  const checkPersonDetection = async () => {

    try {

      // The browser already holds the camera for the preview
      // below (getUserMedia). Most webcams only allow one
      // exclusive consumer, so detection runs server-side on
      // a frame captured from that same stream, rather than
      // the backend opening its own competing camera handle.
      const videoEl = cameraRef.current;

      if (!videoEl || !videoEl.videoWidth || videoEl.readyState < 2) {

        return;
      }

      const canvas = document.createElement('canvas');
      canvas.width = videoEl.videoWidth;
      canvas.height = videoEl.videoHeight;
      canvas.getContext('2d').drawImage(videoEl, 0, 0, canvas.width, canvas.height);

      const frameData = canvas.toDataURL('image/jpeg', 0.7);

      const response = await fetch(
        `${BACKEND_HTTP_ORIGIN}/api/camera/detect`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: frameData })
        }
      );

      const data = await response.json();

      console.log("Camera:", data);

      if (data.person_detected) {

      missedDetectionsRef.current = 0;

      if (!userPresentRef.current) {

        userPresentRef.current = true;

        greetedRef.current = true;

        setIsWaked(true);

        isConversingRef.current = true;

        setStatus("LISTENING");

        // Only greet on a fresh arrival, and never talk over
        // the visitor or over the assistant's own response.
        if (!isAISpeakingRef.current && !mediaActiveRef.current) {

          const greeting =
            (GREETINGS[languageRef.current] || GREETINGS['en-US']).camera;

          const utterance =
            new SpeechSynthesisUtterance(
              greeting
            );

          utterance.lang = languageRef.current;

          speechSynthesis.speak(
            utterance
          );
        }

      } else if (!isConversingRef.current) {

        // Only touch the status label before a conversation has
        // started. Once conversing, this polling loop must not
        // fight with the status set by speech recognition/replies.
        setStatus("PERSON DETECTED");
      }

    } else {

      missedDetectionsRef.current += 1;

      if (missedDetectionsRef.current >= PRESENCE_MISS_THRESHOLD) {

        setStatus("STANDBY");

        userPresentRef.current = false;

        greetedRef.current = false;

        isConversingRef.current = false;

        namasteGreetedRef.current = false;
      }
    }

      }
    catch (error) {

      console.error(
        "Error checking camera status",
        error
      );
    }
  };
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

    startCamera();
    const interval = setInterval(
      checkPersonDetection,
      2000
    );

    return () => clearInterval(interval);

  }, []);

  useEffect(() => {
    languageRef.current = language;
  }, [language]);

  // This is a fully hands-free, voice-only kiosk experience: the
  // system wakes itself as soon as the page loads (no tap needed),
  // rather than waiting for someone to touch the screen.
  //
  // The one thing no page can override is the browser's own audio
  // policy: some browsers withhold speech playback until they have
  // seen one real user gesture (click/tap/key) on the page. This
  // attempts to unlock audio immediately, and silently retries on
  // the first incidental touch/click/key press anywhere (a cleaner,
  // touchpanel tap, a remote click - whatever happens first) if
  // that first attempt was blocked. For a dedicated boardroom/
  // reception display, launching the browser in kiosk mode with
  // --autoplay-policy=no-user-gesture-required removes this
  // restriction entirely, so no gesture is needed at all.
  useEffect(() => {
    wakeSystem();

    const retryAudioUnlock = () => {
      if (audioUnlockedRef.current) return;

      const silent = new SpeechSynthesisUtterance(" ");
      silent.volume = 0;
      silent.onstart = () => {
        audioUnlockedRef.current = true;
        setAudioBlocked(false);
      };
      synthRef.speak(silent);
    };

    window.addEventListener('click', retryAudioUnlock);
    window.addEventListener('touchstart', retryAudioUnlock);
    window.addEventListener('keydown', retryAudioUnlock);

    return () => {
      window.removeEventListener('click', retryAudioUnlock);
      window.removeEventListener('touchstart', retryAudioUnlock);
      window.removeEventListener('keydown', retryAudioUnlock);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const connectWebSocket = () => {
      if (socketRef.current && (socketRef.current.readyState === WebSocket.OPEN || socketRef.current.readyState === WebSocket.CONNECTING)) {
        return;
      }
      const socket = new WebSocket(`${BACKEND_WS_ORIGIN}/api/ws`);
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

  // YouTube embeds are <iframe>s, not <video> elements - they have
  // no .play()/.pause() methods and don't fire onPlay/onPause/onEnded.
  // Controlling them needs the embedded player's postMessage command
  // protocol instead (the embed URL must include enablejsapi=1, see
  // services/media_service.py's convert_youtube_embed).
  const isYoutubeMediaEl = (el) => el && el.tagName === 'IFRAME';

  const sendYoutubeCommand = (el, func) => {
    if (!el || !el.contentWindow) return;
    el.contentWindow.postMessage(
      JSON.stringify({ event: 'command', func, args: [] }),
      '*'
    );
  };

  const stopEverything = () => {
    console.log("🛑 HARD STOP TRIGGERED");
    stopFlagRef.current = true;
    isAISpeakingRef.current = false;
    isMutedBySystemRef.current = false;
    lastSpeechEndTimeRef.current = Date.now();

    window.speechSynthesis.cancel();

    if (mediaVideoRef.current) {
      if (isYoutubeMediaEl(mediaVideoRef.current)) {
        sendYoutubeCommand(mediaVideoRef.current, 'pauseVideo');
      } else {
        mediaVideoRef.current.pause();
      }
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
    if (mediaVideoRef.current) {
      if (isYoutubeMediaEl(mediaVideoRef.current)) {
        sendYoutubeCommand(mediaVideoRef.current, 'playVideo');
      } else {
        mediaVideoRef.current.play();
      }
      setStatus('VIDEO PLAYING (Listening for STOP)');
      speak("Resuming video.");
    }
  };

  const toggleMediaMic = (isActive, videoElement = null) => {
    mediaActiveRef.current = isActive;
    setMediaActive(isActive);
    
    if (videoElement) {
      mediaVideoRef.current = videoElement;
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
    recognition.lang = languageRef.current;

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
        if (mediaVideoRef.current) mediaVideoRef.current.pause();
        mediaActiveRef.current = false;
        setMediaActive(false);

        isConversingRef.current = false;
        namasteGreetedRef.current = false;
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

      // Voice-driven language switching (e.g. "switch to Hindi",
      // "speak in French") - this is a no-touch kiosk, so changing
      // language has to work without anyone touching the dropdown.
      // Checked only against the final transcript, not interim, so
      // it fires once per actual utterance rather than repeatedly
      // while still being spoken.
      const languageSwitchTo = detectLanguageSwitchCommand(lowerFinal);

      if (languageSwitchTo && languageSwitchTo !== languageRef.current) {

        languageRef.current = languageSwitchTo;
        setLanguage(languageSwitchTo);

        const confirmation =
          LANGUAGE_SWITCH_CONFIRM[languageSwitchTo] || LANGUAGE_SWITCH_CONFIRM['en-US'];

        speak(confirmation);
        setInterimText('');
        return;
      }

      // "Namaste" always gets its own dedicated greeting reply,
      // exactly once per conversation, even if the camera already
      // auto-greeted the visitor and isConversingRef is already
      // true. Without this check, saying "Namaste" after the
      // camera's own greeting would fall straight into the normal
      // question path below and get sent to the backend as if it
      // were a real question - producing an irrelevant answer
      // instead of a proper greeting response.
      const saidNamaste =
        lowerFinal.includes("namaste") || lowerInterim.includes("namaste");

      if (saidNamaste && !namasteGreetedRef.current) {

        namasteGreetedRef.current = true;
        isConversingRef.current = true;
        setStatus('LISTENING');

        const welcomeMessage = {
          role: "assistant",
          content: (GREETINGS[languageRef.current] || GREETINGS['en-US']).namaste,
        };
        setChat(prev => [...prev, welcomeMessage]);
        speak(welcomeMessage.content);
        setInterimText('');
        return;
      }

      if (!isConversingRef.current) {
        // Not conversing yet, and this wasn't "Namaste" either -
        // nothing to do until the camera detects someone or they
        // greet the assistant.
        return;
      }

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
  }, [isWaked, language]);

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
        const res = await fetch(`${BACKEND_HTTP_ORIGIN}/api/chat/ask`, {
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

    const currentLang = languageRef.current;
    const langPrefix = currentLang.split('-')[0];

    const voices = synthRef.getVoices();
    const selectedVoice =
      voices.find(v => v.lang === currentLang) ||
      voices.find(v => v.lang && v.lang.startsWith(langPrefix)) ||
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
      utterance.lang = currentLang;
      if (selectedVoice) utterance.voice = selectedVoice;
      utterance.volume = 1.0;

      utterance.onstart = () => {
        isMutedBySystemRef.current = true;
        audioUnlockedRef.current = true;
        setAudioBlocked(false);
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

        // A blocked/denied error on the very first attempt usually
        // means the browser is withholding audio until it sees a
        // real user gesture (click/tap/key) on the page.
        if (!audioUnlockedRef.current) {
          setAudioBlocked(true);
        }

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
          <p style={{ color: GLOW_CYAN, letterSpacing: '2px', fontWeight: 600, marginTop: '10px' }}>STARTING...</p>
        </div>
      )}

      {audioBlocked && (
        <div style={{
          position: 'absolute', top: 0, left: 0, width: '100%',
          backgroundColor: ACCION_RED, color: '#FFFFFF', zIndex: 200,
          textAlign: 'center', padding: '10px', fontSize: '14px', fontWeight: 700,
          letterSpacing: '0.5px'
        }}>
          Voice is muted by the browser until one touch/click is registered on this screen.
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
          .chat-window { width: 100%; max-width: 750px; flex: 1; min-height: 0; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 20px; margin: 15px 0; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
          .bubble { padding: 12px 18px; border-radius: 15px; font-size: clamp(16px, 1.5vw, 24px); line-height: 1.4; max-width: 85%; animation: fadeIn 0.3s ease forwards; }
          .user-bubble { align-self: flex-end; background: #FFFFFF; color: #1A1A1A; border-bottom-right-radius: 2px; }
          .ai-bubble { align-self: flex-start; background: rgba(255, 255, 255, 0.08); border-bottom-left-radius: 2px; border: 1px solid rgba(255,255,255,0.1); }
          @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        `}
      </style>

      <header style={{ textAlign: 'center', flexShrink: 0, position: 'relative', width: '100%' }}>
        <h2 style={{ fontSize: 'clamp(24px, 3vw, 48px)', fontWeight: 600, margin: 0 }}>Insight<span style={{color: ACCION_RED}}>Host</span></h2>
        <p style={{ fontSize: 'clamp(14px, 1.3vw, 20px)', color: '#888', letterSpacing: '1px', textAlign: 'center' }}>ACCION XPERIENCE CENTER</p>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          aria-label="Conversation language"
          style={{
            position: 'absolute', top: 0, right: 0,
            background: 'rgba(255,255,255,0.08)', color: '#FFFFFF',
            border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px',
            fontSize: 'clamp(11px, 1vw, 16px)', padding: '4px 6px', cursor: 'pointer'
          }}
        >
          {SUPPORTED_LANGUAGES.map((lang) => (
            <option key={lang.code} value={lang.code} style={{ color: '#1A1A1A' }}>
              {lang.label}
            </option>
          ))}
        </select>
      </header>

      {/* These stats are only useful before a conversation starts -
          hidden once chatting so the chat area gets that space instead. */}
      {!isChatVisible && (
        <div style={{ display: 'flex', gap: '15px', marginTop: '10px', flexShrink: 0 }}>
          {[['5000+', 'Employees Globally'], ['23+', 'Global Locations'], ['34+', 'Proprietary platforms and IP accelerators']].map(([val, label]) => (
            <div key={label} className="stat-card">
              <div style={{ color: '#7C3AED', fontSize: 'clamp(18px, 1.8vw, 30px)', fontWeight: 800 }}>{val}</div>
              <div style={{ fontSize: 'clamp(10px, 1vw, 16px)', color: '#888' }}>{label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="mic-outer" style={{ margin: isChatVisible ? '6px 0' : '15px 0', transform: isChatVisible ? 'scale(0.7)' : 'scale(1)', flexShrink: 0 }}>
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
      <div
        style={{
          marginTop: "6px",
          marginBottom: "6px",
          flexShrink: 0
        }}
      >

        {/* Presence-detection preview only, not the main UI focus -
            kept small so the chat area gets the room it needs, and
            shrinks further once a conversation is underway. */}
        <video
          ref={cameraRef}
          autoPlay
          muted
          playsInline
          width={isChatVisible ? 90 : 150}
          style={{
            borderRadius: "12px",
            border: "1px solid rgba(255,255,255,0.2)",
            display: "block"
          }}
        />

      </div>
      <p style={{ fontSize: 'clamp(16px, 1.8vw, 30px)', color: (mediaActive || isAISpeakingRef.current) ? ACCION_RED : (isConversingRef.current ? GLOW_CYAN : '#666'), fontWeight: 700, margin: '4px 0', flexShrink: 0 }}>{status}</p>

      {isChatVisible ? (
        <div className="chat-window">
          {chat.map((msg, i) => (
            <div key={i} className={`bubble ${msg.role === 'user' ? 'user-bubble' : 'ai-bubble'}`} style={(msg.images?.length || msg.videos?.length) ? { maxWidth: '95%', width: '95%' } : {}}>
              <div style={{ fontSize: 'clamp(11px, 1vw, 15px)', opacity: 0.6, marginBottom: '4px', fontWeight: 800 }}>{msg.role === 'user' ? 'YOU' : 'INSIGHT HOST'}</div>
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
                      imageUrl = `${BACKEND_HTTP_ORIGIN}/media/${cleanImgPath}`;
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
                      videoUrl = `${BACKEND_HTTP_ORIGIN}/media/${cleanPath}`;
                    }

                    const isYoutubeEmbed = videoUrl.includes('youtube.com/embed');

                    return (
                      <div key={idx} style={{ width: '100%', marginBottom: '10px' }}>
                        {isYoutubeEmbed ? (
                          // YouTube embeds are iframes, not <video> elements -
                          // they have no play()/pause() and fire no onPlay/
                          // onPause/onEnded DOM events, so the mic-listening
                          // state is switched on as soon as it mounts instead
                          // (it also autoplays muted per its embed URL).
                          <iframe
                            title={`youtube-video-${idx}`}
                            src={videoUrl}
                            allow="autoplay; encrypted-media"
                            allowFullScreen
                            style={{ width: '100%', aspectRatio: '16 / 9', border: 'none', borderRadius: '10px', backgroundColor: '#000', display: 'block' }}
                            ref={(el) => {
                              if (el && mediaVideoRef.current !== el) {
                                mediaVideoRef.current = el;
                                toggleMediaMic(true, el);
                              }
                            }}
                          />
                        ) : (
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
                        )}
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
        <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}><p style={{ color: '#444', fontStyle: 'italic', fontSize: 'clamp(16px, 1.8vw, 26px)' }}>Say "Namaste" to start</p></div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', width: '100%', maxWidth: '785px', paddingBottom: '20px' }}>
        {CATEGORY_DATA.map((cat) => (
          <div key={cat.name} onClick={() => handleTabClick(cat.name)} style={{ padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', textAlign: 'center', cursor: 'pointer', fontSize: 'clamp(13px, 1.2vw, 18px)', fontWeight: '700' }}>
            {cat.name.toUpperCase()}
          </div>
        ))}
      </div>
    </div>
  );
};

export default BrightSoftwareHost;