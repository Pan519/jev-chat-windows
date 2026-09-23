# -*- coding: utf-8 -*-
"""回归测试：候选回复被过滤后全空时，analyze() 应抛 JevError 而不是 IndexError。

不联网：draft_candidates / ask 都在边界上换成假的。
"""
import unittest
from unittest.mock import patch

from core import engine
from core.jev_client import JevError


class EmptyCandidatesTest(unittest.TestCase):
    def test_empty_candidates_raises_jev_error(self):
        """候选全被过滤（返回空列表）→ 抛 JevError，带人话原因，而不是 IndexError。"""
        with patch.object(engine, "draft_candidates", return_value=[]), \
             patch.object(engine, "ask", return_value={"answers": {}, "usage": {}}):
            with self.assertRaises(JevError) as ctx:
                engine.analyze([("her", "在吗")], "恋人")
        self.assertIn("候选", str(ctx.exception))

    def test_normal_path_untouched(self):
        """有候选时行为不变：三段式两问、推荐按概率。"""
        def fake_ask(state, questions, *, timeout, provider, model, base_url=None):
            if "literal_question" in questions:
                return {"answers": {}, "usage": {"input_tokens": 1}}
            return {"answers": {"best_reply": {"choice": "reply_b",
                                               "probabilities": {"reply_a": 0.2, "reply_b": 0.7,
                                                                 "reply_c": 0.1}}},
                    "usage": {"input_tokens": 2}}

        def fake_chat(*a, **k):
            return ["甲", "乙", "丙"]

        with patch.object(engine, "draft_candidates", side_effect=fake_chat), \
             patch.object(engine, "ask", side_effect=fake_ask):
            r = engine.analyze([("her", "在吗")], "恋人")
        self.assertEqual(r["best_reply"], "乙")
        self.assertAlmostEqual(r["scores"][1], 0.7)


if __name__ == "__main__":
    unittest.main()
