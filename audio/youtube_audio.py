# Module handles url extraction using yt-dlp and FFmpeg for audio processing
# Also handles SSL certificate issues common for different platforms

import sys
import os
import subprocess
import io
import ssl
import re
from typing import Optional
from pydub import AudioSegment
from yt_dlp import YoutubeDL


def get_ffmpeg_path() -> Optional[str]:

    # Returns the path to the FFmpeg executable, handling deployment scenarios

    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "ffmpeg")
    return "ffmpeg"


def normalize_youtube_url(url: str) -> str:
    
    # Regular expressions to extract video ID from different YouTube URL formats
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            # Return normalized URL format
            return f"https://www.youtube.com/watch?v={video_id}"
    
    # If no pattern matches, return the original URL
    # This allows yt-dlp to handle edge cases or provide its own error
    return url


class YouTubeAudio:

    # Handles extracting and processing audio from YouTube videos

    def __init__(self, sample_rate: int = 44100):
        self.target_sample_rate = sample_rate
        self.ffmpeg_path = get_ffmpeg_path()
        self.video_title = None

    def fetch(self, youtube_url: str) -> AudioSegment:

        # Extract audio from a YouTube video and return it as an AudioSegment
        try:
            audio_source_url = self.extract_audio_url(youtube_url)
            raw_audio_data = self.download_audio_data(audio_source_url)
            return self.convert_to_audio_segment(raw_audio_data)
            
        except Exception as error:
            self.handle_fetch_error(error)

    def extract_audio_url(self, youtube_url: str) -> str:

        # Extracts the direct audio stream URL from a YouTube video
        
        # Normalize the YouTube URL to improve compatibility
        normalized_url = normalize_youtube_url(youtube_url)

        # Configure yt-dlp options for audio extraction
        ydl_options = {
            "format": "bestaudio/best",         
            "quiet": True,                       
            "no_warnings": True,                
            "skip_download": True,               
            "nocheckcertificate": True,           # Bypass SSL certificate verification
            "ignoreerrors": False,               
            "extractaudio": False,               
            "audioformat": "best",             
        }
        
        with YoutubeDL(ydl_options) as ydl:
            # Extract video metadata without downloading the actual file
            video_info = ydl.extract_info(normalized_url, download=False)
            
            # Store the video title for later use
            self.video_title = video_info.get('title', 'Unknown Song')
            
            if "url" in video_info:
                return video_info["url"]
            else:
                return self.find_best_audio_format(video_info)

    def find_best_audio_format(self, video_info: dict) -> str:

        # This selects the best audio format when multiple exist
        formats = video_info.get("formats", [])
        audio_formats = [format_info for format_info in formats if format_info.get("acodec") != "none"]
        
        if not audio_formats:
            raise RuntimeError("No audio formats found")
        return audio_formats[-1]["url"]

    def download_audio_data(self, audio_source_url: str) -> bytes:
        # Download audio using extracted url using FFmpeg

        ffmpeg_command = [
            self.ffmpeg_path,               
            "-i", audio_source_url,         
            "-f", "wav",                          
            "-ar", str(self.target_sample_rate),     
            "-ac", "2",                           
            "pipe:1",                             
        ]
        
        # Configure environment to handle SSL certificate issues
        environment = os.environ.copy()
        environment['CURL_CA_BUNDLE'] = ''           
        

        process = subprocess.Popen(
            ffmpeg_command, 
            stdout=subprocess.PIPE,                  
            stderr=subprocess.DEVNULL,          
            env=environment
        )
        

        raw_audio_data = process.stdout.read()
        process.stdout.close()
        process.wait()


        if process.returncode != 0:
            raise RuntimeError("FFmpeg failed to process audio")

        return raw_audio_data

    def convert_to_audio_segment(self, raw_audio_data: bytes) -> AudioSegment:
        # Convert raw audio bytes to a pydub AudioSegment.

        return AudioSegment.from_file(io.BytesIO(raw_audio_data), format="wav")

    def handle_fetch_error(self, error: Exception):

        error_message = str(error).lower()
        
        # Handle SSL certificate errors
        if "certificate" in error_message or "ssl" in error_message:
            raise RuntimeError(
                f"SSL certificate error: {error}\n"
                "This is a common issue on macOS. Try updating yt-dlp:\n"
                "pip install --upgrade yt-dlp"
            )
        else:
            raise RuntimeError(f"Failed to fetch audio from YouTube: {error}")
