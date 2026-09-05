/**
 * BHARAT ACADEMIX - MASTER CLIENT CONTROLLER
 * Full frontend logic for Dashboard, AI Classroom, Adaptive Loop, Assessment, and Report
 */

const STATE = {
  currentSession: null,
  currentConceptIndex: 0,
  selectedFile: null,
  isAudioPlaying: false,
  playbackSpeed: 1.0,
  speechRecognition: null,
  isRecordingVoice: false,
  studentProfile: null,
  quizAnswers: {}
};

// ==========================================================================
// INITIALIZATION
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
  fetchStudentProfile();
  initSpeechRecognition();
  setupAudioListeners();
});

// ==========================================================================
// VIEW CONTROLLER
// ==========================================================================

function switchView(viewId) {
  document.querySelectorAll(".app-view").forEach(v => v.classList.remove("active"));
  const target = document.getElementById(viewId);
  if (target) {
    target.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

// ==========================================================================
// STUDENT PROFILE & STATS
// ==========================================================================

async function fetchStudentProfile() {
  try {
    const res = await fetch("/api/profile");
    if (res.ok) {
      const data = await res.json();
      STATE.studentProfile = data;
      renderProfileUI(data);
    }
  } catch (err) {
    console.warn("Could not fetch profile:", err);
  }
}

function renderProfileUI(profile) {
  if (!profile) return;
  
  // Update Navigation Bar
  document.getElementById("navStudentName").textContent = profile.student_name || "Aarav Sharma";
  document.getElementById("navStudentXp").textContent = profile.total_xp || "1450";
  document.getElementById("navStudentStreak").textContent = profile.streak_days || "4";

  // Update Dashboard Summary Card
  document.getElementById("dashLessonsCount").textContent = profile.lessons_completed || "3";
  document.getElementById("dashMasteryAvg").textContent = (profile.mastery_average || 82) + "%";
  document.getElementById("dashStreak").textContent = (profile.streak_days || 4) + " 🔥";

  // Render Weak Areas
  const weakList = document.getElementById("dashWeakAreasList");
  if (weakList) {
    weakList.innerHTML = "";
    const weakAreas = profile.weak_areas || ["Recursion Base Cases", "Variable Scoping"];
    weakAreas.forEach(w => {
      const pill = document.createElement("span");
      pill.className = "tag-pill warning";
      pill.textContent = w;
      weakList.appendChild(pill);
    });
  }

  // Render Recommended Next Topics
  const recList = document.getElementById("dashRecommendationsList");
  if (recList) {
    recList.innerHTML = "";
    const recs = profile.recommended_topics || [];
    recs.forEach(r => {
      const card = document.createElement("div");
      card.className = "recommend-item";
      card.onclick = () => {
        setTopic(r.title);
        switchInputTab("topic");
      };
      card.innerHTML = `
        <div class="recommend-info">
          <h5>${r.title}</h5>
          <p>${r.reason || "Recommended next step"}</p>
        </div>
        <button type="button" class="launch-mini-btn" title="Start Lesson"><i class="fa-solid fa-play"></i></button>
      `;
      recList.appendChild(card);
    });
  }
}

// ==========================================================================
// DASHBOARD & LESSON SETUP
// ==========================================================================

function switchInputTab(tab) {
  const topicTab = document.getElementById("tabTopic");
  const fileTab = document.getElementById("tabFile");
  const topicSection = document.getElementById("topicInputSection");
  const fileSection = document.getElementById("fileInputSection");

  if (tab === "topic") {
    topicTab.classList.add("active");
    fileTab.classList.remove("active");
    topicSection.classList.add("active");
    fileSection.classList.remove("active");
  } else {
    fileTab.classList.add("active");
    topicTab.classList.remove("active");
    fileSection.classList.add("active");
    topicSection.classList.remove("active");
  }
}

function setTopic(text) {
  document.getElementById("topicInput").value = text;
}

function handleFileSelected(input) {
  if (input.files && input.files[0]) {
    const file = input.files[0];
    STATE.selectedFile = file;
    document.getElementById("selectedFileName").textContent = file.name;
    document.getElementById("selectedFileInfo").style.display = "flex";
    document.getElementById("pdfDropzone").style.display = "none";
  }
}

function clearSelectedFile() {
  STATE.selectedFile = null;
  document.getElementById("fileUploadInput").value = "";
  document.getElementById("selectedFileInfo").style.display = "none";
  document.getElementById("pdfDropzone").style.display = "block";
}

// Drag & drop dropzone
const dropzone = document.getElementById("pdfDropzone");
if (dropzone) {
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, preventDefaults, false);
  });
  function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      document.getElementById("fileUploadInput").files = files;
      handleFileSelected(document.getElementById("fileUploadInput"));
    }
  });
}

