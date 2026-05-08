#!/usr/bin/env python3
"""
Generate test tracks and export them as PolyTrack1 codes
Run this to create actual PolyTrack1 export strings
"""

from core.generator import TrackGenerator
from core.encoder import export_polytrack
from core.decoder import import_polytrack
from core.analyzer import TrackAnalyzer
from utils.visualizer import visualize_track_2d

def generate_all_tests():
    print("\n🎮 POLYTRACK EXPORT CODE GENERATION TEST 🎮\n")
    
    tracks = {
        "SIMPLE_CIRCUIT": (TrackGenerator(seed=123), lambda g: g.generate_simple_circuit(length=8)),
        "MEDIUM_RALLY": (TrackGenerator(seed=456), lambda g: g.generate_with_obstacles(length=10, difficulty="medium")),
        "HARD_RALLY": (TrackGenerator(seed=789), lambda g: g.generate_with_obstacles(length=12, difficulty="hard")),
        "CUSTOM_15SEG": (TrackGenerator(seed=999), lambda g: g.generate_simple_circuit(length=15)),
    }
    
    codes = {}
    
    for name, (gen, func) in tracks.items():
        print(f"\n{'='*70}")
        print(f"GENERATING: {name}")
        print(f"{'='*70}")
        
        blocks = func(gen)
        export_code = export_polytrack(blocks)
        
        # Verify
        decoded, error = import_polytrack(export_code)
        if not error:
            analyzer = TrackAnalyzer(decoded)
            print(f"✓ Blocks: {len(decoded)}")
            print(f"✓ Difficulty: {analyzer.get_difficulty()}")
            print(f"✓ Length: {analyzer.estimate_length()} units")
            print(f"\n📤 EXPORT CODE:\n{export_code}")
            print(f"\n🗺️ VISUALIZATION:\n{visualize_track_2d(decoded, plane='xy')}")
        
        codes[name] = export_code
    
    # Save all codes
    with open("generated_tracks.txt", "w") as f:
        for name, code in codes.items():
            f.write(f"# {name}\n{code}\n\n")
    
    print(f"\n{'='*70}")
    print("✅ ALL CODES GENERATED & SAVED TO: generated_tracks.txt")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    generate_all_tests()