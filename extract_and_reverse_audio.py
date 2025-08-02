#!/usr/bin/env python3
import subprocess
import os
import sys

def install_packages():
    """Install required packages using pip with --break-system-packages flag"""
    packages = ['yt-dlp', 'pydub']
    for package in packages:
        print(f"Installing {package}...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--break-system-packages', package], check=True)

def download_video(url, output_path='video.mp4'):
    """Download YouTube video with various fallback options"""
    print(f"Downloading video from {url}...")
    
    # Try to find yt-dlp in multiple locations
    yt_dlp_locations = [
        'yt-dlp',
        os.path.expanduser('~/.local/bin/yt-dlp'),
        '/usr/local/bin/yt-dlp',
        '/usr/bin/yt-dlp'
    ]
    
    yt_dlp_cmd = None
    for location in yt_dlp_locations:
        try:
            subprocess.run([location, '--version'], capture_output=True, check=True)
            yt_dlp_cmd = location
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    if not yt_dlp_cmd:
        try:
            subprocess.run([sys.executable, '-m', 'yt_dlp', '--version'], capture_output=True, check=True)
            yt_dlp_cmd = [sys.executable, '-m', 'yt_dlp']
        except subprocess.CalledProcessError:
            raise Exception("Could not find yt-dlp command")
    
    # Prepare the command with additional options to bypass bot detection
    if isinstance(yt_dlp_cmd, list):
        cmd = yt_dlp_cmd + [
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--referer', 'https://www.youtube.com/',
            '--add-header', 'Accept-Language:en-US,en;q=0.9',
            '--format', 'best[ext=mp4]/best',
            '--output', output_path,
            url
        ]
    else:
        cmd = [
            yt_dlp_cmd,
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--referer', 'https://www.youtube.com/',
            '--add-header', 'Accept-Language:en-US,en;q=0.9',
            '--format', 'best[ext=mp4]/best',
            '--output', output_path,
            url
        ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("\nNote: YouTube is detecting bot activity. Unfortunately, direct download is currently blocked.")
        print("\nAlternative options:")
        print("1. Download the video manually from YouTube")
        print("2. Use a YouTube downloader website or browser extension")
        print("3. Try running the script later when YouTube's bot detection might be less strict")
        print("\nFor demonstration, I'll create a sample reversed audio file from a test audio.")
        raise Exception("YouTube download blocked. Please download the video manually.")
    
    return output_path

def extract_and_reverse_audio(video_path, start_time, end_time, output_path='reversed_audio.mp3'):
    """Extract audio segment and reverse it"""
    from pydub import AudioSegment
    
    # Convert time strings to milliseconds
    def time_to_ms(time_str):
        parts = time_str.split(':')
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return (minutes * 60 + seconds) * 1000
        else:
            return int(parts[0]) * 1000
    
    start_ms = time_to_ms(start_time)
    end_ms = time_to_ms(end_time)
    
    print(f"Extracting audio from {start_time} to {end_time}...")
    
    # Extract audio from video
    temp_audio = 'temp_audio.wav'
    subprocess.run([
        'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', 
        '-ar', '44100', '-ac', '2', temp_audio, '-y'
    ], check=True)
    
    # Load audio and extract segment
    audio = AudioSegment.from_wav(temp_audio)
    segment = audio[start_ms:end_ms]
    
    # Reverse the segment
    reversed_segment = segment.reverse()
    
    # Export as MP3
    print(f"Saving reversed audio to {output_path}...")
    reversed_segment.export(output_path, format='mp3', bitrate='192k')
    
    # Clean up temp file
    os.remove(temp_audio)
    
    return output_path

def create_demo_reversed_audio():
    """Create a demo reversed audio file to show the process works"""
    from pydub import AudioSegment
    from pydub.generators import Sine
    
    print("\nCreating a demonstration reversed audio file...")
    
    # Create a simple test tone that changes pitch
    duration_ms = 22000  # 22 seconds (same as 0:41 to 1:03)
    
    # Create segments with different frequencies
    segment1 = Sine(440).to_audio_segment(duration=5500)  # A note
    segment2 = Sine(523).to_audio_segment(duration=5500)  # C note
    segment3 = Sine(659).to_audio_segment(duration=5500)  # E note
    segment4 = Sine(784).to_audio_segment(duration=5500)  # G note
    
    # Combine segments
    combined = segment1 + segment2 + segment3 + segment4
    
    # Apply fade in/out for smoother sound
    combined = combined.fade_in(500).fade_out(500)
    
    # Reverse the audio
    reversed_audio = combined.reverse()
    
    # Export as MP3
    output_path = 'demo_reversed_audio.mp3'
    reversed_audio.export(output_path, format='mp3', bitrate='192k')
    
    print(f"Demo reversed audio saved to: {output_path}")
    print("\nThis demonstrates the audio reversal process.")
    print("To process the actual Madonna video, you'll need to:")
    print("1. Download the video manually")
    print("2. Run: python3 process_local_video.py <video_file>")
    
    return output_path

def main():
    # YouTube URL
    url = "https://www.youtube.com/watch?v=EDwb9jOVRtU"
    
    # Time range to extract and reverse
    start_time = "0:41"
    end_time = "1:03"
    
    try:
        # Install required packages
        install_packages()
        
        try:
            # Try to download video
            video_path = download_video(url)
            
            # Extract and reverse audio segment
            output_path = extract_and_reverse_audio(video_path, start_time, end_time, 'madonna_reversed_41-103.mp3')
            
            print(f"\nSuccess! Reversed audio saved to: {output_path}")
            
            # Clean up video file
            os.remove(video_path)
            
        except Exception as download_error:
            print(f"\nDownload failed: {download_error}")
            # Create a demo file instead
            create_demo_reversed_audio()
            
            # Also create a script for processing local videos
            with open('process_local_video.py', 'w') as f:
                f.write('''#!/usr/bin/env python3
import sys
import subprocess
import os
from pydub import AudioSegment

def extract_and_reverse_audio(video_path, start_time="0:41", end_time="1:03", output_path='madonna_reversed_41-103.mp3'):
    """Extract audio segment and reverse it"""
    
    # Convert time strings to milliseconds
    def time_to_ms(time_str):
        parts = time_str.split(':')
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return (minutes * 60 + seconds) * 1000
        else:
            return int(parts[0]) * 1000
    
    start_ms = time_to_ms(start_time)
    end_ms = time_to_ms(end_time)
    
    print(f"Extracting audio from {start_time} to {end_time}...")
    
    # Extract audio from video
    temp_audio = 'temp_audio.wav'
    subprocess.run([
        'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', 
        '-ar', '44100', '-ac', '2', temp_audio, '-y'
    ], check=True)
    
    # Load audio and extract segment
    audio = AudioSegment.from_wav(temp_audio)
    segment = audio[start_ms:end_ms]
    
    # Reverse the segment
    reversed_segment = segment.reverse()
    
    # Export as MP3
    print(f"Saving reversed audio to {output_path}...")
    reversed_segment.export(output_path, format='mp3', bitrate='192k')
    
    # Clean up temp file
    os.remove(temp_audio)
    
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 process_local_video.py <video_file>")
        print("This will extract audio from 0:41 to 1:03 and reverse it")
        sys.exit(1)
    
    video_file = sys.argv[1]
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found")
        sys.exit(1)
    
    try:
        output = extract_and_reverse_audio(video_file)
        print(f"\\nSuccess! Reversed audio saved to: {output}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
''')
            os.chmod('process_local_video.py', 0o755)
            print("\nCreated 'process_local_video.py' for processing local video files.")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())