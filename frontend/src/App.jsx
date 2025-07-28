import React, { useState, useCallback, useRef } from 'react';
import { useReactMediaRecorder } from 'react-media-recorder';
import './App.css';

const Header = () => {
    return (
        <header className="header">
            <div className="header-logo">
                <div className="header-icon">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.79 2-4 2s-4-.895-4-2 1.79-2 4-2 4 .895 4 2zm-4 0V5m0 0a2 2 0 100-4 2 2 0 000 4zm0 0L9 3"></path></svg>
                </div>
                <span className="header-title">Meeting Insights AI</span>
            </div>
            <nav className="header-nav">
                <a href="#">Help</a>
                <a href="#">Contact</a>
            </nav>
        </header>
    );
};

const FeatureIcons = () => {
    const features = [
        { icon: '🎤', text: 'Analyze Audio' },
        { icon: '🎥', text: 'Analyze Video' },
        { icon: '📄', text: 'Process Transcript' },
        { icon: '📝', text: 'Generate Summaries' },
        { icon: '💡', text: 'Extract Insights' },
    ];

    return (
        <div className="feature-icons-container">
            {features.map((feature, index) => (
                <div key={index} className="feature-item">
                    <span className="feature-icon-emoji">{feature.icon}</span>
                    {feature.text}
                </div>
            ))}
        </div>
    );
};

