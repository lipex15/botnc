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
        region: tuple[int, int, int, int] | None = None,
        bright_mask: bool = False,
    ) -> MatchResult:
        template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
        if template is None:
            raise FileNotFoundError(f"Modelo visual não encontrado: {template_path}")

        offset_x = 0
        offset_y = 0
        search_frame = frame
        if region is not None:
            x, y, width, height = region
            if x < 0 or y < 0 or width <= 0 or height <= 0:
                raise ValueError(f"Região de busca inválida: {region}")
            offset_x, offset_y = x, y
            search_frame = frame[y : y + height, x : x + width]

        frame_height, frame_width = search_frame.shape[:2]
        template_height, template_width = template.shape[:2]
        if template_width > frame_width or template_height > frame_height:
            return MatchResult(found=False, confidence=0.0)

        if bright_mask:
            search_gray = cv2.cvtColor(search_frame, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            mask = np.where(template_gray >= 145, 255, 0).astype(np.uint8)
            if cv2.countNonZero(mask) < 20:
                raise ValueError(f"Máscara visual vazia para: {template_path}")
            scores = cv2.matchTemplate(
                search_gray,
                template_gray,
                cv2.TM_CCORR_NORMED,
                mask=mask,
            )
            scores = np.nan_to_num(scores, nan=0.0, posinf=0.0, neginf=0.0)
        else:
            scores = cv2.matchTemplate(search_frame, template, cv2.TM_CCOEFF_NORMED)

        _, best_score, _, best_location = cv2.minMaxLoc(scores)
        if best_score < confidence:
            return MatchResult(found=False, confidence=float(best_score))

        center = ScreenPoint(
            x=offset_x + best_location[0] + template_width // 2,
            y=offset_y + best_location[1] + template_height // 2,
        )
        return MatchResult(found=True, confidence=float(best_score), center=center)
