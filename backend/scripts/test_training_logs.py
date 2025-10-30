"""
Quick test to trigger training and see the logging output.
Run this to test if training logs appear properly.
"""

import requests
import time

# Start training
print("=" * 80)
print("🚀 TRIGGERING MODEL TRAINING")
print("=" * 80)
print()
print("Sending POST request to /api/analytics/models/train?force=true")
print("Check the backend terminal for detailed progress logs!")
print()

try:
    response = requests.post(
        "http://localhost:8000/api/analytics/models/train?force=true",
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Training started successfully!")
        print(f"Response: {data}")
        print()
        print("=" * 80)
        print("📊 Training is now running in the background.")
        print("👀 WATCH THE BACKEND TERMINAL for detailed progress!")
        print("=" * 80)
        print()
        print("You should see:")
        print("  🚀 Model names being trained")
        print("  📊 Data loading progress")
        print("  🤖 Training status")
        print("  ✓ Completion messages")
        print("  📈 Progress percentages")
        print()
        
        # Poll status
        print("Checking training status...")
        for i in range(10):
            time.sleep(2)
            try:
                status_resp = requests.get(
                    "http://localhost:8000/api/analytics/models/training-status",
                    timeout=5
                )
                status = status_resp.json()
                current = status.get('current_model', 'None')
                progress = status.get('progress', 0)
                state = status.get('status', 'unknown')
                
                print(f"  [{i+1}/10] Status: {state} | Progress: {progress}% | Current: {current}")
                
                if state == 'completed':
                    print()
                    print("🎉 Training completed!")
                    break
                elif state == 'failed':
                    print()
                    print(f"❌ Training failed: {status.get('error', 'Unknown error')}")
                    break
            except Exception as e:
                print(f"  Error checking status: {e}")
                
    else:
        print(f"❌ Failed to start training: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("✅ Request sent! Training is running in background.")
    print("👀 Check the backend terminal for detailed logs!")
except Exception as e:
    print(f"❌ Error: {e}")