// Start Lesson Handler
async function handleStartLesson(e) {
  e.preventDefault();
  
  const startBtn = document.getElementById("startLessonBtn");
  const btnText = startBtn.querySelector(".btn-text");
  const btnLoader = startBtn.querySelector(".btn-loader");

  btnText.style.display = "none";
  btnLoader.style.display = "inline-flex";
  startBtn.disabled = true;

  const topic = document.getElementById("topicInput").value.trim();
  const level = document.querySelector('input[name="level"]:checked')?.value || "beginner";
  const language = document.getElementById("languageSelect").value;
  const time_available = document.querySelector('input[name="time_available"]:checked')?.value || "20 minutes";
  const objective = document.getElementById("objectiveSelect").value;

  const formData = new FormData();
  formData.append("topic", topic);
  formData.append("level", level);
  formData.append("language", language);
  formData.append("time_available", time_available);
  formData.append("objective", objective);

  if (STATE.selectedFile) {
    formData.append("file", STATE.selectedFile);
  }

  try {
    const res = await fetch("/api/lesson/create", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Failed to prepare lesson.");
    const lessonData = await res.json();
    
    STATE.currentSession = lessonData;
    STATE.currentConceptIndex = 0;

    launchClassroom(lessonData);
  } catch (err) {
    alert("Error creating lesson: " + err.message);
  } finally {
    btnText.style.display = "inline-flex";
    btnLoader.style.display = "none";
    startBtn.disabled = false;
  }
}

// ==========================================================================
// CLASSROOM INITIALIZATION & STEPPER
// ==========================================================================

function launchClassroom(lessonData) {
  // Populate Topbar Metadata
  document.getElementById("classLessonTopic").textContent = lessonData.topic || "Interactive Lesson";
  document.getElementById("classLevelTag").textContent = (lessonData.level || "beginner").toUpperCase();
  document.getElementById("classLangTag").textContent = lessonData.language || "Hinglish";

  // Build Concept Stepper Nodes
  const stepper = document.getElementById("conceptStepper");
  stepper.innerHTML = "";
  lessonData.concepts.forEach((c, idx) => {
    const node = document.createElement("div");
    node.className = `step-node ${idx === 0 ? 'active' : ''}`;
    node.id = `stepNode_${idx}`;
    node.innerHTML = `<span>Concept ${idx + 1}</span>`;
    stepper.appendChild(node);
  });

  // Load First Concept
  loadConcept(0);

  // Switch View
  switchView("viewClassroom");
}

function loadConcept(index) {
  if (!STATE.currentSession || !STATE.currentSession.concepts[index]) return;

  STATE.currentConceptIndex = index;
  const concept = STATE.currentSession.concepts[index];
  const total = STATE.currentSession.concepts.length;

  // Update Topbar Badge
  document.getElementById("classConceptBadge").textContent = `Concept ${index + 1} of ${total}`;

  // Update Stepper Active State
  STATE.currentSession.concepts.forEach((_, i) => {
    const node = document.getElementById(`stepNode_${i}`);
    if (node) {
      if (i < index) node.className = "step-node completed";
      else if (i === index) node.className = "step-node active";
      else node.className = "step-node";
    }
  });

  // Update Slide
  const slideImg = document.getElementById("currentSlideImg");
  slideImg.src = concept.slide_url || "/static/slides/slide_placeholder.png";

  // Update Subtitles
  document.getElementById("subtitlesText").textContent = concept.explanation;

  // Update Right Stage Concept Details Card
  document.getElementById("cardConceptCounter").textContent = `CONCEPT ${index + 1} OF ${total}`;
  document.getElementById("cardConceptTitle").textContent = concept.concept;
  
  const keyPointsContainer = document.getElementById("cardKeyPoints");
  if (concept.has_code && concept.code_snippet) {
    keyPointsContainer.innerHTML = `<pre style="background:#0f172a; padding:0.75rem; border-radius:8px; font-family:var(--font-code); font-size:0.8rem; overflow-x:auto;"><code>${escapeHtml(concept.code_snippet)}</code></pre>`;
  } else {
    keyPointsContainer.innerHTML = `<p style="line-height:1.5;">${concept.explanation.substring(0, 180)}...</p>`;
  }

  // Reset Socratic Question Section
  document.getElementById("socraticQuestionText").textContent = concept.question;
  document.getElementById("studentAnswerInput").value = "";
  document.getElementById("studentAnswerSection").style.display = "block";
  document.getElementById("evaluationResultCard").style.display = "none";
  document.getElementById("submitAnswerBtn").disabled = false;

  // Set Next Concept Button Text
  const nextBtn = document.getElementById("nextConceptBtn");
  if (index === total - 1) {
    nextBtn.innerHTML = `<span>Proceed to Final Assessment</span> <i class="fa-solid fa-graduation-cap"></i>`;
  } else {
    nextBtn.innerHTML = `<span>Next Concept</span> <i class="fa-solid fa-arrow-right"></i>`;
  }

  // Play Audio Explanation
  playAudio(concept.audio_url);
}

// ==========================================================================
// AUDIO & AVATAR ANIMATION ENGINE
// ==========================================================================

function setupAudioListeners() {
  const audio = document.getElementById("lessonAudioElement");
  const progressBar = document.getElementById("audioProgressBar");
  const timeDisplay = document.getElementById("audioTimeDisplay");
  const mouth = document.getElementById("avatarMouth");
  const face = document.getElementById("avatarFace");
  const statusIndicator = document.getElementById("speechStatusIndicator");

  audio.addEventListener("timeupdate", () => {
    if (audio.duration) {
      const pct = (audio.currentTime / audio.duration) * 100;
      progressBar.style.width = pct + "%";
      timeDisplay.textContent = `${formatTime(audio.currentTime)} / ${formatTime(audio.duration)}`;
    }
  });

  audio.addEventListener("play", () => {
    STATE.isAudioPlaying = true;
    document.getElementById("playPauseIcon").className = "fa-solid fa-pause";
    document.getElementById("teacherAvatarWrapper").classList.add("speaking");
    statusIndicator.innerHTML = `<i class="fa-solid fa-volume-high"></i> Speaking`;
  });

  audio.addEventListener("pause", () => {
    STATE.isAudioPlaying = false;
    document.getElementById("playPauseIcon").className = "fa-solid fa-play";
    document.getElementById("teacherAvatarWrapper").classList.remove("speaking");
    statusIndicator.innerHTML = `<i class="fa-solid fa-volume-xmark"></i> Paused`;
  });

  audio.addEventListener("ended", () => {
    STATE.isAudioPlaying = false;
    document.getElementById("playPauseIcon").className = "fa-solid fa-play";
    document.getElementById("teacherAvatarWrapper").classList.remove("speaking");
    statusIndicator.innerHTML = `<i class="fa-solid fa-circle-check"></i> Concept Delivered`;
  });
}

function playAudio(url) {
  if (!url) return;
  const audio = document.getElementById("lessonAudioElement");
  audio.src = url;
  audio.playbackRate = STATE.playbackSpeed;
  audio.play().catch(e => {
    console.log("Audio autoplay prevented by browser. Click play button to start audio:", e);
  });
}

function toggleAudioPlayback() {
  const audio = document.getElementById("lessonAudioElement");
  if (audio.paused) {
    audio.play();
  } else {
    audio.pause();
  }
}

function replayCurrentConceptAudio() {
  if (!STATE.currentSession) return;
  const concept = STATE.currentSession.concepts[STATE.currentConceptIndex];
  if (concept && concept.audio_url) {
    playAudio(concept.audio_url);
  }
}

function cyclePlaybackSpeed() {
  const speeds = [1.0, 1.25, 1.5, 0.75];
  const currIdx = speeds.indexOf(STATE.playbackSpeed);
  STATE.playbackSpeed = speeds[(currIdx + 1) % speeds.length];
  
  const audio = document.getElementById("lessonAudioElement");
  audio.playbackRate = STATE.playbackSpeed;
  document.getElementById("speedBtn").textContent = STATE.playbackSpeed + "x";
}

function seekAudio(event) {
  const audio = document.getElementById("lessonAudioElement");
  const container = event.currentTarget;
  const rect = container.getBoundingClientRect();
  const clickX = event.clientX - rect.left;
  const pct = clickX / rect.width;
  if (audio.duration) {
    audio.currentTime = pct * audio.duration;
  }
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

// ==========================================================================
// SPEECH-TO-TEXT VOICE INPUT (Web Speech API)
// ==========================================================================

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    STATE.speechRecognition = new SpeechRecognition();
    STATE.speechRecognition.continuous = false;
    STATE.speechRecognition.interimResults = true;

    STATE.speechRecognition.onstart = () => {
      STATE.isRecordingVoice = true;
      document.getElementById("voiceInputBtn").classList.add("recording");
      document.getElementById("micBtnText").textContent = "Listening...";
    };

    STATE.speechRecognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map(r => r[0].transcript)
        .join("");
      document.getElementById("studentAnswerInput").value = transcript;
    };

    STATE.speechRecognition.onerror = (e) => {
      console.warn("Speech recognition error:", e);
      stopVoiceRecognition();
    };

    STATE.speechRecognition.onend = () => {
      stopVoiceRecognition();
    };
  } else {
    document.getElementById("voiceInputBtn").title = "Voice recognition not supported in this browser";
  }
}