const MeetingAnalysisDisplay = ({ meeting }) => {
    if (!meeting) {
        return <div className="text-center text-gray-600">No meeting data to display.</div>;
    }

    const renderList = (items, renderItem) => {
        if (!items || items.length === 0) {
            return <p className="text-gray-600 italic">No items identified.</p>;
        }
        return (
            <ul className="list-container">
                {items.map((item, index) => (
                    <li key={index} className="list-item">
                        {renderItem(item)}
                    </li>
                ))}
            </ul>
        );
    };

    return (
        <div className="analysis-display-card">
            <h2 className="analysis-header">Meeting Analysis Results</h2>

            <div className="analysis-meta-grid">
                <p className="analysis-meta-text">
                    <span className="font-semibold">Meeting ID:</span> <span className="font-mono break-all">{meeting.meeting_id}</span>
                </p>
                <p className="analysis-meta-text">
                    <span className="font-semibold">Timestamp:</span> <span className="font-semibold">{new Date(meeting.timestamp).toLocaleString()}</span>
                </p>
            </div>

            <div className="mb-8">
                <h3 className="analysis-section-title">
                    <span style={{ color: '#3b82f6' }}>📝</span> Summary:
                </h3>
                <p className="summary-content">
                    {meeting.summary}
                </p>
            </div>

            <div className="mb-8">
                <h3 className="analysis-section-title">
                    <span style={{ color: '#22c55e' }}>✅</span> Action Items:
                </h3>
                {renderList(meeting.action_items, (item) => (
                    <>
                        <p className="font-medium">Task: <span className="font-normal">{item.task}</span></p>
                        <p className="text-sm">Assignee: <span className="font-normal">{item.assignee || 'N/A'}</span></p>
                        <p className="text-sm">Deadline: <span className="font-normal">{item.deadline || 'N/A'}</span></p>
                        <p className="text-sm">Status: <span className={`font-semibold ${item.status === 'completed' ? 'text-green-600' : item.status === 'in-progress' ? 'text-yellow-600' : 'text-red-600'}`}>{item.status}</span></p>
                    </>
                ))}
            </div>

            <div className="mb-8">
                <h3 className="analysis-section-title">
                    <span style={{ color: '#a855f7' }}>💡</span> Key Decisions:
                </h3>
                {renderList(meeting.key_decisions, (decision) => (
                    <>
                        <p className="font-medium">Decision: <span className="font-normal">{decision.description}</span></p>
                        <p className="text-sm">Participants: <span className="font-normal">{decision.participants_involved.join(', ') || 'N/A'}</span></p>
                        <p className="text-sm">Date Made: <span className="font-normal">{decision.date_made || 'N/A'}</span></p>
                    </>
                ))}
            </div>

            <div className="context-grid">
                {meeting.speakers_detected && meeting.speakers_detected.length > 0 && (
                    <div className="context-item">
                        <h4><span style={{ color: '#ec4899' }}>🗣️</span> Speakers:</h4>
                        <p>{meeting.speakers_detected.join(', ')}</p>
                    </div>
                )}
                {meeting.tone_overview && (
                    <div className="context-item">
                        <h4><span style={{ color: '#f97316' }}>🎶</span> Overall Tone:</h4>
                        <p>{meeting.tone_overview}</p>
                    </div>
                )}
                {meeting.important_topics && meeting.important_topics.length > 0 && (
                    <div className="context-item">
                        <h4><span style={{ color: '#14b8a6' }}>🎯</span> Key Topics:</h4>
                        <ul className="list-disc pl-5">
                            {meeting.important_topics.map((topic, index) => (
                                <li key={index}>{topic}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {meeting.raw_transcript_preview && (
                <div className="transcript-preview-container">
                    <h3 className="analysis-section-title">
                        <span style={{ color: '#6b7280' }}>📄</span> Raw Transcript Preview:
                    </h3>
                    <div className="transcript-preview-content">
                        {meeting.raw_transcript_preview}
                    </div>
                </div>
            )}
        </div>
    );
};

const ExportOptions = ({ meetingAnalysis, setError }) => {
    const [slackChannel, setSlackChannel] = useState('');
    const [emailRecipient, setEmailRecipient] = useState('');
    const [exportFormat, setExportFormat] = useState('summary_and_tasks');
    const [exportMessage, setExportMessage] = useState('');
    const [loading, setLoading] = useState({
        slack: false,
        email: false
    });

    const handleExport = useCallback(async (type) => {
        setLoading((prev) => ({ ...prev, [type]: true }));
        setExportMessage('');
        setError(null);

        try {
            let response;
            let payload;
            let url;

            if (type === 'slack') {
                if (!slackChannel) {
                    throw new Error("Slack Channel ID is required.");
                }
                url = 'http://localhost:8000/export/slack';
                payload = {
                    meeting_analysis: meetingAnalysis,
                    slack_channel_id: slackChannel,
                    export_format: exportFormat
                };
            } else if (type === 'email') {
                if (!emailRecipient) {
                    throw new Error("Email Recipient is required.");
                }
                url = `http://localhost:8000/export/email?recipient=${encodeURIComponent(emailRecipient)}`;
                payload = meetingAnalysis;
            }  else {
                throw new Error("Invalid export type.");
            }

            response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Failed to export to ${type}.`);
            }

            const data = await response.json();
            setExportMessage(`Successfully exported to ${type}!`);
            console.log(`Export to ${type} successful:`, data);
        } catch (err) {
            console.error(`Error exporting to ${type}:`, err);
            setError(err.message || `An unexpected error occurred during ${type} export.`);
        } finally {
           setLoading((prev) => ({ ...prev, [type]: false }));
        }
    }, [meetingAnalysis, slackChannel, emailRecipient, exportFormat, setError]);


    return (
        <div className="export-options-card">
            <h2 className="export-header">Export Options</h2>

            {exportMessage && (
                <div className="export-message-alert" role="alert">
                    <span className="block sm:inline">{exportMessage}</span>
                </div>
            )}

            <div className="export-options-space">
                <div className="export-section">
                    <h3 className="export-section-title"><span style={{ color: '#7c3aed' }}>💬</span> Export to Slack</h3>
                    <div className="export-input-group">
                        <input
                            type="text"
                            placeholder="Slack Channel ID (e.g., C1234567890)"
                            value={slackChannel}
                            onChange={(e) => setSlackChannel(e.target.value)}
                            className="export-input"
                        />
                        <select
                            value={exportFormat}
                            onChange={(e) => setExportFormat(e.target.value)}
                            className="export-select"
                        >
                            <option value="summary_and_tasks">Summary & Tasks</option>
                            <option value="summary_only">Summary Only</option>
                            <option value="tasks_only">Tasks Only</option>
                        </select>
                        <button
                            onClick={() => handleExport('slack')}
                            disabled={loading.slack || !meetingAnalysis}
                            className="export-button slack"
                        >
                            {loading.slack ? 'Sending...' : 'Send to Slack'}
                        </button>

                    </div>
                </div>

                <div className="export-section">
                    <h3 className="export-section-title"><span style={{ color: '#dc2626' }}>📧</span> Export via Email</h3>
                    <div className="export-input-group">
                        <input
                            type="email"
                            placeholder="Recipient Email Address"
                            value={emailRecipient}
                            onChange={(e) => setEmailRecipient(e.target.value)}
                            className="export-input"
                        />
                        <button
                            onClick={() => handleExport('email')}
                            disabled={loading.email || !meetingAnalysis}
                            className="export-button email"
                        >
                            {loading.email ? 'Sending...' : 'Send Email'}
                        </button>

                    </div>
                </div>

                
            </div>
        </div>
    );
};

const App = () => {
    const [meetingAnalysis, setMeetingAnalysis] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [fileType, setFileType] = useState('audio_video');
    const [selectedFile, setSelectedFile] = useState(null);
    const fileInputRef = useRef(null);
    const [recordedBlob, setRecordedBlob] = useState(null);

    const {
        startRecording,
        stopRecording,
        mediaBlobUrl,
        status,
        clearBlobUrl
    } = useReactMediaRecorder({ audio: true, onStop: (blobUrl, blob) => {
        const file = new File([blob], 'recording.wav', { type: 'audio/wav' });
        setSelectedFile(file);
        setRecordedBlob(blobUrl);
    }});

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
        setError(null);
    };

    const handleFileTypeChange = (type) => {
        setFileType(type);
        setSelectedFile(null);
        setError(null);
        setRecordedBlob(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleUploadClick = () => {
        fileInputRef.current.click();
    };

    const handleDrop = (event) => {
        event.preventDefault();
        event.stopPropagation();
        if (event.dataTransfer.files && event.dataTransfer.files[0]) {
            setSelectedFile(event.dataTransfer.files[0]);
            setError(null);
        }
    };

    const handleDragOver = (event) => {
        event.preventDefault();
        event.stopPropagation();
    };

    const handleSubmit = async () => {
        if (!selectedFile) {
            setError(`Please select or record a valid file.`);
            return;
        }

        setIsLoading(true);
        setError(null);
        setMeetingAnalysis(null);

        const formData = new FormData();
        formData.append('file', selectedFile);

        // Detect file type using MIME or extension
        const fileType = selectedFile.type;
        const fileName = selectedFile.name.toLowerCase();
        const isTextFile = fileType === 'text/plain' || fileName.endsWith('.txt');

        // Choose correct endpoint
        const endpoint = isTextFile
            ? 'http://localhost:8000/analyze/'
            : 'http://localhost:8000/transcribe-and-analyze/';

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to analyze meeting.');
            }

            const data = await response.json();
            setMeetingAnalysis(data);
        } catch (err) {
            setError(err.message || 'Unexpected error during analysis.');
        } finally {
            setIsLoading(false);
            setSelectedFile(null);
            setRecordedBlob(null);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };


    return (
        <div className="app-container">
            <Header />

            <main className="main-content">
                <FeatureIcons />

                <div className="upload-card">
                    <div className="ai-powered-badge">
                        <span className="mr-1">✨</span> AI powered
                    </div>

                    <div className="upload-card-header">
                        <h2 className="upload-card-title">
                            Transform Your Meetings into Actionable Insights
                        </h2>
                        <p className="upload-card-subtitle">
                            Accurate transcription and intelligent analysis for better productivity.
                        </p>
                    </div>

                    <div className="file-type-selector">
                        <div className="segmented-control">
                            <button
                                type="button"
                                onClick={() => handleFileTypeChange('audio_video')}
                                className={fileType === 'audio_video' ? 'active' : ''}
                            >
                                Audio/Video File
                            </button>
                            <button
                                type="button"
                                onClick={() => handleFileTypeChange('transcript')}
                                className={fileType === 'transcript' ? 'active' : ''}
                            >
                                Text Transcript
                            </button>
                            <button
                                type="button"
                                onClick={() => handleFileTypeChange('record_audio')}
                                className={fileType === 'record_audio' ? 'active' : ''}
                            >
                                Record Audio
                            </button>
                        </div>
                    </div>

                    <div
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                        className="drop-area"
                    >
                        {fileType !== 'record_audio' && (
                            <>
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handleFileChange}
                                    accept={fileType === 'audio_video' ? 'audio/*,video/*' : '.txt,text/plain'}
                                    className="hidden"
                                />
                                <button
                                    type="button"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleUploadClick();
                                    }}
                                    className="choose-file-button"
                                >
                                    Choose a file
                                </button>
                                <p className="drag-drop-text">or drag and drop a file</p>
                            </>
                        )}

                        {fileType === 'record_audio' && (
                            <div className="text-center mb-4">
                                <p>Status: <strong>{status}</strong></p>
                                <div className="flex gap-4 justify-center mt-3 ">
                                    <button onClick={startRecording} disabled={status === "recording"} className="choose-file-button">Start Recording</button>
                                    <button onClick={stopRecording} disabled={status !== "recording"} className="choose-file-button">Stop Recording</button>
                                </div>
                                {mediaBlobUrl && (
                                    <div className="mt-4">
                                        <audio controls src={mediaBlobUrl} className="w-full"></audio>
                                    </div>
                                )}
                            </div>
                        )}

                        {selectedFile && (
                            <>
                                <p className="selected-file-info">
                                    Selected: <span className="selected-file-name">{selectedFile.name}</span>
                                </p>
                                <button
                                    onClick={handleSubmit}
                                    disabled={isLoading}
                                    className="start-analysis-button"
                                >
                                    {isLoading ? 'Analyzing...' : 'Start Analysis'}
                                </button>
                            </>
                        )}
                    </div>
                </div>

                {error && (
                    <div className="error-alert" role="alert">
                        <strong>Error!</strong>
                        <span className="block sm:inline">{error}</span>
                    </div>
                )}

                {isLoading && (
                    <div className="loading-container">
                        <div className="loader"></div>
                        <p className="loading-text">Processing your meeting data...</p>
                    </div>
                )}

                {!isLoading && meetingAnalysis && (
                    <>
                        <MeetingAnalysisDisplay meeting={meetingAnalysis} />
                        <ExportOptions meetingAnalysis={meetingAnalysis} setError={setError} />
                    </>
                )}
            </main>
        </div>
    );
};

export default App;