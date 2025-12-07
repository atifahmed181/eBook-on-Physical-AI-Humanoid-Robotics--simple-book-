---
sidebar_position: 2
---

# Voice-to-Action: Using OpenAI Whisper for Voice Commands

## Introduction to Voice-to-Action Systems

Voice-to-Action systems enable humanoid robots to receive and interpret spoken commands, transforming natural language into executable actions. This technology forms the foundation of intuitive human-robot interaction, allowing users to communicate with robots using everyday language rather than specialized commands.

In this chapter, we'll explore how OpenAI Whisper, a state-of-the-art speech recognition system, can be integrated with ROS 2 to create responsive voice-controlled humanoid robots.

## Understanding OpenAI Whisper

OpenAI Whisper is a robust automatic speech recognition (ASR) system trained on a vast dataset of audio and text. It excels at:
- Multilingual speech recognition
- Robust performance in noisy environments
- Accurate transcription of spoken commands
- Real-time processing capabilities

### Whisper Architecture
Whisper uses a Transformer-based architecture with both encoder and decoder components. The encoder processes audio input and the decoder generates text transcriptions, making it ideal for voice-to-action applications.

## Setting up Whisper for Robotics

### Installation
```bash
# Install Whisper and dependencies
pip install openai-whisper
pip install pyaudio  # For audio capture
pip install sounddevice  # Alternative audio library
```

### Basic Whisper Node
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import whisper
import pyaudio
import numpy as np
import threading
import queue
import time

class VoiceToActionNode(Node):
    def __init__(self):
        super().__init__('voice_to_action_node')
        
        # Load Whisper model
        self.get_logger().info('Loading Whisper model...')
        self.model = whisper.load_model("base")  # or "small", "medium", "large"
        self.get_logger().info('Whisper model loaded successfully')
        
        # Audio parameters
        self.audio_format = pyaudio.paFloat32
        self.channels = 1
        self.rate = 16000  # Whisper works best at 16kHz
        self.chunk = 1024
        self.audio_buffer = queue.Queue()
        
        # ROS publishers
        self.transcription_pub = self.create_publisher(String, 'voice_transcription', 10)
        self.command_pub = self.create_publisher(String, 'robot_command', 10)
        
        # Start audio capture in a separate thread
        self.audio_thread = threading.Thread(target=self.capture_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
        # Timer for processing audio chunks
        self.process_timer = self.create_timer(2.0, self.process_audio_chunk)
        
        self.get_logger().info('Voice-to-Action node initialized')

    def capture_audio(self):
        """Capture audio from microphone in a separate thread"""
        p = pyaudio.PyAudio()
        
        stream = p.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        self.get_logger().info('Audio capture started')
        
        while rclpy.ok():
            try:
                data = stream.read(self.chunk)
                audio_data = np.frombuffer(data, dtype=np.float32)
                self.audio_buffer.put(audio_data)
            except Exception as e:
                self.get_logger().error(f'Audio capture error: {e}')
                break
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    def process_audio_chunk(self):
        """Process accumulated audio data for transcription"""
        if self.audio_buffer.empty():
            return
            
        # Collect audio data from buffer
        audio_data = []
        while not self.audio_buffer.empty():
            chunk = self.audio_buffer.get()
            audio_data.append(chunk)
        
        if len(audio_data) == 0:
            return
            
        # Concatenate audio chunks
        full_audio = np.concatenate(audio_data)
        
        # Ensure we have enough audio data to process
        if len(full_audio) < 16000 * 0.5:  # Minimum 0.5 seconds of audio
            return
            
        try:
            # Transcribe the audio
            result = self.model.transcribe(full_audio)
            transcription = result['text'].strip()
            
            if transcription:  # Only publish if we have a transcription
                # Publish the transcription
                trans_msg = String()
                trans_msg.data = transcription
                self.transcription_pub.publish(trans_msg)
                
                self.get_logger().info(f'Heard: "{transcription}"')
                
                # Convert to robot command
                command = self.parse_command(transcription)
                if command:
                    cmd_msg = String()
                    cmd_msg.data = command
                    self.command_pub.publish(cmd_msg)
                    self.get_logger().info(f'Sending command: {command}')
                    
        except Exception as e:
            self.get_logger().error(f'Whisper transcription error: {e}')

    def parse_command(self, transcription):
        """Parse natural language command into robot action"""
        transcription_lower = transcription.lower()
        
        # Command mapping - in a real system, this would be more sophisticated
        if 'move forward' in transcription_lower or 'go forward' in transcription_lower:
            return 'MOVE_FORWARD'
        elif 'move backward' in transcription_lower or 'go back' in transcription_lower:
            return 'MOVE_BACKWARD'
        elif 'turn left' in transcription_lower:
            return 'TURN_LEFT'
        elif 'turn right' in transcription_lower:
            return 'TURN_RIGHT'
        elif 'stop' in transcription_lower:
            return 'STOP'
        elif 'pick up' in transcription_lower or 'grasp' in transcription_lower:
            return 'PICK_UP_OBJECT'
        elif 'put down' in transcription_lower or 'release' in transcription_lower:
            return 'PUT_DOWN_OBJECT'
        elif 'clean the room' in transcription_lower:
            return 'CLEAN_ROOM_SEQUENCE'
        elif 'wave hello' in transcription_lower:
            return 'WAVE_HELLO_GESTURE'
        else:
            # For a more advanced system, you could use an LLM to parse complex commands
            return f'UNKNOWN_COMMAND: {transcription}'

def main(args=None):
    rclpy.init(args=args)
    node = VoiceToActionNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()