function toggleVoiceSpeechRecognition() {
  if (!STATE.speechRecognition) {
    alert("Speech-to-text is not supported in this browser. Please type your answer.");
    return;
  }

  if (STATE.isRecordingVoice) {
    STATE.speechRecognition.stop();
  } else {
    // Set language according to session
    const lang = STATE.currentSession?.language || "English";
    if (lang === "Hindi" || lang === "Hinglish") {
      STATE.speechRecognition.lang = "hi-IN";
    } else if (lang === "Bengali") {
      STATE.speechRecognition.lang = "bn-IN";
    } else if (lang === "Tamil") {
      STATE.speechRecognition.lang = "ta-IN";
    } else if (lang === "Telugu") {
      STATE.speechRecognition.lang = "te-IN";
    } else {
      STATE.speechRecognition.lang = "en-IN";
    }

    STATE.speechRecognition.start();
  }
}

function stopVoiceRecognition() {
  STATE.isRecordingVoice = false;
  const btn = document.getElementById("voiceInputBtn");
  if (btn) {
    btn.classList.remove("recording");
    document.getElementById("micBtnText").textContent = "Voice";
  }
}

// ==========================================================================
// CORE SOCRATIC ADAPTIVE EVALUATION LOOP
// ==========================================================================

async function submitStudentAnswer() {
  const answer = document.getElementById("studentAnswerInput").value.trim();
  if (!answer) {
    alert("Please type or speak your answer before submitting.");
    return;
  }

  const submitBtn = document.getElementById("submitAnswerBtn");
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Evaluating...`;

  try {
    const res = await fetch("/api/lesson/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: STATE.currentSession.session_id,
        concept_idx: STATE.currentConceptIndex,
        student_answer: answer
      })
    });

    if (!res.ok) throw new Error("Evaluation failed.");
    const evalData = await res.json();
    
    renderEvaluationResult(evalData);
  } catch (err) {
    alert("Evaluation error: " + err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<span>Submit Answer</span> <i class="fa-solid fa-paper-plane"></i>`;
  }
}

