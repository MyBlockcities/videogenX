import React, { useState } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import axios from 'axios';
import {
  CloudArrowUpIcon,
  DocumentTextIcon,
  SparklesIcon,
  VideoCameraIcon,
} from '@heroicons/react/24/outline';

function App() {
  const [url, setUrl] = useState('');
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('transcript');

  const getSourceIcon = (sourceType) => {
    switch (sourceType) {
      case 'youtube':
        return '🎥';
      case 'instagram':
        return '📸';
      case 'facebook':
        return '👥';
      case 'tiktok':
        return '🎵';
      default:
        return '🎬';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!url) {
      toast.error('Please enter a video URL');
      return;
    }

    setProcessing(true);
    setResult(null);

    try {
      const toastId = toast.loading('Processing video...');
      
      const response = await axios.post('/api/process', { url });
      
      if (response.data) {
        setResult(response.data);
        toast.update(toastId, {
          render: `Successfully processed ${getSourceIcon(response.data.source_type)} video!`,
          type: 'success',
          isLoading: false,
          autoClose: 3000
        });
      }
    } catch (error) {
      console.error('Processing error:', error);
      toast.error(
        error.response?.data?.detail || 
        error.message || 
        'An error occurred while processing the video'
      );
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Video Processor
          </h1>
          <p className="text-lg text-gray-600">
            Transform videos from multiple platforms into transcripts and summaries
          </p>
          <div className="mt-4 flex justify-center space-x-4">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              🎥 YouTube
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-pink-100 text-pink-800">
              📸 Instagram
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              👥 Facebook
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
              🎵 TikTok
            </span>
          </div>
        </div>

        {/* Main Form */}
        <div className="max-w-xl mx-auto">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Paste any video URL here... (YouTube, Instagram, Facebook, TikTok)"
                className="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500"
                disabled={processing}
              />
              <button
                type="submit"
                disabled={processing || !url}
                className={`mt-4 w-full flex items-center justify-center px-4 py-3 border border-transparent text-base font-medium rounded-md text-white ${
                  processing || !url
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-primary-600 hover:bg-primary-700'
                } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
              >
                {processing ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Processing Video...
                  </>
                ) : (
                  <>
                    <VideoCameraIcon className="w-5 h-5 mr-2" />
                    Process Video
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Results Section */}
        {result && (
          <div className="mt-12">
            <div className="bg-white shadow rounded-lg">
              {/* Source Type Badge */}
              <div className="px-6 pt-4">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                  {getSourceIcon(result.source_type)} {result.source_type.charAt(0).toUpperCase() + result.source_type.slice(1)}
                </span>
              </div>
              
              {/* Tabs */}
              <div className="border-b border-gray-200 mt-4">
                <nav className="-mb-px flex" aria-label="Tabs">
                  <button
                    onClick={() => setActiveTab('transcript')}
                    className={`${
                      activeTab === 'transcript'
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    } w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm`}
                  >
                    <DocumentTextIcon className="w-5 h-5 inline-block mr-2" />
                    Transcript
                  </button>
                  <button
                    onClick={() => setActiveTab('summary')}
                    className={`${
                      activeTab === 'summary'
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    } w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm`}
                  >
                    <SparklesIcon className="w-5 h-5 inline-block mr-2" />
                    Summary
                  </button>
                </nav>
              </div>

              {/* Content */}
              <div className="p-6">
                {activeTab === 'transcript' ? (
                  <div className="prose max-w-none">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">
                      Full Transcript
                    </h3>
                    <p className="whitespace-pre-wrap text-gray-700">
                      {result.transcript}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Brief Summary
                      </h3>
                      <p className="text-gray-700">{result.summary.brief}</p>
                    </div>
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Key Points
                      </h3>
                      <ul className="list-disc pl-5 space-y-2 text-gray-700">
                        {result.summary.keyPoints.map((point, index) => (
                          <li key={index}>{point}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Processing Steps */}
        <div className="mt-12 max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            How It Works
          </h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            <div className="text-center">
              <div className="mx-auto h-12 w-12 text-primary-500">
                <CloudArrowUpIcon className="h-12 w-12" />
              </div>
              <h3 className="mt-3 text-lg font-medium text-gray-900">
                1. Upload
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Paste any video URL
              </p>
            </div>
            <div className="text-center">
              <div className="mx-auto h-12 w-12 text-primary-500">
                <DocumentTextIcon className="h-12 w-12" />
              </div>
              <h3 className="mt-3 text-lg font-medium text-gray-900">
                2. Transcribe
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                AI converts speech to text
              </p>
            </div>
            <div className="text-center">
              <div className="mx-auto h-12 w-12 text-primary-500">
                <SparklesIcon className="h-12 w-12" />
              </div>
              <h3 className="mt-3 text-lg font-medium text-gray-900">
                3. Analyze
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Get summaries and insights
              </p>
            </div>
          </div>
        </div>
      </div>
      <ToastContainer position="bottom-right" />
    </div>
  );
}

export default App;
