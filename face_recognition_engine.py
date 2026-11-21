# face_recognition_engine.py
"""
NIRVYTH Angle-Invariant Facial Recognition & Watchlist Matching Engine
Includes DPDP Act 2023 compliant automated civilian blurring.
"""

import math
import random
import hashlib
import time
from config import FACE_RECOGNITION

class FaceRecognitionEngine:
    def __init__(self, watchlist_data=None):
        self.match_threshold = FACE_RECOGNITION["match_threshold"]
        self.critical_threshold = FACE_RECOGNITION["critical_threshold"]
        self.dpdp_blurring = FACE_RECOGNITION["dpdp_privacy_masking"]
        
        # Load or populate suspect watchlist
        self.watchlist = watchlist_data or [
            {
                "id": "W-2026-0891",
                "name": "Vikram Singh (Alias: Vicky)",
                "category": "WANTED_CRIMINAL",
                "threat_level": "CRITICAL",
                "offense": "Armed Robbery & Gang Violence",
                "warrant_id": "W-DL-CR-2026-4410",
                "target_embedding": [0.12, -0.08, 0.45, -0.22, 0.31, 0.05, -0.19, 0.62]
            },
            {
                "id": "M-2026-0342",
                "name": "Aarav Sharma (Age: 8)",
                "category": "MISSING_CHILD",
                "threat_level": "URGENT",
                "offense": "Amber Alert - Lost in Festival Fairgrounds",
                "warrant_id": "MPR-ND-2026-0189",
                "target_embedding": [-0.18, 0.32, -0.09, 0.51, -0.25, 0.14, 0.38, -0.05]
            }
        ]

    def cosine_similarity(self, vec_a, vec_b):
        """Computes cosine similarity between two vector embeddings."""
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def scan_frame(self, simulated_targets=None):
        """
        Processes simulated detections from aerial frame.
        Applies DPDP Act civilian blurring on non-watchlist detections.
        """
        results = []
        targets = simulated_targets or self._generate_simulated_targets()

        for t in targets:
            match_found = None
            highest_score = 0.0

            for entry in self.watchlist:
                sim = self.cosine_similarity(t["embedding"], entry["target_embedding"])
                if sim > highest_score:
                    highest_score = sim
                    if sim >= self.match_threshold:
                        match_found = entry

            is_alert = match_found is not None
            should_mask_privacy = (not is_alert) and self.dpdp_blurring

            record = {
                "track_id": t["track_id"],
                "box": t["box"],
                "match": match_found,
                "confidence": round(highest_score, 3),
                "is_alert": is_alert,
                "dpdp_blurred": should_mask_privacy,
                "timestamp": time.time(),
                "audit_hash": hashlib.sha256(f"{t['track_id']}_{highest_score}_{time.time()}".encode()).hexdigest()[:16]
            }
            results.append(record)

        return results

    def _generate_simulated_targets(self):
        """Generates realistic targets in aerial frame."""
        targets = [
            # Civilian 1 (to be blurred by DPDP privacy)
            {
                "track_id": "TRK-0192",
                "box": [120, 180, 70, 70],
                "embedding": [random.uniform(-0.1, 0.1) for _ in range(8)]
            },
            # Civilian 2 (to be blurred by DPDP privacy)
            {
                "track_id": "TRK-0193",
                "box": [340, 210, 65, 65],
                "embedding": [random.uniform(-0.1, 0.1) for _ in range(8)]
            },
            # Target matching wanted criminal Vikram Singh
            {
                "track_id": "TRK-0891-SUSPECT",
                "box": [510, 160, 85, 85],
                "embedding": [0.115, -0.075, 0.44, -0.21, 0.30, 0.048, -0.185, 0.61]
            }
        ]
        return targets

    def toggle_dpdp_masking(self):
        self.dpdp_blurring = not self.dpdp_blurring
        return self.dpdp_blurring