function renderEvaluationResult(evalData) {
  const resultCard = document.getElementById("evaluationResultCard");
  const verdictBanner = document.getElementById("evalVerdictBanner");
  const verdictIcon = document.getElementById("verdictIcon");
  const verdictTitle = document.getElementById("verdictTitle");
  const verdictScore = document.getElementById("verdictScore");
  const feedbackText = document.getElementById("evalFeedbackText");

  const misconceptionBox = document.getElementById("misconceptionBox");
  const reexplanationBox = document.getElementById("reexplanationBox");
  const followupBox = document.getElementById("followupBox");

  verdictBanner.className = `eval-verdict-banner ${evalData.verdict}`;
  feedbackText.textContent = evalData.feedback || "Good response.";

  if (evalData.verdict === "correct") {
    verdictIcon.innerHTML = `<i class="fa-solid fa-circle-check"></i>`;
    verdictTitle.textContent = "Excellent! Concept Mastered";
    verdictScore.textContent = "Mastery: 100% · Solid understanding";

    misconceptionBox.style.display = "none";
    reexplanationBox.style.display = "none";
    followupBox.style.display = "none";
  } else if (evalData.verdict === "partial") {
    verdictIcon.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i>`;
    verdictTitle.textContent = "Good Effort! Partial Understanding";
    verdictScore.textContent = "Mastery: 60% · Core intuition grasped, but missed key details";

    if (evalData.misconception_name && evalData.misconception_name !== "None") {
      misconceptionBox.style.display = "block";
      document.getElementById("misconceptionName").textContent = evalData.misconception_name;
      document.getElementById("misconceptionDesc").textContent = evalData.misconception_description || "Misunderstood key operational rule.";
    }

    if (evalData.reexplanation) {
      reexplanationBox.style.display = "block";
      document.getElementById("reexplanationText").textContent = evalData.reexplanation;
    }

    if (evalData.followup_question) {
      followupBox.style.display = "block";
      document.getElementById("followupQuestionText").textContent = evalData.followup_question;
    }
  } else {
    // Incorrect
    verdictIcon.innerHTML = `<i class="fa-solid fa-circle-xmark"></i>`;
    verdictTitle.textContent = "Misconception Detected";
    verdictScore.textContent = "Mastery: 35% · Let's fix this misunderstanding together";

    misconceptionBox.style.display = "block";
    document.getElementById("misconceptionName").textContent = evalData.misconception_name || "Concept Gap";
    document.getElementById("misconceptionDesc").textContent = evalData.misconception_description || "Confused the fundamental mechanism.";

    if (evalData.reexplanation) {
      reexplanationBox.style.display = "block";
      document.getElementById("reexplanationText").textContent = evalData.reexplanation;
    }

    if (evalData.followup_question) {
      followupBox.style.display = "block";
      document.getElementById("followupQuestionText").textContent = evalData.followup_question;
    }
  }

  // Play re-explanation audio if available
  if (evalData.feedback_audio_url) {
    STATE.currentEvalAudioUrl = evalData.feedback_audio_url;
    playAudio(evalData.feedback_audio_url);
  }

  resultCard.style.display = "flex";
}

function playEvaluationAudio() {
  if (STATE.currentEvalAudioUrl) {
    playAudio(STATE.currentEvalAudioUrl);
  }
}

function submitRetryAnswer() {
  const retryVal = document.getElementById("retryAnswerInput").value.trim();
  if (retryVal) {
    alert("Great job! Your retry demonstrates you've corrected the misconception. Let's move forward!");
    document.getElementById("followupBox").style.display = "none";
  }
}

function advanceToNextConceptOrQuiz() {
  const nextIdx = STATE.currentConceptIndex + 1;
  const total = STATE.currentSession.concepts.length;

  if (nextIdx < total) {
    loadConcept(nextIdx);
  } else {
    // Launch Final Assessment Quiz
    launchFinalQuiz();
  }
}

// ==========================================================================
// CONTEXTUAL "ASK YOUR TEACHER" (DOUBT SOLVER)
// ==========================================================================

function openAskDoubtPanel() {
  document.getElementById("askDoubtDrawer").classList.add("open");
  document.getElementById("doubtTextInput").focus();
}

function closeAskDoubtPanel() {
  document.getElementById("askDoubtDrawer").classList.remove("open");
}

async function submitDoubtQuestion() {
  const input = document.getElementById("doubtTextInput");
  const question = input.value.trim();
  if (!question) return;

  const history = document.getElementById("doubtChatHistory");

  // Render Student Message
  const studentMsg = document.createElement("div");
  studentMsg.className = "chat-msg student-msg";
  studentMsg.innerHTML = `
    <div class="msg-avatar"><i class="fa-solid fa-user"></i></div>
    <div class="msg-bubble">${escapeHtml(question)}</div>
  `;
  history.appendChild(studentMsg);
  input.value = "";
  history.scrollTop = history.scrollHeight;

  // Placeholder Teacher Message
  const teacherMsg = document.createElement("div");
  teacherMsg.className = "chat-msg teacher-msg";
  teacherMsg.innerHTML = `
    <div class="msg-avatar"><i class="fa-solid fa-graduation-cap"></i></div>
    <div class="msg-bubble"><i class="fa-solid fa-spinner fa-spin"></i> Thinking...</div>
  `;
  history.appendChild(teacherMsg);
  history.scrollTop = history.scrollHeight;

  const currConcept = STATE.currentSession?.concepts[STATE.currentConceptIndex]?.concept || "";

  try {
    const res = await fetch("/api/lesson/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: STATE.currentSession?.session_id,
        question: question,
        current_concept: currConcept
      })
    });

    if (!res.ok) throw new Error("Could not get doubt response.");
    const data = await res.json();

    teacherMsg.querySelector(".msg-bubble").textContent = data.answer;
    history.scrollTop = history.scrollHeight;

    if (data.audio_url) {
      playAudio(data.audio_url);
    }
  } catch (err) {
    teacherMsg.querySelector(".msg-bubble").textContent = "Error answering doubt: " + err.message;
  }
}

// ==========================================================================
// FINAL QUIZ & COMPREHENSIVE LEARNING REPORT
// ==========================================================================

function finishLessonEarly() {
  if (confirm("Are you sure you want to finish the lesson and proceed to the final assessment?")) {
    launchFinalQuiz();
  }
}

function launchFinalQuiz() {
  switchView("viewAssessment");
  document.getElementById("quizContainer").style.display = "block";
  document.getElementById("reportContainer").style.display = "none";

  const quizList = document.getElementById("quizQuestionsList");
  quizList.innerHTML = "";

  const questions = STATE.currentSession?.final_quiz || [
    {
      id: 1,
      concept: "Core Foundations",
      question: "What is the primary operational rule governing this concept?",
      options: [
        "It establishes a base stopping condition to avoid infinite loops",
        "It executes non-deterministically without parameters",
        "It ignores previous state transitions",
        "It replaces foundational logic"
      ],
      correct_index: 0
    }
  ];

  STATE.quizAnswers = {};

  questions.forEach((q, idx) => {
    const item = document.createElement("div");
    item.className = "quiz-question-item";
    
    let optionsHtml = "";
    (q.options || []).forEach((opt, optIdx) => {
      optionsHtml += `
        <label class="option-label">
          <input type="radio" name="quiz_q_${q.id || idx}" value="${optIdx}" onchange="recordQuizAnswer(${idx}, ${optIdx})" />
          <span>${escapeHtml(opt)}</span>
        </label>
      `;
    });

    item.innerHTML = `
      <div class="q-concept-tag">${q.concept || 'Concept Check'}</div>
      <h4>${idx + 1}. ${escapeHtml(q.question)}</h4>
      <div class="quiz-options-list">${optionsHtml}</div>
    `;
    quizList.appendChild(item);
  });
}

function recordQuizAnswer(questionIndex, selectedOptionIndex) {
  STATE.quizAnswers[questionIndex] = selectedOptionIndex;
}

async function submitFinalQuiz() {
  const submitBtn = document.getElementById("submitQuizBtn");
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Analyzing Knowledge & Generating Diagnostic Report...`;

  const questions = STATE.currentSession?.final_quiz || [];
  const quizResults = questions.map((q, idx) => {
    const selected = STATE.quizAnswers[idx];
    const isCorrect = selected !== undefined && selected === q.correct_index;
    return {
      id: q.id || idx,
      concept: q.concept,
      selected_index: selected,
      correct_index: q.correct_index,
      is_correct: isCorrect
    };
  });

  try {
    const res = await fetch("/api/lesson/complete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: STATE.currentSession?.session_id,
        quiz_results: quizResults
      })
    });

    if (!res.ok) throw new Error("Could not generate report.");
    const reportData = await res.json();
    
    renderLearningReport(reportData);
    fetchStudentProfile(); // Refresh student stats
  } catch (err) {
    alert("Report generation error: " + err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<span>Submit Quiz & Generate Learning Report</span> <i class="fa-solid fa-square-poll-vertical"></i>`;
  }
}

function renderLearningReport(report) {
  document.getElementById("quizContainer").style.display = "none";
  const reportContainer = document.getElementById("reportContainer");
  reportContainer.style.display = "block";

  // Metadata
  document.getElementById("reportTopicMeta").textContent = `Topic: ${report.topic} · Level: ${report.level.toUpperCase()} · Language: ${report.language}`;

  // Score & Grade
  document.getElementById("reportScoreValue").textContent = report.score_percent + "%";
  document.getElementById("reportGradeBadge").textContent = `Grade: ${report.grade || 'A'}`;
  document.getElementById("reportTeacherSummary").textContent = report.teacher_summary || "Great job completing your personalized lesson session!";

  // Strong Concepts
  const strongList = document.getElementById("reportStrongList");
  strongList.innerHTML = "";
  (report.strong_concepts || []).forEach(sc => {
    const card = document.createElement("div");
    card.className = "breakdown-card";
    card.innerHTML = `
      <div class="breakdown-top">
        <span>${sc.concept}</span>
        <span style="color:var(--accent-green);">${sc.mastery || 90}%</span>
      </div>
      <p>${sc.note || 'Demonstrated solid grasp.'}</p>
      <div class="mini-bar-bg"><div class="mini-bar-fill green" style="width:${sc.mastery || 90}%"></div></div>
    `;
    strongList.appendChild(card);
  });

  // Weak Concepts
  const weakList = document.getElementById("reportWeakList");
  weakList.innerHTML = "";
  (report.weak_concepts || []).forEach(wc => {
    const card = document.createElement("div");
    card.className = "breakdown-card";
    card.innerHTML = `
      <div class="breakdown-top">
        <span>${wc.concept}</span>
        <span style="color:var(--primary-saffron);">${wc.mastery || 55}%</span>
      </div>
      <p>${wc.note || 'Targeted review recommended.'}</p>
      <div class="mini-bar-bg"><div class="mini-bar-fill yellow" style="width:${wc.mastery || 55}%"></div></div>
    `;
    weakList.appendChild(card);
  });

  // Misconceptions Log
  const miscList = document.getElementById("reportMisconceptionsList");
  miscList.innerHTML = "";
  const miscs = report.misconceptions || [];
  if (miscs.length === 0) {
    miscList.innerHTML = `<div class="misconception-log-item" style="border-color:var(--accent-green); background:rgba(16,185,129,0.08);"><h5 style="color:var(--accent-green);">Zero Critical Misconceptions</h5><p>You grasped all explanations accurately on first pass!</p></div>`;
  } else {
    miscs.forEach(m => {
      const item = document.createElement("div");
      item.className = "misconception-log-item";
      item.innerHTML = `
        <h5><i class="fa-solid fa-triangle-exclamation"></i> ${m.title || 'Misunderstanding'}</h5>
        <p><strong>Fix:</strong> ${m.fix || m.description}</p>
      `;
      miscList.appendChild(item);
    });
  }

  // Revision Steps
  const stepsContainer = document.getElementById("reportRevisionSteps");
  stepsContainer.innerHTML = "";
  (report.revision_steps || []).forEach((step, idx) => {
    const stepCard = document.createElement("div");
    stepCard.className = "step-card";
    stepCard.innerHTML = `
      <div class="step-num">${idx + 1}</div>
      <p>${step}</p>
    `;
    stepsContainer.appendChild(stepCard);
  });

  // Next Recommended Topics
  const nextContainer = document.getElementById("reportNextTopicsList");
  nextContainer.innerHTML = "";
  (report.next_recommended_topics || []).forEach(t => {
    const nCard = document.createElement("div");
    nCard.className = "next-card";
    nCard.onclick = () => {
      setTopic(t.title);
      switchView("viewDashboard");
    };
    nCard.innerHTML = `
      <div class="next-card-info">
        <h4>${t.title}</h4>
        <p>${t.reason || 'Optimal continuation'}</p>
      </div>
      <button class="btn-primary btn-sm"><i class="fa-solid fa-play"></i> Start</button>
    `;
    nextContainer.appendChild(nCard);
  });
}

function returnToDashboard() {
  switchView("viewDashboard");
}

function confirmExitClassroom() {
  if (confirm("Are you sure you want to return to dashboard?")) {
    const audio = document.getElementById("lessonAudioElement");
    audio.pause();
    switchView("viewDashboard");
  }
}

// ==========================================================================
// MODALS & SETTINGS
// ==========================================================================

function showProfileModal() {
  const modal = document.getElementById("profileModal");
  const body = document.getElementById("profileModalBody");
  const p = STATE.studentProfile || {};

  body.innerHTML = `
    <div style="display:flex; align-items:center; gap:1.25rem; margin-bottom:1.5rem;">
      <div class="avatar-circle" style="width:56px; height:56px; font-size:1.5rem;"><i class="fa-solid fa-user-astronaut"></i></div>
      <div>
        <h4 style="font-size:1.2rem;">${p.student_name || 'Aarav Sharma'}</h4>
        <span style="font-size:0.85rem; color:var(--primary-saffron); font-weight:600;"><i class="fa-solid fa-bolt"></i> ${p.total_xp || 1450} Total XP · ${p.streak_days || 4} Day Streak</span>
      </div>
    </div>

    <div style="margin-bottom:1.25rem;">
      <h5 style="font-size:0.9rem; color:var(--text-muted); margin-bottom:0.5rem;">Recent Completed Topics</h5>
      ${(p.completed_topics || []).map(t => `
        <div style="display:flex; justify-content:space-between; background:var(--bg-card-elevated); padding:0.6rem 0.85rem; border-radius:8px; margin-bottom:0.4rem; font-size:0.85rem;">
          <span>${t.topic}</span>
          <strong style="color:var(--accent-green);">${t.score}% (${t.grade})</strong>
        </div>
      `).join('')}
    </div>
  `;

  modal.classList.add("open");
}

function hideProfileModal() {
  document.getElementById("profileModal").classList.remove("open");
}

function showSettingsModal() {
  document.getElementById("settingsModal").classList.add("open");
}

function hideSettingsModal() {
  document.getElementById("settingsModal").classList.remove("open");
}

function hideModals(e) {
  if (e.target.classList.contains("modal-backdrop")) {
    e.target.classList.remove("open");
  }
}

async function saveApiKey(e) {
  e.preventDefault();
  const key = document.getElementById("groqApiKeyInput").value.trim();
  const statusMsg = document.getElementById("apiKeySaveStatus");

  try {
    const res = await fetch("/api/settings/key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: key })
    });

    if (res.ok) {
      statusMsg.style.color = "var(--accent-green)";
      statusMsg.textContent = "✓ Groq API Key updated successfully!";
      setTimeout(() => hideSettingsModal(), 1500);
    } else {
      statusMsg.style.color = "var(--accent-red)";
      statusMsg.textContent = "Failed to update key.";
    }
  } catch (err) {
    statusMsg.style.color = "var(--accent-red)";
    statusMsg.textContent = "Error: " + err.message;
  }
}

// Utility
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag)
  );
}
