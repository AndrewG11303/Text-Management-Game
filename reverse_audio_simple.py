#!/usr/bin/env python3
import subprocess
import os
import sys

def download_video_with_ytdlp(url, output_path='video.mp4'):
    """Try to download YouTube video"""
    print(f"Attempting to download video from {url}...")
    
    # Try different yt-dlp locations
    yt_dlp_cmd = None
    for cmd in [os.path.expanduser('~/.local/bin/yt-dlp'), 'yt-dlp', sys.executable + ' -m yt_dlp']:
        try:
            test_cmd = cmd.split() if ' ' in cmd else [cmd]
            subprocess.run(test_cmd + ['--version'], capture_output=True, check=True)
            yt_dlp_cmd = cmd
            break
        except:
            continue
    
    if not yt_dlp_cmd:
        return None
    
    # Try to download
    cmd = yt_dlp_cmd.split() if ' ' in yt_dlp_cmd else [yt_dlp_cmd]
    cmd.extend([
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        '-f', 'best[ext=mp4]/best',
        '-o', output_path,
        url
    ])
    
    try:
        subprocess.run(cmd, check=True)
        return output_path
    except:
        return None

def extract_and_reverse_audio_ffmpeg(input_file, start_time, end_time, output_file):
    """Extract audio segment and reverse it using ffmpeg only"""
    print(f"\nExtracting audio from {start_time} to {end_time} and reversing...")
    
    # Calculate duration
    start_parts = start_time.split(':')
    end_parts = end_time.split(':')
    
    start_seconds = int(start_parts[0]) * 60 + int(start_parts[1]) if len(start_parts) == 2 else int(start_parts[0])
    end_seconds = int(end_parts[0]) * 60 + int(end_parts[1]) if len(end_parts) == 2 else int(end_parts[0])
    duration = end_seconds - start_seconds
    
    # Extract and reverse in one command
    cmd = [
        'ffmpeg',
        '-ss', str(start_seconds),  # Start time
        '-t', str(duration),        # Duration
        '-i', input_file,           # Input file
        '-af', 'areverse',          # Audio filter: reverse
        '-acodec', 'libmp3lame',    # MP3 codec
        '-b:a', '192k',             # Bitrate
        '-y',                       # Overwrite output
        output_file
    ]
    
    subprocess.run(cmd, check=True)
    print(f"Reversed audio saved to: {output_file}")

def create_test_audio():
    """Create a test audio file to demonstrate the reversal"""
    print("\nCreating a test audio file...")
    
    # Generate a 22-second test tone that changes frequency
    test_file = 'test_audio.mp3'
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'sine=frequency=440:duration=5.5,sine=frequency=523:duration=5.5,sine=frequency=659:duration=5.5,sine=frequency=784:duration=5.5',
        '-t', '22',
        '-acodec', 'libmp3lame',
        '-b:a', '192k',
        '-y',
        test_file
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return test_file
    except:
        # Simpler approach
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', 'sine=frequency=440:duration=22',
            '-acodec', 'libmp3lame',
            '-b:a', '192k',
            '-y',
            test_file
        ]
        subprocess.run(cmd, check=True)
        return test_file

def main():
    url = "https://www.youtube.com/watch?v=EDwb9jOVRtU"
    start_time = "0:41"
    end_time = "1:03"
    output_file = "madonna_reversed_41-103.mp3"
    
    # Try to download the video
    video_file = download_video_with_ytdlp(url)
    
    if video_file and os.path.exists(video_file):
        # Process the actual video
        try:
            extract_and_reverse_audio_ffmpeg(video_file, start_time, end_time, output_file)
            os.remove(video_file)  # Clean up
            print("\nSuccess! The reversed audio has been created.")
        except Exception as e:
            print(f"Error processing video: {e}")
    else:
        print("\nYouTube download was blocked. Creating a demonstration file instead...")
        
        # Create test audio
        test_file = create_test_audio()
        
        # Reverse the test audio
        demo_output = "demo_reversed_audio.mp3"
        extract_and_reverse_audio_ffmpeg(test_file, "0:0", "0:22", demo_output)
        
        # Clean up
        os.remove(test_file)
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETE")
        print("="*60)
        print("\nA demo reversed audio file has been created.")
        print("\nTo process the actual Madonna video:")
        print("1. Download the video manually from:", url)
        print("2. Save it as 'madonna_video.mp4'")
        print("3. Run this command:")
        print(f"   ffmpeg -ss 41 -t 22 -i madonna_video.mp4 -af areverse -acodec libmp3lame -b:a 192k {output_file}")
        print("\nThis will extract the audio from 0:41 to 1:03 and reverse it.")

if __name__ == "__main__":
    main()