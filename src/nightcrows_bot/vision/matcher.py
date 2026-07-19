from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from nightcrows_bot.core.models import MatchResult, ScreenPoint


class TemplateMatcher:
    def find(
        self,
        frame: np.ndarray,
        template_path: Path,
        confidence: float = 0.88,
    ) -> MatchResult:
        template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
        if template is None:
            raise FileNotFoundError(f"Modelo visual não encontrado: {template_path}")

        frame_height, frame_width = frame.shape[:2]
        template_height, template_width = template.shape[:2]
        if template_width > frame_width or template_height > frame_height:
            return MatchResult(found=False, confidence=0.0)

        scores = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        _, best_score, _, best_location = cv2.minMaxLoc(scores)
        if best_score < confidence:
            return MatchResult(found=False, confidence=float(best_score))

        center = ScreenPoint(
            x=best_location[0] + template_width // 2,
            y=best_location[1] + template_height // 2,
        )
        return MatchResult(found=True, confidence=float(best_score), center=center)

